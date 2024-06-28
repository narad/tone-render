
import os
import subprocess
import sys
from pathlib import Path
from google.cloud import storage
import csv

# Options
SHOULD_INDEX = True
SHOULD_UPLOAD = True
SHOULD_DELETE = False

# Set Path to tone-render scripts
TONE_RENDER_SCRIPT_PATH="/Users/narad/Desktop/projects/tone-render/scripts/"

# Authenticate with Google Cloud
creds = None
creds_path = "/Users/narad/Downloads/api-project-188936840889-870adc9fa631.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path

# Create a client to access the Google Cloud Storage
client = storage.Client(credentials=creds)

# Set up the google cloud storage client
# client = storage.Client()
bucket_name = 'amp-space-synthetic'
bucket = client.get_bucket(bucket_name)


# Define the directory to start from
start_dir = Path(sys.argv[1])

# Iterate over the subdirectories
for sub_dir in start_dir.iterdir():
    if sub_dir.is_dir():
        print(sub_dir)

        # Creates the HF index file
        if SHOULD_INDEX:
            print(" ".join(['python3', TONE_RENDER_SCRIPT_PATH + 'huggingface_preprocessor.py', '--input_dir', f'{sub_dir}']))
            subprocess.run(['python3', TONE_RENDER_SCRIPT_PATH + 'huggingface_preprocessor.py', '--input_dir', f'{sub_dir}'])


        # Extracts the device and brand from the HF data.csv file
        with open(Path(sub_dir) / 'data.csv', 'r') as csvfile:
            # create a CSV reader object
            reader = csv.reader(csvfile)
            
            # read the header row
            header = next(reader)
            # read the second row, which contains the device and brand values
            row = next(reader)
            
            # extract the values of the "device" and "brand" fields
            device = row[header.index("device")]
            brand = row[header.index("brand")]
            

        # Zip the subdirectory
        sub_dir = str(sub_dir) #.replace(" ", "\ ")
        zip_file = brand + " - " + device + " - " + Path(sub_dir).stem + ".zip"
        zip_command = f'zip -r "{zip_file}" "{sub_dir}"'
        print(zip_command)
        subprocess.run(zip_command, shell=True)

        # Upload the zip file to the google bucket
        if SHOULD_UPLOAD:
            blob = bucket.blob("data/" + Path(zip_file).name)
            blob.upload_from_filename(zip_file)

            # Set the ACL to be public-read
            blob.acl.save_predefined('publicRead')

        # Delete the local zip file
        if SHOULD_DELETE:
            os.remove(zip_file) 







                # zip_file = f'{sub_dir}.zip'.replace(" ", "\ ")
        # print(zip_file)
        # subprocess.run(['zip', '-r', zip_file, str(sub_dir).replace(" ", "\ ")])



# while not creds:
#     creds_path = input("Enter path to Google credentials JSON file: ")
# #    try:
#     creds = Credentials.from_authorized_user_file(creds_path)
#     # except:
#     #     print("Invalid credentials file, try again.")


