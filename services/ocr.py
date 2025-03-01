from io import BytesIO
from typing import List
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
    def __init__(self, prompts: List[str]):
        self.client = JigsawStack(api_key=os.environ["JIGSAWSTACK_API_KEY"])
        self.prompts = prompts
    

    def parse(self, image_file, filename):

        try:
            uploaded_url = upload_to_s3(image_file, filename)

            print(f"Image uploaded to {uploaded_url}")
            print(self.prompts)
            result = self.client.vision.vocr({"url": uploaded_url, "prompts" : self.prompts})      
            result_context = result["context"]  
            # print(result_context)
        except KeyError as e:
            print(e)
            result_context = None
        except JigsawStackError as e:
            print(f"An error occurred during uploading: {e}")
            result_context = None

        return result_context
        
