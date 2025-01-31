# Inbox
A rudimentary API for creating "inboxes", which you can receive messages. Even without creating an inbox, you can send messages to other inboxes.

<!-- Visit [TK](https://TK) to see the Swagger UI and try out the API. -->

## Endpoints
Besides `/login`, data is sent via a JSON body.  
Authentication is done via JWT tokens, which are passed in the `Authorization` header as `Bearer <token>`.
### `POST /login`
Takes form data with a `username` and `password` field. Returns a JWT token.
### `POST /inbox`
Takes a JSON body with a `username` and `password` field. Returns a JWT token. **The password is hashed in the database!**
### `GET /inboxes`  
Get your current inbox and its information, including the messages in it. Requires authentication.
### `POST /messages/send`
Takes a JSON body with a `to`, `name`, and `text` field. Sends a message to the inbox with the given `to` username. Requires authentication.
### `GET /messages`
Get all messages in your inbox. Requires authentication.
### `GET /help`
Returns basic information about the API.