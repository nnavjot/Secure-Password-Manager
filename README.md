# Secure Password Manager

A secure password manager web application built with Python and Flask for the B207 Cybersecurity module (Idea 2).

## Features

- User registration and login
- Master passwords hashed with bcrypt (salted automatically)
- Saved passwords encrypted with Fernet before being stored
- Random password generator (using Python's `secrets` module)
- Add, view, and delete saved password entries
- CSRF protection on all forms (Flask-WTF)
- Parameterised SQL queries to prevent SQL injection
- Jinja2 auto-escaping to prevent XSS

## Requirements

- Python 3

## Setup

```bash
bash setup.sh
```

This installs Flask, Flask-WTF, bcrypt, and cryptography, then starts the app.

Then open:

```
http://127.0.0.1:5000
```

The database file (`vault.db`) and encryption key (`secret.key`) are created automatically on first run.

## How to Use

1. Register a new account
2. Log in
3. Click **Add New Password** to save a new entry — you can type your own password or click **Generate Password**
4. View saved entries on the dashboard, click **Show** to reveal a password
5. Delete entries you no longer need

## Project Files

| File | Purpose |
|---|---|
| `app.py` | Main Flask application — routes, database, security logic |
| `login.html` | Login page |
| `register.html` | Registration page |
| `dashboard.html` | Lists saved passwords |
| `add.html` | Form to add a new password entry |
| `requirements.txt` | Python dependencies |
| `setup.sh` | Installs dependencies and starts the app |

## Security Notes

- Master passwords are hashed with bcrypt, never stored as plain text
- Stored passwords are encrypted with Fernet (AES-128-CBC + HMAC-SHA256)
- All forms include CSRF tokens
- All database queries are parameterised
