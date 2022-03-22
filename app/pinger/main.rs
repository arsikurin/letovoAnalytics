#[tokio::main]
async fn main() {
    let resp = reqwest::Client::new()
        .get("https://letovo-analytics-api.herokuapp.com")
        .send()
        .await;

    match resp {
        Ok(..) => println!("Sent ping to API!"),
        Err(e) => println!("Something went wrong!\n{}", e)
    }
}
