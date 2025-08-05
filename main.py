from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import gspread
from google.oauth2.service_account import Credentials

app = FastAPI()

# Allow CORS so your Framer website can call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your Framer website origin in production for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- GOOGLE CREDENTIALS ----------------
GOOGLE_CREDENTIALS = {
    "type": "service_account",
    "project_id": "chrome-era-466616-p6",
    "private_key_id": "38b6747defee0879797ff6d9c0592b1b44381c28",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCa5KyQ2wbJQjJe\ngZRNwYX4RLg97/0rQR/ARFL8a3cMsK6sDCwTvt/6uFsqKx4iJV3MW6679Zo08im6\nVu4Ftqu/FouEQ6W3fnrzjw6s59LzHlsntO1UcF9OBMIdywUq4p2dv73PG6nMfzPf\nJKlm2pC5bS7lFlqA+4qyVPc5hr0qXeJBYxpf0fUFZPvu0+cUA+xYkSqxkuvMjA8Q\nu37JL0Kwxy7G6iBj+Kxuqi/gTKK/hnSSRr03yeIWC6LZdQGdpRUnBhZjychZ/uJG\nXBfQ+81AFzlWTa9o6nTSkUEaA3TOp7YpXvcZLQFXfda/rq9ksI1QYJ7+Y0JqY29T\n/jEAW5VLAgMBAAECggEADIwMyCJcU/er/NvVfgPFkzoXcqAuJRxxZf6JRy+tXraX\not6ZjQy5OAx9b6Nug9v8oFrZtkzlR15Jr9ghQw7SrfgCW54Sa0eWzh2YiSKxg+Ao\nCJKVzXFAE+6h8UF9rN7bX08lup35czqBCS8yScXXhpQoAe0XOu6/A9/xTUemd/f8\nQ0p1ZNFN+VTX5O8+5VYFs9DybcSn7C/F0o9aIRj73zPs+N7l+v6EoyXkvpFfNLHu\nvGPWjUcNMWg+07L++cd7Ih/OxJzR8mamhjBxAeYbGelSqJ/rIFunTNd4oawvpUGb\ndOvGxVL0T8TZAqCsD6GudcBJS/Z4AHN3dQl/8TDkgQKBgQDOua+XXhZg3WX7D1ao\n1Aa64VCh91PGr9D7XiI6YRzTPp3JardHUy0/+FJ02kB3o7bKAeJi/sUHhOGQhVAJ\n4b8n6ELfUm9t8LgtzW08TfFAUUET9hm2WLvghwTVDDy6xrFQAe3mG1rjXtfHVvDE\nMkiE4Ek5xRh65e60T/oKNHEExQKBgQC/0DYaHGn38doQcyDH+2SC7g8CE7adbupa\nadLUgp4T2qOjs5Uy3BzDQiQefh0/9N7HCbWvqBVSrNUJHIFFMt5IcSg+uXRsgMeW\nEkoro9/zjFPramrhcML2884z6DNzmKULGucDNHC+8H3TLSyfQwbBZ9GxersUfjGI\ndHZBSQVyzwKBgHUREE/e1ztphUvkhsW6tEj2OYxPHGEixWzkBOwcfI9gIUijp0C7\n6J8WR9OmmOVnj6bb5FD9R6SXaolGBWpjLbYywFPpQfL3Y8WEVLzWwq0SlpDwR+VM\nYLCopWLkuCtpQ5Y0UX2CtjiWSAm5wUTJ2Olufek6JT/LoB76P3Wx9uKlAoGALH79\nffMndfgp0PUUHrAnsePNoXq3OzA2t0CjQt8GEq7+lQQc0U6UcYtPW69/041XfK64\n8gW45JPpW5K8PjQ9smplnp9g7aa2Jg8aG6OJWTMtaIgoQSHqaGVIaWwtO1ymtLvJ\n6Ulp+jFJzwpEtrFSyNzvnQ9OhMN9dB0oLZ7l36sCgYAB89R1eSnrmpXzbEWx1EnJ\nmBpnOXe1VToQGFl2Ss27oIO/scYADM2ZD/PeQyb+x6b83mSDR9rMzhseDGQpU/he\nf9tLgX4pPbTPP4mJ9tYtgDulU1YhqyScrUxMImUZ97d6bKJCyAp8O2GpLzeeD2QP\nvrKDCAsYJ1qacXYE+IY8tA==\n-----END PRIVATE KEY-----\n",
    "client_email": "test-158@chrome-era-466616-p6.iam.gserviceaccount.com",
    "client_id": "100044211882308239252",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test-158%40chrome-era-466616-p6.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}
# ---------------- END GOOGLE CREDENTIALS ----------------

SHEET_NAME = "journalix_test"  # Change this if needed

def connect_to_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(GOOGLE_CREDENTIALS, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).sheet1

@app.post("/write")
async def write_to_sheet(request: Request):
    data = await request.json()
    text = data.get("text")
    if not text:
        return {"error": "No text provided"}
    
    sheet = connect_to_sheet()
    sheet.append_row([text])
    return {"message": f"✅ Added text to sheet: {text}"}
