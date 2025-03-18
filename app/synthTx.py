from fastapi import FastAPI, File, UploadFile
import uvicorn
from enum import Enum
from google.cloud import documentai
import json
import io
from google.api_core.client_options import ClientOptions

PROJECT_ID = 'vishretail-2301'
LOCATION = 'us'
PROCESSOR_ID ='5ce173ab9343f3d7'
MIME_TYPE = 'application/pdf'
PDF_PROCESSOR = 'projects/vishretail-2301/locations/us/processors/5ce173ab9343f3d7'
API_KEY = 'AIzaSyBrurVe98zATq_4iYl6sfRmn8WvDLFsYYc'

docai_client = documentai.DocumentProcessorServiceClient(
  client_options=ClientOptions(api_endpoint="us-documentai.googleapis.com"
  )
)

RESOURCE_NAME = docai_client.processor_path(PROJECT_ID, LOCATION, PROCESSOR_ID)

app = FastAPI(
  title='SynthTx,
    description='Synthetic Retail Transactional data generator',
    summary='none',
    version='25.01',
)

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

  
  return("generation wip")

@app.post(
  '/v1/parsePDF/',
  summary='Parses a PDF using the DocAI api',
  description='This API uses the DocAI API to perform multi-modal parsing of a document.',
)
async def parsePDF(pdfFile:UploadFile, chunk_size: int, chunk_overlap: int, chunk_uom:str='char'):

  if pdfFile.filename.endswith('pdf'):
    pass
  else:
    return('error')

  pdf_bytes = await pdfFile.read()

  raw_document = documentai.RawDocument(content=pdf_bytes, mime_type=MIME_TYPE)

  request = documentai.ProcessRequest(name=RESOURCE_NAME, raw_document=raw_document)
  response = docai_client.process_document(request=request)

  text = ""
  for page in response.document.pages:
    for block in page.blocks:
      for paragraph in block.paragraphs:
        for word in paragraph.words:
          text += word.symbol
          if word.break_category == documentai.DocumentProcessor.EntityBreakCategory.SPACE:
            text += ""
  return text

  return("wip")

if __name__ == "__main__":
  uvicorn.run("gretail:app", host="0.0.0.0", reload=True,   port=8080)
