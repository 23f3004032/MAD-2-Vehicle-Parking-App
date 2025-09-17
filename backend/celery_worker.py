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
