#!/bin/bash
echo "Starting Resume Parser Service"
cd /opt/app
gunicorn --workers=1 -b 0.0.0.0:5000 ResumeParser:app --log-file=-
