#!/usr/bin/env python3
"""
Celery Worker Module for OnlyPark Application
Handles background task processing including email notifications and CSV exports
"""

import os
import sys
from celery_app import celery
from app import app

# Import all tasks to ensure they are registered with Celery
import tasks

# Configure Celery worker
if __name__ == '__main__':
    # Set up proper logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Start the worker with proper configuration
    with app.app_context():
        celery.start()
