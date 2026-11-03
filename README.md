# Medical-Agentic-Chatbot

conda create -n project python=3.11 -y

conda activate project

pip install -r requirements.txt

add  .env

# Edit .env with real API keys

python ingest.py --pdf data/medical_book.pdf

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000