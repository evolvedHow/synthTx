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


@app.post(
  '/v1/generate/',
  summary='Generates synthetic transactional data.',
  description='This API uses several default parameters to generate synthetic data.  You can supply values to override the params to suit yur needs.',
)
async def generate(order_count=1000,
                customer_count=50,
                sku_count=100,
                catalog=None,
                store_ratio=0.6,
                start_date=datetime.date(2023,1,1),
                end_date=datetime.date(2023,12,31),
                curve="normal",
                format="JSON",
):

  transactions = SynthRetailOrders()
  tx = transactions.generateTx(order_count=10000)
  print(f'Got {len(tx)} orders')
  print(json.dumps(tx, indent=2))

  with open(OUTPUT, 'w') as f:
    for row in tx:
      f.write(json.dumps(row) + '\n')
return(f'Output is {tx}'
  

if __name__ == "__main__":
  uvicorn.run("gretail:app", host="0.0.0.0", reload=True,   port=8080)
