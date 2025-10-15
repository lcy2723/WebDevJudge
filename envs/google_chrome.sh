#!/bin/bash

if [ -f "/usr/bin/google-chrome" ]; then
    echo "Chrome is already installed"
    INSTALLED_VERSION=$(google-chrome --version | cut -d ' ' -f 3)
    echo "Installed Chrome version: $INSTALLED_VERSION"
    echo "Cleaning up old Chrome installation..."
    rm -rf /opt/chrome-linux64
    rm -f /usr/local/bin/chromedriver
    rm -f /usr/bin/google-chrome
    echo "Rerun this script to install Chrome and ChromeDriver"
else
    # install Chrome and ChromeDriver, need to be the latest version
    CHROME_VERSION="142.0.7412.0"
    echo "installing Chrome and ChromeDriver version: ${CHROME_VERSION}..."

    # create temporary directory
    mkdir -p /tmp/chrome_install
    cd /tmp/chrome_install

    # download and install Chrome and ChromeDriver
    wget -q https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chrome-linux64.zip
    wget -q https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip

    unzip chrome-linux64.zip
    unzip chromedriver-linux64.zip

    # move Chrome and ChromeDriver to the correct position
    mv chrome-linux64 /opt/
    mv chromedriver-linux64/chromedriver /usr/local/bin/

    # set permissions
    chmod +x /usr/local/bin/chromedriver
    chmod +x /opt/chrome-linux64/chrome

    # create a symbolic link for Chrome
    ln -sf /opt/chrome-linux64/chrome /usr/bin/google-chrome

    # clean up temporary files
    cd /
    rm -rf /tmp/chrome_install
fi