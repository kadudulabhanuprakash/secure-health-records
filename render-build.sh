#!/usr/bin/env bash

# --- Step 1: Install system dependencies for pyodbc ---
apt-get update
apt-get install -y unixodbc-dev g++

# --- Step 2: Upgrade pip ---
pip install --upgrade pip

# --- Step 3: Install Python dependencies ---
pip install -r backend/requirements.txt
