#!/bin/sh

set -e -x

URL=http://download.dojotoolkit.org/release-1.8.6/dojo-release-1.8.6.tar.gz

cd texcavator/static/js
curl ${URL} | tar xzvf -
