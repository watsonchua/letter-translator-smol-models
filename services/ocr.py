from io import BytesIO
from jigsawstack import JigsawStack, JigsawStackError
from dotenv import load_dotenv, find_dotenv
import os
import boto3
from botocore.exceptions import ClientError
import logging



env_key_loaded = load_dotenv(find_dotenv())
if not env_key_loaded:
    raise Exception("Environment key not found")


s3_bucket_name = os.environ["S3_BUCKET_NAME"]
s3_client = boto3.client('s3', region_name='ap-southeast-1', aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"], aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])

# Initialize a boto3 client for S3
def upload_to_s3(file_data, object_name):
    """
    Uploads a file to the S3 bucket.

    :param file_data: File data to upload.
    :param object_name: S3 object name.
    :return: True if the file was uploaded successfully, False otherwise.
    """

    print(file_data)
    try:
        # if isinstance(file_data, str):
        #     file_data = file_data.encode('utf-8')  # Encode string to bytes
        # elif not isinstance(file_data, bytes):
        #     raise ValueError("file_data must be either a string or bytes")

        # s3_client.upload_fileobj(BytesIO(file_data), s3_bucket_name, object_name)


        s3_client.upload_fileobj(file_data, s3_bucket_name, object_name)


        # Construct the URL
        object_url = f"{s3_client.meta.endpoint_url}/{s3_bucket_name}/{object_name}"
        return object_url
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        return None
    except ClientError as e:
        logging.error(e)
        return None


class OCR:
    def __init__(self):
        self.client = JigsawStack(api_key=os.environ["JIGSAWSTACK_API_KEY"])
    
    # def upload_file(self, image_file, filename):
    #     print(image_file)
    #     # image_data = image_file.read()
    #     # result = self.client.store.upload(
    #     #     image_file, {"filename": filename, "overwrite": True}
    #     # )
    #     # print("Image uploaded successfully:", result)
        
    #     result = upload_to_s3(image_file, filename)
    #     print("Image uploaded successfully:", result)

        



    def parse(self, image_file, filename):

        try:
            # upload_results = self.upload_file(image_file, filename)
            uploaded_url = upload_to_s3(image_file, filename)
            # uploaded_url = upload_results["url"]
            # uploaded_url = image_file.file_path

            print(f"Image uploaded to {uploaded_url}")
            result = self.client.vision.vocr({"url": uploaded_url, "prompt" : ["Extract the list of ingredients and allergens from the image"]})        
            result_text = result['context']
            print(result_text)
        except KeyError as e:
            print(e)
            result_text = None
        except JigsawStackError as e:
            print(f"An error occurred during uploading: {e}")
            result_text = None

        
        return result_text
        
