#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Build the Mac app using PyInstaller
pyinstaller --onefile --windowed --name="EMall计划维护助手" --collect-all=customtkinter updateGUI_mac.py