# Flask Backend

This is a simple Flask backend for a user authentication system. It uses MongoDB as the database and the `passlib` library for password hashing.

## Setup

1. Install the required Python packages:

```bash
pip install flask flask_pymongo passlib
Start your MongoDB server. You can do this by running mongod in your terminal.
Running the Server
To start the server, run the following command in your terminal:

The server will start on http://127.0.0.1:5000.

Endpoints
The server has the following endpoints:

POST /register: Registers a new user. The request body should contain name, email, and password fields.

POST /login: Logs in a user. The request body should contain username and password fields.

GET /logout: Logs out the current user.

Database
The server uses a MongoDB database named bank. It has a users collection, where each document represents a user and has the following fields:

_id: A unique identifier for the user.
name: The name of the user.
email: The email of the user.
password: The hashed password of the user.
Security
Passwords are hashed using the pbkdf2_sha256 algorithm from the passlib library before they are stored in the database. When a user tries to log in, the provided password is hashed and compared to the stored hashed password to verify it. ```

signup_form
