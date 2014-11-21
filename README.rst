::

     _____                             _             
    |_   _|____  _____ __ ___   ____ _| |_ ___  _ __ 
      | |/ _ \ \/ / __/ _` \ \ / / _` | __/ _ \| '__|
      | |  __/>  < (_| (_| |\ V / (_| | || (_) | |   
      |_|\___/_/\_\___\__,_| \_/ \__,_|\__\___/|_|   


Copyright Netherlands eScience Center, University of Amsterdam.

Distributed under the terms of the Apache2 license. See LICENSE for details.


Installation
============
To install Texcavator, make a virtualenv and activate it, then::

    pip install -r requirements.txt

Install Dojo::

    sh install-dojo.sh

In ``settings.py``, change the path to the log, if your installation does
not live in ``/home/jvdzwaan``. In ``texcavator/settings_local.py``, set up
the database; for a quick test, set::

    DATABASE_ENGINE = 'django.db.backends.sqlite3'

Make sure Redis and MySQL (if needed) are running.
Populate the database if this is the first time you're running Texcavator::

    python manage.py syncdb

Finally, start Celery and the webserver::

    celery --app=texcavator.celery:app worker --loglevel=info
    # In a separate terminal
    python manage.py runserver

(In production, use ``--loglevel=warn``.)

Texcavator is now ready for use at ``http://localhost:8000``.

If you want to display timelines, run the management command
``gatherstatistics``::

    python manage.py gatherstatistics

Preparing the data
==================

Make sure you have the kb data loaded in an Elasticsearch index. To install
Elasticsearch, see the website_. To get started using Elasticsearch see the quickstart_.

.. _website: http://www.elasticsearch.org/
.. _quickstart: http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/getting-started.html

Texcavator assumes the data is in an index called ``kb`` (tip: use it as an alias).

Texcavator requires that the documents are stored in a ``doc_type`` doc that has at least the following fields:

* article_dc_subject
* article_dc_title
* identifier
* paper_dc_date
* paper_dc_title
* paper_dcterms_spatial
* paper_dcterms_temporal
* text_content

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