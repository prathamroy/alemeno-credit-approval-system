# Credit Approval System – Backend

This is a backend application built with Django, Django REST Framework, Celery, PostgreSQL, and Redis to automate credit approval decisions based on historical and current loan data.

---

## Features

* Register new customers and auto-calculate approved limits
* Check loan eligibility based on credit score rules
* Approve and create new loans with dynamic interest rate correction
* View loan details and all customer loans
* Background ingestion of Excel data using Celery workers and Redis

---

## Tech Stack

* Python 3.11
* Django 5.2
* Django REST Framework
* PostgreSQL
* Redis + Celery (for background tasks)
* Pandas + OpenPyXL (for Excel file processing)
* Docker + Docker Compose

---

## Setup Instructions

### 1. Clone the repo and navigate into it:

```bash
git clone <repo-url>
cd credit_approval_system
```

### 2. Create and activate virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies:

```bash
pip install -r requirements.txt
```

### 4. Run PostgreSQL and Redis with Docker:

```bash
docker compose up -d
```

### 5. Apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Start the Django server:

```bash
python manage.py runserver 8001
```

---

## Background Data Ingestion


### 1. Run Celery worker in another terminal:

```bash
celery -A backend worker --loglevel=info
```

### 2. Trigger data loading:

```bash
python manage.py shell

# Inside shell
from credit_app.tasks import load_data
load_data.delay()
```

---

## API Endpoints

### `POST /register`

Register a new customer.

### `POST /check-eligibility`

Check if a customer is eligible for a loan.

### `POST /create-loan`

Create and approve a loan (if eligible).

### `GET /view-loan/<loan_id>`

View loan and customer details.

### `GET /view-loans/<customer_id>`

View all loans for a given customer.

---

## Folder Structure

```
credit_approval_system/
├── backend/              # Django project
├── credit_app/           # Main app with models, views, tasks
├── customer_data.xlsx    # Initial customer data
├── loan_data.xlsx        # Initial loan data
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Author

Pratham Roy

Built as part of a backend engineering internship assignment.
