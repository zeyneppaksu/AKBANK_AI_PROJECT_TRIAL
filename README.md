# AKBANK_AI_PROJECT_TRIAL

This project is a demo system that converts **natural-language questions into PostgreSQL SQL**
and executes them on a **mock bank database**.

- Backend: **FastAPI**
- Database: **PostgreSQL (Docker)**
- LLM modes:
  - `mock` – no model, deterministic SQL
  - `hf` – Hugging Face Transformers (local model, GPU supported)
- API endpoint: `POST /ask`

---

## Prerequisites

- Python **3.12+**
- Docker Desktop
- (Optional) NVIDIA GPU + drivers for CUDA acceleration

---

## 1) Clone the Repository

```bash
git clone <YOUR_REPO_URL>
cd AKBANK_AI_PROJECT_TRIAL
```

---

## 2) Start the Database (Docker)

From the `backend/` directory:

```powershell
cd backend
docker compose up -d
docker ps
```

Check the `PORTS` column:

- `0.0.0.0:5432->5432/tcp` → DB port is **5432**
- `0.0.0.0:5433->5432/tcp` → DB port is **5433**

To stop the database:

```powershell
docker compose down
```

---

## 3) Create and Activate Virtual Environment

From `backend/`:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4) Install PyTorch

### GPU (recommended if you have NVIDIA GPU)

```powershell
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

Verify GPU support:

```powershell
python -c "import torch; print(torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
```

### CPU-only

```powershell
pip install torch
```

---

## 5) Set Environment Variables

Set these **in the same terminal** where you run the backend.

### Database URL

If port is **5432**:

```powershell
$env:DB_URL="postgresql://postgres:postgres@localhost:5432/mockbank"
```

If port is **5433**:

```powershell
$env:DB_URL="postgresql://postgres:postgres@localhost:5433/mockbank"
```

---

### LLM Mode

#### Hugging Face (real model)

```powershell
$env:LLM_MODE="hf"
$env:HF_MODEL="Qwen/Qwen2.5-3B-Instruct"
```

#### Mock mode

```powershell
$env:LLM_MODE="mock"
```

---

## 6) Run the Backend

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

