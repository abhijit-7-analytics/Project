# SalesDB — Full Stack Sales Dashboard

A Flask + plain HTML/CSS/JS dashboard for the PostgreSQL sales analytics project.

---

## Project Structure

```
├── app.py           ← Flask backend (REST API)
├── index.html       ← Frontend dashboard (open in browser)
├── requirements.txt ← Python dependencies
└── README.md
```

---

## 1. Database Setup

Make sure PostgreSQL is running and your `sales_db` database exists.

```bash
psql -U postgres -c "CREATE DATABASE sales_db;"
```

Or call the setup endpoint after starting the API (see below).

---

## 2. Backend — Flask API

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure credentials (optional — defaults match the original script)

```bash
export DB_NAME=sales_db
export DB_USER=postgres
export DB_PASSWORD=Abhi@1234
export DB_HOST=localhost
```

### Run the server

```bash
python app.py
```

API runs at **http://localhost:5000**

### First-time schema setup via API (alternative to running analytics script) 

```bash
curl -X POST http://localhost:5000/api/setup
```
### OR

```bash
Invoke-WebRequest -Uri http://localhost:5000/api/setup -Method POST
```

---

## 3. Frontend

Just open `index.html` in your browser — no build step required.

```bash
open index.html        # macOS
start index.html       # Windows
xdg-open index.html    # Linux
```

Make sure Flask is running first or the dashboard will show a connection error.

---

## API Endpoints

| Method | Path                              | Description               |
|--------|-----------------------------------|---------------------------|
| GET    | /api/health                       | Health check              |
| GET    | /api/analytics/kpis               | KPI summary               |
| GET    | /api/analytics/revenue-by-category| Revenue per category      |
| GET    | /api/analytics/revenue-over-time  | Daily revenue series      |
| GET    | /api/customers                    | List all customers        |
| POST   | /api/customers                    | Add a customer            |
| DELETE | /api/customers/:id                | Delete a customer         |
| GET    | /api/products                     | List all products         |
| POST   | /api/products                     | Add a product             |
| DELETE | /api/products/:id                 | Delete a product          |
| GET    | /api/sales                        | List all sales (joined)   |
| POST   | /api/sales                        | Add a sale                |
| DELETE | /api/sales/:id                    | Delete a sale             |
| POST   | /api/setup                        | Create tables (DDL)       |
