**This project is no longer maintained and has been archived. It is succeeded by I-Analyzer, which is actively developed: https://github.com/UUDigitalHumanitieslab/I-analyzer.**

::

     _____                             _             
    |_   _|____  _____ __ ___   ____ _| |_ ___  _ __ 
      | |/ _ \ \/ / __/ _` \ \ / / _` | __/ _ \| '__|
      | |  __/>  < (_| (_| |\ V / (_| | || (_) | |   
      |_|\___/_/\_\___\__,_| \_/ \__,_|\__\___/|_|   


Copyright '`Digital Humanities lab` @ Utrecht University',`Netherlands eScience Center`_, `University of Amsterdam`_. 

From 2015 onwards developed by the `Digital Humanities lab`_, Utrecht University.

.. _`Netherlands eScience Center`: https://www.esciencecenter.nl/
.. _`University of Amsterdam`: http://www.uva.nl/en/
.. _`Digital Humanities lab`: http://dig.hum.uu.nl/

Developer quick-start
=====================

************
Dependencies
************

Before installing Texcavator, make sure your packages are up-to-date and
a relational database (we use MySQL_) and Redis_ server are present on the system.
In apt-based Linux distros like Ubuntu/Debian, issue::

    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get install mysql-server redis-server

Make sure both servers are running. Furthermore, you will need a few development packages::

    sudo apt-get install libmysqlclient-dev libxml2-dev libxslt-dev python-dev

.. _MySQL: https://www.mysql.com/
.. _Redis: http://redis.io/

************
Installation
************

To install Texcavator, clone the repository (using git_) in your home directory
and make a virtualenv_, activate it, and install the requirements::

    sudo apt-get install git python-pip
    pip install virtualenv
    cd ~
    git clone https://github.com/UUDigitalHumanitieslab/texcavator.git
    mkdir .virtualenvs
    virtualenv .virtualenvs/texc
    source .virtualenvs/texc/bin/activate
    pip install -r texcavator/requirements.txt

In ``texcavator/settings.py``, you can change the path to the log file, if you like.

Copy ``texcavator/settings_local_default.py`` to ``texcavator/settings_local.py``.
The latter file is not kept under version control.

In ``texcavator/settings_local.py``, set up the database; for a quick test, you can use SQLite::

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(PROJECT_PARENT, 'db.sqlite3')
        }
    }

.. _git: https://git-scm.com/
.. _virtualenv: http://virtualenv.readthedocs.io/

*************
Elasticsearch
*************

The next step is to load your data into an elasticsearch_ index.
To get started using elasticsearch see the quickstart_.

In ``texcavator/settings_local.py``, you can specify the elasticsearch host and port
(typically elasticsearch runs on ``localhost:9200``).
Texcavator assumes by default the data is in an index called ``kb`` and
that the documents are stored in a type ``doc`` that has at least the following fields:

* article_dc_subject
* article_dc_title
* identifier
* paper_dc_date
* paper_dc_title
* paper_dcterms_spatial
* paper_dcterms_temporal
* text_content

We use the mapping specified in ``mapping.rst``.

.. _elasticsearch: https://www.elastic.co/
.. _quickstart: https://www.elastic.co/guide/en/elasticsearch/reference/current/getting-started.html

*********************
Prerequisite commands
*********************

Texcavator requires you to install some external packages and management commands in order to function correctly.
Before issuing the commands below, make sure Elasticsearch, MySQL and Redis are still running at the specified ports.

* Install ShiCo, which allows for visualizing shifting concepts over time::

    python install-shico.py

* Populate the database::

    python manage.py migrate

* Create a Django superuser. The username and password you pick will be the administrator account for Texcavator::

    python manage.py createsuperuser

* Run the management command ``gatherstatistics`` to be able to display timelines::

    python manage.py gatherstatistics

* Run the management command ``add_stopwords`` to add a default list of (Dutch) stop words::

    python manage.py add_stopwords stopwords/nl.txt

* Run the management command ``gathertermcounts`` to be able to create word clouds normalized for inverse document frequency::

    python manage.py gathertermcounts

* Run the management command ``add_guest_user`` to add a guest environment (with limited options)::

    python manage.py add_guest_user

.. _Dojo: http://dojotoolkit.org/

******************
Development server
******************

First, make sure Elasticsearch, MySQL and Redis are still running at the specified ports.
Then, start Celery and Django's built-in webserver::

    celery --app=texcavator.celery:app worker --loglevel=info
    # In a separate terminal
    python manage.py runserver

Texcavator is now ready for use at ``http://127.0.0.1:8000``.

Downloading of query data requires a running SMTP server; you can use Python's built-in server for that::

    # In a separate terminal
    python -m smtpd -n -c DebuggingServer localhost:1025

Deployment
==========

You can find instructions for deploying Texcavator in ``deployment.rst``

Documentation
=============

The documentation for Texcavator is in Sphinx_. You can generate the documentation by running::

    make html

in the /doc/ directory.

.. _Sphinx: http://sphinx-doc.org/index.html


License
=======

Texcavator is distributed under the terms of the Apache2 license. See ``LICENSE`` for details.
