from fastapi import FastAPI, UploadFile, File
import uvicorn

app = FastAPI()

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    contents = await file.read()
    with open("output.txt", "wb") as f:
        f.write(contents)
    return {"message": "File saved!"}
