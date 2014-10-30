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

To install, make a virtualenv and activate it, then::

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
