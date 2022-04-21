#[tokio::main]
async fn main() {
    let resp = reqwest::Client::new()
        .get("https://letovo-analytics-api.herokuapp.com")
        .send()
        .await;

    match resp {
        Ok(r) => println!("Sent ping to the API! code: {}", r.status()),
        Err(e) => println!("Something went wrong!\n{}", e)
    }
}
