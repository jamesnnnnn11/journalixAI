import json
import gspread
from google.oauth2.service_account import Credentials
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Firebase Admin imports
import firebase_admin
from firebase_admin import credentials as admin_credentials, firestore

# The name of the Google Sheet (you can also fetch this from Firestore per user if you want)
SHEET_NAME = "journalix"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://welcome-level-075907.framer.app/getstarted"],  # Update this in production to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase Admin SDK once (only if not initialized already)
if not firebase_admin._apps:
    # Use your Firebase Admin SDK JSON file path
    admin_cred = admin_credentials.Certificate(r"C:\Users\Lenny\Documents\framer\FireBasesdk.json")
    firebase_admin.initialize_app(admin_cred)

db = firestore.client()

def load_credentials_from_firestore(user_id: str):
    """Fetch the user's Google service account JSON stored as a string in Firestore, parse it, and create Credentials."""
    doc_ref = db.collection("users").document(user_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise Exception(f"No Firestore document found for user {user_id}")

    user_data = doc.to_dict()
    credentials_json_string = user_data.get("googleCredentialsJson")  # Make sure this key matches Firestore

    if not credentials_json_string:
        raise Exception(f"No credentials JSON saved for user {user_id}")

    creds_info = json.loads(credentials_json_string)
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
    return creds

def connect_to_sheet(user_id: str):
    """Authorize with Google Sheets API using the user's credentials and open the specified sheet."""
    creds = load_credentials_from_firestore(user_id)
    client = gspread.authorize(creds)

    # Option 1: Use a global sheet name
    sheet = client.open(SHEET_NAME).sheet1

    # Option 2: If you want to store and use the googleSheetId per user, uncomment and use this instead:
    # user_data = db.collection("users").document(user_id).get().to_dict()
    # sheet_id = user_data.get("googleSheetId")
    # sheet = client.open_by_key(sheet_id).sheet1

    return sheet

def append_text_to_sheet(sheet, text):
    """Append the text as a new row in the Google Sheet."""
    sheet.append_row([text])
    print(f"✅ Added text to sheet: {text}")

@app.post("/write")
async def write_text(request: Request):
    data = await request.json()
    text = data.get("text")
    user_id = data.get("user_id")  # Expect frontend to send this securely after user auth

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
