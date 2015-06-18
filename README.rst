::

     _____                             _             
    |_   _|____  _____ __ ___   ____ _| |_ ___  _ __ 
      | |/ _ \ \/ / __/ _` \ \ / / _` | __/ _ \| '__|
      | |  __/>  < (_| (_| |\ V / (_| | || (_) | |   
      |_|\___/_/\_\___\__,_| \_/ \__,_|\__\___/|_|   


Copyright Netherlands eScience Center, University of Amsterdam.
From 2015 onwards developed by the Digital Humanities Lab, Utrecht University.

Distributed under the terms of the Apache2 license. See LICENSE for details.


Dependencies
============
Before installing Texcavator, make sure your packages are up-to-date and
a MySQL and Redis server are present on the system.
In apt-based Linux distros like Ubuntu, do::

    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get install mysql-server redis-server

Also make sure they are running. Furthermore, you will need a few development packages::

    sudo apt-get install libmysqlclient-dev libxml2-dev libxslt-dev

For Python development, it's almost customary to install git, python-dev, python-pip
and the virtualenv package::

    sudo apt-get install git python-dev python-pip
    sudo pip install virtualenv

Installation
============
To install Texcavator, clone the repository and make a virtualenv, activate it, and install the requirements::

    cd ~
    git clone https://github.com/UUDigitalHumanitieslab/texcavator.git
    mkdir .virtualenvs
    virtualenv .virtualenvs/texc
    source .virtualenvs/texc/bin/activate
    pip install -r texcavator/requirements.txt

Install Dojo::

    sh install-dojo.sh

In ``texcavator/settings.py``, you can change the path to the log file, if you like.

In ``texcavator/settings_local.py``, set up the database; for a quick test, set::

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(PROJECT_PARENT, 'db.sqlite3')
        }
    }

Make sure Redis and MySQL (if needed) are running.
Populate the database if this is the first time you're running Texcavator::

    python manage.py migrate

Create a Django superuser::

    python manage.py createsuperuser

The username and password you pick will be the administrator account for
Texcavator.

Finally, start Celery and the webserver::

    celery --app=texcavator.celery:app worker --loglevel=info
    # In a separate terminal
    python manage.py runserver

(In production, use ``--loglevel=warn``.)

Also make sure Elasticsearch is running.
Texcavator is now ready for use at ``http://localhost:8000``.

If you want to display timelines, run the management command
``gatherstatistics``::

    python manage.py gatherstatistics

Downloading of query data requires a running SMTP server; you can use Python's build in for that::

    python -m smtpd -n -c DebuggingServer localhost:1025

Preparing the data
==================

Make sure you have the kb data loaded in an Elasticsearch index. To install
Elasticsearch, see the website_. To get started using Elasticsearch see the quickstart_.

.. _website: http://www.elasticsearch.org/
.. _quickstart: http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/getting-started.html

Texcavator assumes the data is in an index called ``kb`` (tip: use it as an alias).

Texcavator requires that the documents are stored in a doc_type ``doc`` that has at least the following fields:

* article_dc_subject
* article_dc_title
* identifier
* paper_dc_date
* paper_dc_title
* paper_dcterms_spatial
* paper_dcterms_temporal
* text_content

And mapping::

    PUT /kb
    {
      "settings": {
        "analysis" : {
          "analyzer" : {
            "dutch_analyzer" : {
              "type" : "custom",
              "tokenizer": "standard",
              "filter" : ["standard", "lowercase", "dutch_stemmer"]
            }
          },
          "filter" : {
            "dutch_stemmer" : {
              "type" : "stemmer",
              "name" : "dutch_kp"
            }
          }
        }
      },
      "mappings": {
        "doc": {
          "properties" : {
            "article_dc_subject": {
              "type": "string",
              "include_in_all": "false",
              "index": "not_analyzed"
            },
            "article_dc_title": {
              "type": "string",
              "term_vector": "with_positions_offsets_payloads",
              "fields": {
                "stemmed": {
                  "type": "string",
                  "analyzer": "dutch_analyzer",
                  "term_vector": "with_positions_offsets_payloads"
                }
              }
            },
            "identifier": {
              "type": "string",
              "include_in_all": "false",
              "index": "not_analyzed"
            },
            "paper_dc_date": {
              "format": "dateOptionalTime",
              "type": "date"
            },
            "paper_dc_title": {
              "type": "string",
              "term_vector": "with_positions_offsets_payloads",
              "fields": {
                "raw": {
                  "type": "string",
                  "index": "not_analyzed"
                }
              }
            },
            "paper_dcterms_spatial": {
              "type": "string",
              "include_in_all": "false",
              "index": "not_analyzed"
            },
            "paper_dcterms_temporal": {
              "type": "string",
              "include_in_all": "false",
              "index": "not_analyzed"
            },
            "text_content": {
              "type": "string",
              "term_vector": "with_positions_offsets_payloads",
              "fields": {
                "stemmed": {
                  "type": "string",
                  "analyzer": "dutch_analyzer",
                  "term_vector": "with_positions_offsets_payloads"
                }
              }
            }
          }
        }
      }
    }

An example document::

    curl -XPOST localhost:9200/kb/doc -d '{
        "article_dc_subject": "newspaper", 
        "article_dc_title": "Test for Texcavator", 
        "identifier": "test1", 
        "paper_dc_date": "1912-04-15", 
        "paper_dc_title": "The Texcavator Test", 
        "paper_dcterms_spatial": "unknown", 
        "paper_dcterms_temporal": "daily", 
        "text_content": "This is a test to see whether Texcavator works!"
    }'

Deployment
==========

For deployment, you could use Apache2 (we presume this installed) with mod_wsgi enabled ::

    sudo apt-get install libapache2-mod-wsgi

Then, follow the instructions on https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/modwsgi/ closely.
