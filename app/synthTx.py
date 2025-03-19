import generate_tx.py
from fastapi import FastAPI, File, UploadFile
import uvicorn
from enum import Enum
from google.cloud import documentai
import json
import io
from google.api_core.client_options import ClientOptions






app = FastAPI(
  title='SynthTx,
    description='Synthetic Retail Transactional data generator',
    summary='none',
    version='25.01',
)
OUTPUT = '/content/drive/MyDrive/1Colab/synthcurve/output/transactions.json'

  
@app.get("/")
async def index():
  return("Hello world!")



  

if __name__ == "__main__":
  uvicorn.run("gretail:app", host="0.0.0.0", reload=True,   port=8080)
