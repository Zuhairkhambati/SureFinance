@echo off
echo Starting Backend Server...
cd backend
if exist venv\Scripts\activate (
    call venv\Scripts\activate
) else (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    call venv\Scripts\activate
    echo Installing dependencies...
    pip install -r requirements.txt
)
echo Starting FastAPI server on http://localhost:8000
uvicorn main:app --reload --port 8000



