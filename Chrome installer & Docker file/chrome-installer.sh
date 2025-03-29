#!/bin/bash
set -e

chrome_linux_url="https://storage.googleapis.com/chrome-for-testing-public/134.0.6998.90/linux64/chrome-linux64.zip"
chromedriver_linux_url="https://storage.googleapis.com/chrome-for-testing-public/134.0.6998.90/linux64/chromedriver-linux64.zip"

download_path_chrome_linux="/opt/chrome-linux64.zip"
download_path_chrome_driver_linux="/opt/chromedriver-linux64.zip"

mkdir -p "/opt/chrome"
curl -Lo "$download_path_chrome_linux" "$chrome_linux_url"
unzip -q "$download_path_chrome_linux" -d "/opt/chrome"
rm -rf "$download_path_chrome_linux"

mkdir -p "/opt/chromedriver"
curl -Lo "$download_path_chrome_driver_linux" "$chromedriver_linux_url"
unzip -q "$download_path_chrome_driver_linux" -d "/opt/chromedriver"
rm -rf "$download_path_chrome_driver_linux"
chmod +x "/opt/chromedriver/chromedriver-linux64/chromedriver" # Add this line