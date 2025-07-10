#!/usr/bin/env python3
"""
🚀 Azure Startup Script for Guerilla AI

This script starts the optimized AI application on Azure App Service.
"""

import os
import sys
import subprocess
from app_optimized import app

if __name__ == "__main__":
    # Set environment variables for Azure
    port = int(os.environ.get('PORT', 5000))
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=port, debug=False) 