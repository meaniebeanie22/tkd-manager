#!/bin/sh
celery -A tkdmanager worker --beat --concurrency=2 -l INFO