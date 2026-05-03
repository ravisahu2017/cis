import os
import boto3
from botocore.exceptions import NoCredentialsError
from utils import logger

def download_from_s3(s3_key, local_path):
    """Downloads a file from S3 to a local path"""
    S3_APPAREL_BUCKET_NAME = os.getenv("APPARELS_S3_BUCKET_NAME")
    print("Downloading from S3 with key:", s3_key)
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    try:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        if not os.path.exists(local_path):
            print(f"File does not exist locally. Downloading from S3: {s3_key}")
            s3.download_file(S3_APPAREL_BUCKET_NAME, s3_key, local_path)
        return f"Downloaded {s3_key} to {local_path}"
    except NoCredentialsError:
        return "AWS credentials not available."
    except Exception as e:
        return f"Error downloading file: {e}"

def list_s3_files(prefix):
    """Lists files in a given S3 prefix"""
    S3_APPAREL_BUCKET_NAME = os.getenv("APPARELS_S3_BUCKET_NAME")
    logger.info(f"Listing S3 files with prefix: {prefix}")
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    try:
        response = s3.list_objects_v2(Bucket=S3_APPAREL_BUCKET_NAME, Prefix=prefix)

        if "Contents" in response:
            return [obj["Key"] for obj in response["Contents"]]
        else:
            return []
    except NoCredentialsError:
        return "AWS credentials not available."
    except Exception as e:
        return f"Error listing files: {e}"


def upload_to_s3(file_path, s3_key, content_type="image/png"):
    """Uploads a file to S3 and returns the public URL"""
    BUCKET_BASE_URL = os.getenv("BUCKET_BASE_URL")
    S3_APPAREL_BUCKET_NAME = os.getenv("APPARELS_S3_BUCKET_NAME")

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION", "ap-south-1")
    )

    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return "File not found."

    logger.info(
        f"Uploading {file_path} to S3 with key: {s3_key}, bucket: {S3_APPAREL_BUCKET_NAME}"
    )

    try:
        s3.upload_file(
            file_path,
            S3_APPAREL_BUCKET_NAME,
            s3_key,
            ExtraArgs={"ContentType": content_type},
        )
        return f"{BUCKET_BASE_URL}{s3_key}"
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return "File not found."
    except NoCredentialsError:
        logger.error("AWS credentials not available.")
        return "AWS credentials not available."


def upload_file_object(file_object, s3_key, content_type="image/png"):
    """Uploads a file object to S3 and returns the public URL"""
    BUCKET_BASE_URL = os.getenv("BUCKET_BASE_URL")
    S3_APPAREL_BUCKET_NAME = os.getenv("APPARELS_S3_BUCKET_NAME")

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION", "ap-south-1")
    )

    logger.info(
        f"Uploading file object to S3 with key: {s3_key}, bucket: {S3_APPAREL_BUCKET_NAME}"
    )

    try:
        s3.upload_fileobj(
            file_object,
            S3_APPAREL_BUCKET_NAME,
            s3_key,
            ExtraArgs={"ContentType": content_type},
        )
        return f"{BUCKET_BASE_URL}{s3_key}"
    except Exception as e:
        logger.error(f"Error uploading file object: {e}")
        return f"Error uploading file object: {e}"