import json
import gspread
from google.oauth2.service_account import Credentials
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Add Firebase Admin SDK imports
import firebase_admin
from firebase_admin import credentials as admin_credentials, firestore

SHEET_NAME = "journalix_test"  # Change to your sheet name

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase Admin once
if not firebase_admin._apps:
    # Use your Firebase Admin SDK private key file or environment variable
    # For local dev, you can put the service account JSON file path here
    admin_cred = admin_credentials.Certificate("C:\Users\Lenny\Documents\framer\FireBasesdk.json")
    firebase_admin.initialize_app(admin_cred)

db = firestore.client()

def load_credentials_from_firestore(user_id: str):
    # Fetch user doc from Firestore
    doc_ref = db.collection("users").document(user_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise Exception(f"No Firestore document found for user {user_id}")

    user_data = doc.to_dict()
    credentials_json_string = user_data.get("credentials_json")

    if not credentials_json_string:
        raise Exception(f"No credentials JSON saved for user {user_id}")

    # Parse the JSON string to dict
    creds_info = json.loads(credentials_json_string)
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
    return creds

def connect_to_sheet(user_id: str):
    creds = load_credentials_from_firestore(user_id)
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
    user_id = data.get("user_id")  # The frontend should send the user ID here

    if not text:
        return {"message": "No text provided."}
    if not user_id:
        return {"message": "No user ID provided."}

    try:
        sheet = connect_to_sheet(user_id)
        append_text_to_sheet(sheet, text)
        return {"message": f"Text '{text}' added successfully!"}
    except Exception as e:
        return {"error": str(e)}
