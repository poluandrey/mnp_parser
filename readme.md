# MNP file parser
## Description
### These scripts allow you to parse incoming files from different sources, copy parsed files to local FTP storage and to the remote server

## Set up
1) create virtual environment
``python -m venv venv``
2) install requirements
``pip install -r requirements.txt``
3) fill .env file
``mv .env_example .env``
4) get help message
``python main.py --help``
5) parse BD for country_name
``python main.py --country country_name``
