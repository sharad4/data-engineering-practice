import requests
import os
import zipfile
from pathlib import Path

download_uris = [
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q1.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q2.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q3.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q4.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2020_Q1.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2220_Q1.zip",
]

def create_dowloads_directory():
    """Create dowloads directory if it doesn't exist."""
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)
    return downloads_dir


def extract_filename_from_uri(uri):
    """Extract filename from URI."""
    return uri.split('/')[-1]

def download_file(uri, downloads_dir):
    filename = extract_filename_from_uri(uri)
    file_path = downloads_dir / filename

    try:
        print(f"Downloading {filename}...")
        response =requests.get(uri,stream=True)
        response.raise_for_status()

        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8191):
                f.write(chunk)
        print(f"✓ Downloaded {filename}")
        return file_path
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to download {filename}: {e}")
        return None
    
def extract_zip_file(zip_path):
    """Extract ZIP file and delete the original ZIP."""

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extract to the same directory as the ZIP file
            extract_dir = zip_path.parent
            zip_ref.extractall(extract_dir)

            # Get list of extracted files
            extracted_files = zip_ref.namelist()

        # Delete the ZIP file after successful extraction.
        zip_path.unlink()

        print(f"✓ Extracted and deleted {zip_path.name}")
        return extracted_files
    except zipfile.BadZipFile:
        print(f"✗ {zip_path.name} is not a valid ZIP file")
        return None
    except Exception as e:
        print(f"✗ Failed to extract {zip_path.name}: {e}")
        return None

def main():
    """Main function to orchestrate the download process."""
    print("Starting file download process...")

    # Step 1: Create downloads directory
    downloads_dir = create_dowloads_directory()
    print(f"✓ Created/verified download directory: {downloads_dir}")
    
    successful_downloads = 0
    failed_downloads = 0

    # Step 2-4: Download files one by one and extract
    for uri in download_uris:
        print(f"\nProcessing: {uri}")

        # Download the file
        zip_path = download_file(uri, downloads_dir)

        if zip_path and zip_path.exists():
            extracted_files = extract_zip_file(zip_path)

            if extracted_files:
                successful_downloads += 1
                print(f" Extracted files: {extracted_files}")
            else:
                failed_downloads += 1
        else:
            failed_downloads += 1

    # Summary
    print(f"\n{'='*50}")
    print(f"Download Summary")
    print(f"Successful: {successful_downloads}")
    print(f"Failed: {failed_downloads}")
    print(f"Total: {len(download_uris)}")
    print(f"{'='*50}")

    uri = "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip"

    download_file(uri, downloads_dir)
    pass


if __name__ == "__main__":
    main()
