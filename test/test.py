from io import BytesIO
from services.ocr import upload_to_s3
from pathlib import Path

filepath = Path("/mnt/c/Users/watso/Pictures/Screenshots/Screenshot 2023-04-13 094335.png")
with open(filepath, "rb") as f:
    file_data =BytesIO(f.read())

url = upload_to_s3(file_data= file_data, object_name=filepath.name)
print(url)