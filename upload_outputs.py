import boto3
import os
import re
from pathlib import Path

def get_aws_credentials():
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    if not aws_access_key_id or not aws_secret_access_key:
        raise ValueError("AWS credentials not found in environment variables")
    
    return aws_access_key_id, aws_secret_access_key

def initialize_s3_client():
    aws_access_key_id, aws_secret_access_key = get_aws_credentials()
    
    return boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name='eu-west-1' 
    )

def upload_file_to_s3(s3_client, bucket_name, key, file_path):
     
    try:
        s3_client.upload_file(file_path, bucket_name, key)
        print(f"Uploaded {file_path} to s3://{bucket_name}/{key}")
    except Exception as e:
        print(f"Failed to upload {file_path} to s3://{bucket_name}/{key}. Error: {e}")

def upload_files():
    bucket_name = '905418005465-eu-west-1-data-files'
    source = 'RM-scraped-data'
    s3_client = initialize_s3_client()

    #Upload listings.csv (From GT-6)
    listings_csv_path = Path('rightmove_scraper/rightmove_scraper/listings.csv')
    if listings_csv_path.exists():
        extracted_date = '2024-06-07'  
        key = f"{source}/extracted_date={extracted_date}/listing.csv"
        upload_file_to_s3(s3_client, bucket_name, key, str(listings_csv_path))
    else:
        print(f"{listings_csv_path} does not exist and will be skipped.")

    #Upload JSON files from rmpipeline folder(From GT-7 and GT-8)
    rmpipeline_dir = Path('rmpipeline/rmpipeline')
    json_files = rmpipeline_dir.glob('*.json')
    for json_file in json_files:
        filename = json_file.name
        match = re.match(r'rmpipeline_(.+?)_(\d{4}-\d{2}-\d{2}).json', filename)
        if match:
            postcode, extracted_date = match.groups()
            key = f"{source}/extracted_date={extracted_date}/listing.csv"
            upload_file_to_s3(s3_client, bucket_name, key, str(json_file))
        else:
            print(f"Filename {filename} does not match the expected format and will be skipped.")

if __name__ == "__main__":
    try:
        upload_files()
    except ValueError as e:
        print(e)
