## 🧠 Research Papers Processing Pipeline

This project is a **containerized data pipeline** for processing research papers. It uses **Apache Airflow** for orchestration and **MinIO** as a data lake to store raw and translated PDF files.

## 🛠 Setup Instructions

### 1. ✅ Prerequisites

* Docker
* Docker Compose
* Python 3.10+ (for development and custom scripts)

### 2. 🔧 Clone the Repo

```bash
git clone https://github.com/your-org/research-papers-pipeline.git
cd research-papers-pipeline
```

### 3. 🌍 Create Environment File

Create the environment file with necessary credentials:

```bash
echo "AIRFLOW_UID=$(id -u)" >> env/main.env
```

Fill in `env/main.env` with the following variables:

```env
# Airflow
AIRFLOW_USER_USERNAME=admin
AIRFLOW_USER_PASSWORD=admin
AIRFLOW_USER_EMAIL=admin@example.com

# Postgres
POSTGRES_DB_USER=airflow
POSTGRES_DB_PASSWORD=airflow
POSTGRES_DB_NAME=airflow

# MinIO
MINIO_ACCESS_KEY=admin123
MINIO_SECRET_KEY=admin123
```

---

### 4. 🧱 Build Custom Airflow Image

```bash
docker build -f docker/airflow/Dockerfile -t custom_airflow:1.0 .
```

---

### 5. 🚀 Launch the Stack

```bash
docker-compose up -d
```

---

### 6. 🖥 Access Services

| Service        | URL                                            |
| -------------- | ---------------------------------------------- |
| Airflow Web UI | [http://localhost:8080](http://localhost:8080) |
| MinIO Console  | [http://localhost:9001](http://localhost:9001) |
| MinIO Buckets  | `raw/`, `translated/`                          |

Login credentials for MinIO:

* **Access Key:** `admin123`
* **Secret Key:** `admin123`

---

## 📂 Directory Structure

```text
Volumes/
├── airflow/
│   ├── dags/          # Place your DAGs here
│   ├── logs/          # Airflow logs
│   └── plugins/       # Custom Airflow plugins
.env/
├── main.env           # Environment variables
docker/
├── airflow/
│   └── Dockerfile     # Custom Airflow image setup
.storage/
├── minio/             # Local MinIO data volume
```

---

## 📌 Notes

* MinIO buckets `raw` and `translated` are created automatically at startup.
* The custom image `custom_airflow:1.0` must be built before starting the services.
* Airflow example DAGs are disabled by default.
* Airflow user is created using `AIRFLOW_USER_USERNAME`, `PASSWORD`, and `EMAIL` from the `.env` file.

---

## 🧪 Development Tips

* Use `airflow dags list` or the UI to verify your DAGs are loaded.
* Add custom DAGs in `Volumes/airflow/dags/`.
* Use `minio-py`, `boto3`, or any S3-compatible library to interact with MinIO from Python.

---
Here's a **README** for your project that includes an overview of the Airflow DAGs, the Docker Compose setup, and how to use it effectively:

---

# 📘 Airflow + MinIO: ArXiv Scraper & Translator Pipeline

This project sets up an ETL pipeline using **Apache Airflow** and **MinIO** (S3-compatible object storage) to:

1. Scrape scientific papers from **arXiv.org**
2. Store the papers in **MinIO**
3. Translate PDF content into **Ukrainian** using the **OpenAI API**
4. Save translated text back to MinIO

---

## 📂 DAGs Overview

### 🧪 `arxiv_scraping_and_translation`

* **Task**: `scrape_arxiv_papers`
* **Function**: Uses `ArxivScrapingManager` to scrape papers in batches and stores them in the `raw` bucket in MinIO.
* **Execution**: Trigger manually via the Airflow UI.

```python
def get_papers_from_arxiv():
    manager = ArxivScrapingManager(minio, BUCKET_RAW_NAME)
    asyncio.run(manager.run_arxiv_papers(batch_size=5, delay=3))
```

### 🌐 `arxiv_translation_pdf_file`

* **Task**: `translate_pdf_file`
* **Function**: Reads a specific PDF from the `raw` bucket, translates it to Ukrainian using OpenAI, and stores it as a `.txt` in the `translated` bucket.
* **Input**: Requires a `file_name` to be passed via `dag_run.conf`.

```json
{
  "file_name": "example_paper.pdf"
}
```

```python
translator = OpenAITranslater(minio, BUCKET_RAW_NAME, file_name, language="ukrainian")
translated_text = translator.translate_pdf_file().encode('utf-8')
```

---

## 🧪 Testing

To manually trigger translation with a specific file:

1. Go to Airflow UI → DAGs → `arxiv_translation_pdf_file`
2. Click "Trigger DAG"
3. Enter config JSON:

```json
{
  "file_name": "2025-01-01/my_paper.pdf"
}
```

---
