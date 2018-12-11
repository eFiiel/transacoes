#!/bin/bash
chmod +x serverStart.sh

python3 coord/manage.py runserver localhost:8000
python3 hotel/manage.py runserver localhost:8500
python3 passagem/manage.py runserver localhost:9000
