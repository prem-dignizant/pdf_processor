from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from service import get_s3_data , pdf_to_image
import os, shutil
from pdf_process_model import get_segment , process_segmentation_masks , process_masks_to_xfdf

# Initialize FastAPI app
app = FastAPI()

folder_path = "input_files"

# Input schema
class PDFRequest(BaseModel):
    s3_url: str


@app.post("/process-pdf")
async def process_pdf(request: PDFRequest):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

    # Recreate the folder
    os.makedirs(folder_path, exist_ok=True)
    s3_url = request.s3_url
    
    try:
        file_name = get_s3_data(s3_url)
        all_images = pdf_to_image(file_name)
        image = all_images[0]
        sam_result = get_segment(image)
        annotations = process_segmentation_masks(sam_result)
        xfdf_content = process_masks_to_xfdf(sam_result, 'output.xfdf')
        return {"file_name": 'data'}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to download PDF: {e}")


