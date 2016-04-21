import os
import shutil
import StringIO
import zipfile

import requests

VERSION = '0.5'
GITHUB_URL = 'https://github.com/NLeSC/ShiCo/archive/v{}.zip'.format(VERSION)
DIST_DIR = 'ShiCo-{}/webapp/dist/'.format(VERSION)
STATIC_DIR = 'texcavator/static/js/'
TMP_DIR = 'ShiCo-{}'.format(VERSION)
FINAL_DIR = 'ShiCo'

# Retrieve the archive from GitHub
r = requests.get(GITHUB_URL, stream=True)
z = zipfile.ZipFile(StringIO.StringIO(r.content))

# Extract files from the DIST_DIR to the STATIC_DIR
for f in z.namelist():
    if f.startswith(DIST_DIR):
        z.extract(f, STATIC_DIR)

# Move the files to the ShiCo folder
shutil.move(os.path.join(STATIC_DIR, DIST_DIR), os.path.join(STATIC_DIR, FINAL_DIR))
shutil.rmtree(os.path.join(STATIC_DIR, TMP_DIR))
