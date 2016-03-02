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
a relational database (we prefer MySQL) and Redis server are present on the system.
In apt-based Linux distros like Ubuntu/Debian, do::

    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get install mysql-server redis-server

Make sure they are running. Furthermore, you will need a few development packages::

    sudo apt-get install libmysqlclient-dev libxml2-dev libxslt-dev

For Python development, it's almost customary to install git, python-dev, python-pip
and the virtualenv package::

    sudo apt-get install git python-dev python-pip
    sudo pip install virtualenv

Installation
============
To install Texcavator, clone the repository in your home directory
and make a virtualenv, activate it, and install the requirements::

    cd ~
    git clone https://github.com/UUDigitalHumanitieslab/texcavator.git
    mkdir .virtualenvs
    virtualenv .virtualenvs/texc
    source .virtualenvs/texc/bin/activate
    pip install -r texcavator/requirements.txt

Then install the JavaScript toolkit Dojo_, on which the user interface is built::

    sh install-dojo.sh

.. _Dojo: http://dojotoolkit.org/

In ``texcavator/settings.py``, you can change the path to the log file, if you like.

Copy ``texcavator/settings_local_default.py`` to ``texcavator/settings_local.py``. The latter file is not kept under version control.

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

Preparing the data
==================

Make sure you have the kb data loaded in an Elasticsearch index. To install
Elasticsearch, see the website_. To get started using Elasticsearch see the quickstart_.

.. _website: https://www.elastic.co/
.. _quickstart: https://www.elastic.co/guide/en/elasticsearch/reference/current/getting-started.html

Texcavator assumes the data is in an index called ``kb`` (tip: use it as an alias).
In ``texcavator/settings_local.py``, you can specify the Elasticsearch host and port (typically localhost:9200).
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

    curl -XPUT localhost:9200/kb -d '
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
    }'

An example document would then be::

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

Development server
==================

First, make sure Elasticsearch is still running at the specified port.
Then, start Celery and the webserver::

    celery --app=texcavator.celery:app worker --loglevel=info
    # In a separate terminal
    python manage.py runserver

(In production, be sure to use ``--loglevel=warn``.)

Texcavator is now ready for use at ``http://localhost:8000``.

Downloading of query data requires a running SMTP server; you can use Python's build in for that::

    python -m smtpd -n -c DebuggingServer localhost:1025

Additional functionality via management commands
================================================

If you want to display timelines, run the management command ``gatherstatistics``::

    python manage.py gatherstatistics

To add a default list of stopwords, run the management command ``add_stopwords``::

    python manage.py add_stopwords stopwords/nl.txt

To be able to create word clouds normalized for inverse document frequency, run the management command ``gathertermcounts``::

    python manage.py gathertermcounts

Deployment
==========

For deployment, you could use Apache2 (we presume this installed) with mod_wsgi enabled::

    sudo apt-get install libapache2-mod-wsgi

Then, follow the instructions on https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/modwsgi/ closely,
and be sure to update settings.py and settings_local.py according to your server settings.

If you have deployed your server, updating can be done via the following commands::

    git stash
    git fetch --tags & git checkout <tag> OR git pull origin <branch>
    git stash apply
    python manage.py collectstatic
    sudo service apache2 restart

For Celery, follow the instructions on http://celery.readthedocs.org/en/latest/tutorials/daemonizing.html#example-django-configuration

For Postfix, follow the instructions on https://www.digitalocean.com/community/tutorials/how-to-install-and-setup-postfix-on-ubuntu-14-04

On request, we can provide you with a Puppet script that handles the complete installation for you.

Documentation
=============

The documentation for Texcavator is in Sphinx_. You can generate the documentation by running::

    make html

in the /doc/ directory.

.. _Sphinx: http://sphinx-doc.org/index.html
