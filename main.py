import json
import gspread
from google.oauth2.service_account import Credentials
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

SHEET_NAME = "journalix_test"  # Change to your sheet name

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_credentials():
    with open("credentials.json") as f:
        creds_info = json.load(f)
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
    return creds

def connect_to_sheet():
    creds = load_credentials()
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1
    return sheet

def append_text_to_sheet(sheet, text):
    sheet.append_row([text])
    print(f"✅ Added text to sheet: {text}")

@app.post("/write")
async def write_text(request: Request):
    data = await request.json()
    text = data.get("text")
    if not text:
        return {"message": "No text provided."}

    sheet = connect_to_sheet()
    append_text_to_sheet(sheet, text)
    return {"message": f"Text '{text}' added successfully!"}
