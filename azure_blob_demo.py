from azure.storage.blob import BlobServiceClient
import os

# 🔑 Use your connection string here
connection_string = "DefaultEndpointsProtocol=https;AccountName=securehealthrecords123;AccountKey=bLEsr/0cpV63DBt233z9O6xJ1kSYZ5s34/QqrlM6V1i8EthFGxGmFL+mPz+7xZQQGd58aP+iuKin+AStWh6PMA==;EndpointSuffix=core.windows.net"
container_name = "patient-records"

# Initialize Blob Service Client
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client(container_name)

# Function: Upload a file
def upload_file(local_file, blob_name):
    with open(local_file, "rb") as data:
        container_client.upload_blob(name=blob_name, data=data, overwrite=True)
    print(f"✅ Uploaded '{local_file}' as blob '{blob_name}'")

# Function: List all blobs
def list_blobs():
    print("\n📂 Files in container:")
    for blob in container_client.list_blobs():
        print(f"- {blob.name}")

# Function: Download a file
def download_file(blob_name, download_path):
    with open(download_path, "wb") as file:
        data = container_client.download_blob(blob_name)
        file.write(data.readall())
    print(f"✅ Downloaded blob '{blob_name}' to '{download_path}'")

# ----------------------------
# Demo usage
# ----------------------------

# 1. Upload all patient files from 'patients/' folder
folder = "patients"
for filename in os.listdir(folder):
    filepath = os.path.join(folder, filename)
    if os.path.isfile(filepath):
        upload_file(filepath, filename)

# 2. List all blobs
list_blobs()

# 3. Download one blob as example
download_file("patient1.txt", "downloaded_patient1.txt")
