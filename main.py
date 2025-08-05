from fastapi import FastAPI, Request
from pydantic import BaseModel
import gspread
from google.oauth2.service_account import Credentials

app = FastAPI()

# ---------------- GOOGLE CREDENTIALS ----------------
GOOGLE_CREDENTIALS = {
    "type": "service_account",
    "project_id": "chrome-era-466616-p6",
    "private_key_id": "38b6747defee0879797ff6d9c0592b1b44381c28",
    "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCa5KyQ2wbJQjJe
...
-----END PRIVATE KEY-----\n""",
    "client_email": "test-158@chrome-era-466616-p6.iam.gserviceaccount.com",
    "client_id": "100044211882308239252",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test-158%40chrome-era-466616-p6.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}
# ---------------- END GOOGLE CREDENTIALS ----------------

SHEET_NAME = "journalix_test"

def connect_to_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(GOOGLE_CREDENTIALS, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).sheet1

sheet = connect_to_sheet()

class SheetData(BaseModel):
    text: str

@app.post("/append")
async def append_text(data: SheetData):
    sheet.append_row([data.text])
    return {"message": f"✅ Added text to sheet: {data.text}"}

@app.get("/")
async def root():
    return {"status": "API is running"}
