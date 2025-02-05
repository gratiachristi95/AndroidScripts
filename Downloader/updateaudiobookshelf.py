import os
import requests
from bs4 import BeautifulSoup

# File to store the last downloaded version
VERSION_FILE = "audiobookshelf_latest_version.txt"

# URL of the GitHub tags page
TAGS_URL = "https://github.com/advplyr/audiobookshelf-app/tags"

def get_latest_version():
    """Fetches the latest version from GitHub."""
    try:
        response = requests.get(TAGS_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract version tags from the page
        tags = soup.find_all('a', href=True)
        for tag in tags:
            if '/advplyr/audiobookshelf-app/releases/tag/' in tag['href']:
                return tag['href'].split('/')[-1]
    except Exception as e:
        print(f"Error fetching the latest version: {e}")
    return None

def download_apk(version):
    """Downloads the APK for the given version."""
    try:
        apk_url = f"https://github.com/advplyr/audiobookshelf-app/releases/download/{version}/app-release.apk"
        apk_file = f"audiobookshelf-{version}.apk"
        print(f"Downloading APK for version {version}...")
        response = requests.get(apk_url, stream=True)
        response.raise_for_status()
        with open(apk_file, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded {apk_file}")
        return apk_file
    except Exception as e:
        print(f"Error downloading APK: {e}")
    return None

def main():
    # Get the latest version from GitHub
    latest_version = get_latest_version()
    if not latest_version:
        print("Failed to fetch the latest version. Please check your internet connection or the URL.")
        return

    # Check if VERSION_FILE exists and read its content
    current_version = ""
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r") as file:
            current_version = file.read().strip()

    # Compare versions and download if there's a new one
    if latest_version != current_version:
        print(f"New version found: {latest_version} (Current: {current_version})")
        apk_file = download_apk(latest_version)
        
        if apk_file:
            # Update the VERSION_FILE with the new version
            with open(VERSION_FILE, "w") as file:
                file.write(latest_version)
            print(f"Updated to version {latest_version}.")
            
            # Open the downloaded APK using termux-open
            os.system(f"termux-open {apk_file}")
    else:
        print(f"No new version found. Current version ({current_version}) is up-to-date.")

if __name__ == "__main__":
    main()
