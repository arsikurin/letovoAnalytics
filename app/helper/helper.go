package main

import (
	"cloud.google.com/go/firestore"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/joho/godotenv"
	"google.golang.org/api/option"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"
	"sync"
)

type TokenResponse struct {
	Status  string `json:"status"`
	Code    int    `json:"code"`
	Message string `json:"message"`
	Data    struct {
		ExpiresAt string `json:"expires_at"`
		Token     string `json:"token"`
		TokenType string `json:"token_type"`
	} `json:"data"`
}

func receiveToken(doc *firestore.DocumentSnapshot) (*TokenResponse, error) {
	var err error
	login, err := doc.DataAt("data.analytics_login")
	if err != nil {
		return nil, err
	}
	pass, err := doc.DataAt("data.analytics_password")
	if err != nil {
		return nil, err
	}
	data := url.Values{
		"login":    {login.(string)},
		"password": {pass.(string)},
	}

	resp, err := http.PostForm("https://s-api.letovo.ru/api/login", data)
	if err != nil {
		return nil, err
	}
	if resp.StatusCode != 200 {
		return nil, errors.New("unable to obtain token (" + login.(string) + "): " + resp.Status)
	}

	res := new(TokenResponse)
	err = json.NewDecoder(resp.Body).Decode(res)
	if err != nil {
		return nil, err
	}

	defer func(Body io.ReadCloser) {
		err := Body.Close()
		if err != nil {
			log.Println(err)
		}
	}(resp.Body)
	return res, nil
}

func main() {
	var (
		err error
		wg  sync.WaitGroup
	)
	err = godotenv.Load(".env.development.local")
	if err != nil {
		log.Println(err)
	}
	opt := option.WithCredentialsJSON([]byte(os.Getenv("GOOGLE_FS_KEY")))
	ctx := context.Background()
	client, err := firestore.NewClient(ctx, "letovo-analytics", opt)
	defer func(client *firestore.Client) {
		err := client.Close()
		if err != nil {
			fmt.Println(err)
		}
	}(client)
	if err != nil {
		fmt.Println(err)
	}

	q := client.Collection("users").Where("data.student_id", ">", 1)
	docs, err := q.Documents(ctx).GetAll()
	if err != nil {
		return
	}

	for _, doc := range docs {
		wg.Add(1)
		go func(doc *firestore.DocumentSnapshot, wg *sync.WaitGroup) {
			defer wg.Done()
			token, err := receiveToken(doc)
			if err != nil {
				fmt.Println(err)
				return
			}
			_, err = client.Collection("users").Doc(doc.Ref.ID).Update(ctx, []firestore.Update{
				{Path: "data.token", Value: token.Data.TokenType + " " + token.Data.Token},
			})
			if err != nil {
				fmt.Println(err)
			}
		}(doc, &wg)
	}
	wg.Wait()
}
