import asyncio
import aiofiles
import aiohttp
import os
import zipfile
from pathlib import Path
from typing import List, Tuple

download_uris = [
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q1.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q2.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q3.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q4.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2020_Q1.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2220_Q1.zip",

]

def create_downloads_directory():
    """Create downloads directory if it doesn't exist."""
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)
    return downloads_dir

def extract_filename_from_uri(uri:str)->  str:
    """Extract filename from URI."""
    return uri.split('/')[-1]

async def download_file_async(session: aiohttp.ClientSession, uri: str, downloads_dir: Path) -> Tuple[bool, str]:
    """Download a Single file asynchronously."""
    filename = extract_filename_from_uri(uri)
    file_path = downloads_dir / filename

    try:
        print(f"Starting download: {filename}")
        async with session.get(uri) as response:
            response.raise_for_status()

            async with aiofiles.open(file_path, 'wb') as f:
                async for chunk in response.content.iter_chunked(8192):
                    await f.write(chunk)
        
        print(f"✔ Downloaded {filename}")
        return True, str(file_path)
    except Exception as e:
        print(f"❌ Failed to download {filename}: {e}")
        return False, ""
    
def extract_zip_file(zip_path: str) -> Tuple[bool, List[str]]:
    """Extract ZIP file and delete the original ZIP."""
    zip_path_obj = Path(zip_path)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            extract_dir = zip_path_obj.parent
            zip_ref.extractall(extract_dir)
            extracted_files = zip_ref.namelist()

        # Delete the ZIP file after susccessful extraction
        zip_path_obj.unlink()

        print(f"✔ Extracted and deleted {zip_path_obj.name}")
        return True, extracted_files
    except zipfile.BadZipFile:
        print(f"❌ {zip_path_obj.name} is not a valid ZIP file")
        return False, []
    except Exception as e:
        print(f"❌ Failed to extract {zip_path_obj.name}: {e}")
        return False, []

async def main_async():
    """Main async function to orchestrate the download process."""
    print("Starting async file download process....")

    # Create downloads directory
    downloads_dir = create_downloads_directory()
    print(f"✔ Create / verified downloads directory: {downloads_dir}")


    successful_downloads = 0
    failed_downloads = 0

    # Configure session with timeout and connection limits
    timeout = aiohttp.ClientTimeout(total=300)
    connector = aiohttp.TCPConnector(limit=10)

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        # Download all files concurrently
        download_tasks = [
            download_file_async(session, uri, downloads_dir)
            for uri in download_uris
        ]

        print(f"\nDownloading {len(download_tasks)} file concurrently...")
        download_results = await asyncio.gather(*download_tasks)

    # Process the downloaded files (extract ZIPs)
    print('\nExtracting ZIP files...')
    for success, file_path in download_results:
        if success and file_path:
            extract_success, extracted_files = extract_zip_file(file_path)

            if extract_success:
                successful_downloads += 1
                print(f" Extraced files: {extracted_files}")
            else:
                failed_downloads += 1
        else:
            failed_downloads += 1

    # Summary
    print(f"\n{'='*50}")
    print(f"Async Download Summary:")
    print(f"Successful: {successful_downloads}")
    print(f"Failed: {failed_downloads}")
    print(f"Total: {len(download_uris)}")
    print(f"{'='*50}")
    
def main():
    """Entry point that runs the async main function."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()