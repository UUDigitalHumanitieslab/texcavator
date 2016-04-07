import os
import shutil
import StringIO
import zipfile

import requests

GITHUB_URL = 'https://github.com/c-martinez/ShiCo/archive/demo.zip'
DIST_DIR = 'ShiCo-demo/webapp/dist/'
STATIC_DIR = 'texcavator/static/js/'
TMP_DIR = 'ShiCo-demo'
FINAL_DIR = 'ShiCo'

# Retrive the demo branch from GitHub
r = requests.get(GITHUB_URL, stream=True)
z = zipfile.ZipFile(StringIO.StringIO(r.content))

# Extract files from the dist directory
for f in z.namelist():
    if f.startswith(DIST_DIR):
        z.extract(f, STATIC_DIR)

# Move the files to the ShiCo folder
shutil.move(os.path.join(STATIC_DIR, DIST_DIR), os.path.join(STATIC_DIR, FINAL_DIR))
shutil.rmtree(os.path.join(STATIC_DIR, TMP_DIR))
