from bs4 import BeautifulSoup  # v4.x
import requests  # v2.x                                 import re
from packaging.version import Version
import os

BASE_URL = "https://ftp.mozilla.org/pub/fenix/releases/"
VERSION_FILE = "firefox_last_version.txt"

def get_latest_version(base_url):                           """
    Fetches the latest stable version from the given base URL.
    """
    response = requests.get(base_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    dirs = [a.text.strip('/') for a in soup.find_all('a', href=True) if a['href'].endswith('/')]

    version_pattern = re.compile(r'^\d+(\.\d+)*$')
    valid_versions = [dir_name for dir_name in dirs if version_pattern.match(dir_name)]
    valid_versions.sort(key=Version)                    
    return valid_versions[-1] if valid_versions else None

def read_last_version():
    """
    Reads the last downloaded version from a local file.
    """
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'r') as file:
            return file.read().strip()
    return None

def write_last_version(version):
    """
    Writes the latest downloaded version to a local file.
    """
    with open(VERSION_FILE, 'w') as file:
        file.write(version)

def download_latest_version(base_url, latest_version):
    """
    Downloads the APK for the latest stable version and opens it using termux-open.
    """
    download_url = (
        f"{base_url}{latest_version}/android/"
        f"fenix-{latest_version}-android-arm64-v8a/"
        f"fenix-{latest_version}.multi.android-arm64-v8a.apk"
    )

    response = requests.get(download_url, stream=True)

    if response.status_code == 200:
        file_name = f"fenix-{latest_version}.multi.android-arm64-v8a.apk"
        with open(file_name, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded: {file_name}")

        # Use termux-open to open the APK file
        os.system(f"termux-open {file_name}")
        write_last_version(latest_version)
    else:
        print(f"Failed to download. Status code: {response.status_code}, URL: {download_url}")

if __name__ == "__main__":
    latest_version = get_latest_version(BASE_URL)

    if latest_version:
        print(f"Latest Version: {latest_version}")
        last_version = read_last_version()

        if last_version == latest_version:
            print("Already up-to-date. No download needed.")
        else:
            download_latest_version(BASE_URL, latest_version)
    else:
        print("No valid versions found.")
