import os
import shutil
import StringIO
import urlparse
import zipfile

import requests

VERSION = '0.6'
GITHUB_URL = 'https://github.com/NLeSC/ShiCo/archive/v{}.zip'.format(VERSION)

STATIC_DIR = 'texcavator/static/js/'
DIST = 'ShiCo-{}/webapp/dist/'.format(VERSION)
DIST_DIR = os.path.join(STATIC_DIR, DIST)
FINAL_DIR = os.path.join(STATIC_DIR, 'ShiCo')

# Retrieve the archive from GitHub
print 'Retrieving the archive...'
r = requests.get(GITHUB_URL, stream=True)
z = zipfile.ZipFile(StringIO.StringIO(r.content))

# Extract files from the DIST_DIR to the STATIC_DIR
print 'Unpacking...'
for f in z.namelist():
    if f.startswith(DIST):
        z.extract(f, STATIC_DIR)

# Move the files to the ShiCo folder
print 'Moving to ShiCo folder...'
shutil.rmtree(FINAL_DIR, ignore_errors=True)
shutil.move(DIST_DIR, STATIC_DIR)
os.rename(os.path.join(STATIC_DIR, 'dist'), FINAL_DIR)
shutil.rmtree(os.path.join(STATIC_DIR, 'ShiCo-{}'.format(VERSION)))

# Replace relative paths with absolute paths
print 'Replacing paths...'
print os.path.join(FINAL_DIR, 'scripts/app.js')
with open(os.path.join(FINAL_DIR, 'scripts/app.js'), 'r+') as f:
    lines = []
    for line in f:
        line = line.replace('config.json', urlparse.urljoin(FINAL_DIR, 'config.json'))
        line = line.replace('/help/algorithm.md', urlparse.urljoin(FINAL_DIR, 'help/algorithm.md'))
        lines.append(line)

    f.seek(0)
    f.truncate()
    for line in lines:
        f.write(line)
