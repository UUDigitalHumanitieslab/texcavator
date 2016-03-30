import StringIO
import zipfile

import requests

r = requests.get('https://github.com/c-martinez/ShiCo/archive/master.zip', stream=True)
z = zipfile.ZipFile(StringIO.StringIO(r.content))

for f in z.namelist():
    if f.startswith('ShiCo-master/webapp/'):
        z.extract(f, 'texcavator/static/js/')
