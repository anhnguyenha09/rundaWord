file .env de luu cac gia tri nhay cam
Cài đặt python-dotenv để load .env:
pip install python-dotenv

Sau đó trong app.py thêm:
from dotenv import load_dotenv
load_dotenv()