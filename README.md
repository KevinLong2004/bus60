# Bus60.py

A simple Python backend service, containerized with Docker and Docker Compose.

---

## 📁 Project Structure

```
Bus60.py/
├── templates/
├── app.py
├── backend.py
├── requirements.txt
├── Dockerfile
├── compose.yaml
├── .dockerignore
├── .gitignore
├── LICENSE
├── README.md
└── README.Docker.md
```

---

## 🐳 Running with Docker (Recommended)

Using Docker Compose:

```bash
docker compose up --build
```

The service will be available at:

```
http://localhost:5000
```

---

## ▶️ Running Locally (Optional)

```bash
pip install -r requirements.txt
python app.py
```

---

## 🧩 Files Overview

* `app.py` – Application entry point
* `backend.py` – Core backend logic
* `templates/` – Template files (if applicable)
* `requirements.txt` – Python dependencies
* `Dockerfile` – Docker image definition
* `compose.yaml` – Docker Compose configuration

---

## 📄 License

MIT License
