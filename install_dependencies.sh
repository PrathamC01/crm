#!/bin/bash

# Install Dependencies for Automation Testing
# Enterprise CRM System

echo "🔧 Installing Testing Dependencies..."

# Python dependencies for testing
echo "📦 Installing Python testing packages..."
pip install selenium requests

# Install Chrome for Selenium testing
echo "🌐 Setting up Chrome for automated testing..."

# Update package list
apt-get update

# Install Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
apt-get update
apt-get install -y google-chrome-stable

# Install ChromeDriver
echo "🚗 Installing ChromeDriver..."
CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)
wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip
unzip /tmp/chromedriver.zip -d /tmp/
chmod +x /tmp/chromedriver
mv /tmp/chromedriver /usr/local/bin/chromedriver

# Verify installations
echo "✅ Verifying installations..."
python3 -c "import selenium; print('Selenium installed successfully')"
google-chrome --version
chromedriver --version

echo "🎉 All testing dependencies installed successfully!"
echo ""
echo "📋 Available test scripts:"
echo "  • python3 /app/frontend_backend_test_automation.py  # Complete testing suite"
echo "  • python3 /app/quick_test_script.py                 # Quick backend tests"
echo ""
echo "🚀 Ready to run automated tests!"