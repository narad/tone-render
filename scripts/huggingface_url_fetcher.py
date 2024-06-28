import os
import subprocess
import sys
from pathlib import Path
from google.cloud import storage
import csv

creds = None
creds_path = "/Users/narad/Downloads/api-project-188936840889-870adc9fa631.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path

# Create a client to access the Google Cloud Storage
client = storage.Client(credentials=creds)

# Set up the google cloud storage client
bucket_name = 'amp-space-synthetic'
bucket = client.get_bucket(bucket_name)

# list all blobs (files) in the bucket
blobs = bucket.list_blobs()

# open a CSV file for writing
with open('file_urls.csv', mode='w') as csv_file:
    # create a CSV writer
    writer = csv.writer(csv_file)

    # write the header row
    writer.writerow(['File name', 'URL'])

    # iterate over each blob and write its filename and URL to the CSV file
    for blob in blobs:
        url = f"https://storage.googleapis.com/{bucket_name}/{blob.name}"
        writer.writerow([blob.name[5:-4], url])