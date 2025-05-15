# FindMail

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Table of Contents

1. [Project Description](#project-description)  
2. [Tech Stack](#tech-stack)  
3. [Getting Started Locally](#getting-started-locally)  
4. [Available Scripts](#available-scripts)  
5. [Project Scope](#project-scope)  
6. [Project Status](#project-status)  
7. [License](#license)  

---

## Project Description

FindMail is an MVP webmail client for the `@findmail.pl` domain.  
It enables users to register (with a one-time invitation key), log in, generate or access shared mailboxes (max 20-character, email-safe names), and perform basic email operations:  
- List messages (with automatic 60 s polling or manual refresh)  
- Preview message content (HTML/TXT) in a sandboxed `iframe` (all `<script>` tags stripped)  
- Permanently delete messages (with confirmation)  
- Centralized error handling with user-friendly messages  

---

## Tech Stack

**Frontend**  
- Bootstrap 5 (via CDN)  
- Jinja2 templating (Flask)  
- Custom CSS for lightweight overrides  
- Vanilla JavaScript for polling and UI interactions  

**Backend**  
- Python 3.x  
- Flask (Blueprints, routing, templating)  
- Flask-Login for session management and authentication  
- MariaDB (InnoDB) for persistence  
- SMTP configured via a local config file  

**CI/CD & Hosting**  
- GitHub Actions for automated pipelines  
- Self-hosted deployment  
- Public domain: `www.findmail.pl`  

---

## Getting Started Locally

### Prerequisites

- Python 3.8+  
- MariaDB server  
- Git  

### Clone & Install

```bash
git clone https://github.com/your-username/findmail.git
cd findmail
# create a virtual environment
python3 -m venv .venv
source .venv/bin/activate
# install dependencies
pip install -r requirements.txt
```

### Configuration

1. Copy the example config file and update credentials:

   ```bash
   cp config_example.yml config.yml
   ```

2. In `config.yml`, set:
   - `DATABASE_URI` (e.g. `mysql+pymysql://user:password@localhost/findmail`)
   - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USE_TLS`  
   - Any other application settings (secret key, etc.)

### Database Setup

```bash
# create the database
mysql -u root -p -e "CREATE DATABASE findmail CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
# run SQL schema/migrations if provided
# e.g., flask db upgrade
```

Ensure the `invitation_keys` table exists with columns `id` and `klucz`.

### Running the App

```bash
export FLASK_APP=app
export FLASK_ENV=development
flask run
```

Access the UI at `http://localhost:8080` (Chrome only).

---

## Available Scripts

| Command               | Description                                  |
|-----------------------|----------------------------------------------|
| `flask run`           | Start the Flask development server           |
| `pytest`              | Run the test suite (if tests are provided)   |
| `flake8`              | Run code linting (if linter config exists)   |

> Replace or extend these scripts based on your local setup.

---

## Project Scope

**Features**  
- Invitation-key management (one-time use)  
- User registration & login  
- Mailbox creation & access (shared)  
- Email listing with metadata (Date, Sender, Subject)  
- Polling every 60 s + manual refresh with loading indicator  
- Secure preview in sandboxed `iframe`  
- Message deletion with confirmation modal  
- Central UI error handler ("Coś poszło nie tak, spróbuj ponownie")

**Limitations**  
- Chrome only  
- No attachments support  
- No email address verification  
- No rate limiting or request throttling  
- No mobile app or user documentation  

---

## Project Status

**MVP** – under active development.  
Supports core functionality in Chrome; further enhancements (attachments, multi-browser support, advanced security) planned for future releases.

---

## License

This project is licensed under the MIT License.  
See [LICENSE](LICENSE) for details. 