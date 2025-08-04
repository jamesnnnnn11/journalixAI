from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# Allow CORS for all domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to Framer's domain if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/write")
async def write_text(request: Request):
    body = await request.json()
    text = body.get("text")

    if not text:
        return {"message": "No text received"}

    with open("output.txt", "a") as f:
        f.write(text + "\n")

    return {"message": "Text written to file!"}
