==========
Deployment
==========

Texcavator is currently battle-tested on a Debian-based distribution with Apache_ (`mod_wsgi`), MySQL_, Redis_ and Postfix_.
Starting from a clean install, this guide should get you going.
Feel free to replace one or all of these components, but then the usual caveats apply.

.. _Apache: https://httpd.apache.org/
.. _MySQL: https://www.mysql.com/
.. _Redis: http://redis.io/
.. _Postfix: http://www.postfix.org/

************
Dependencies
************

First, let's install some dependencies::

    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get install apache2
    sudo apt-get install mysql-server
    sudo apt-get install redis-server
    sudo apt-get install postfix
    sudo apt-get install libapache2-mod-wsgi libmysqlclient-dev libxml2-dev libxslt-dev

During installation of ``mysql-server`` and ``postfix``, make sure to jot down the details to set these in Texcavator's settings later on.

*************
elasticsearch
*************

You can run elasticsearch_ on the same server as Texcavator, but we would propose setting up a separate server.
See https://www.elastic.co/guide/en/elasticsearch/guide/current/deploy.html for some instructions.

.. _elasticsearch: https://www.elastic.co/

**********************
Retrieving the sources
**********************

This should be easy, as you can retrieve the sources from GitHub_::

    sudo apt-get install git
    git clone https://github.com/UUDigitalHumanitieslab/texcavator.git

.. _GitHub: https://github.com/

*******************
Virtual environment
*******************

It's customary to install the Python dependencies in a virtual environment, so::

    sudo apt-get install python-pip
    pip install virtualenv

Then, activate the virtual environment and install the requirements using the ``requirements.txt`` provided in the source directory::

    pip install -r requirements.txt

********************
Application settings
********************

Copy ``texcavator/settings_local_default.py`` to ``texcavator/settings_local.py``.
The latter file is not kept under version control.
Then, change the settings in ``texcavator/settings_local.py`` and (if necessary) ``texcavator/settings.py`` to reflect your setup.

Run the commands in the section **Prerequisite commands** from ``README.rst``.

********
Database
********

Create a database (and user) in your RDMS. After that, run::

    python manage.py migrate

from your virtual environment to migrate the database to the latest and greatest version.

******
Celery
******

For Celery_, it's (probably) best to use the ``celery multi`` command, from your virtual environment, with a specific celery user.
The following command would start 3 workers with 8 concurrent processes, more than enough for Texcavator::

   ${virtualenv}/bin/celery multi restart worker1 worker2 worker3 --app=texcavator.celery:app --workdir=${app_source} --time-limit=300 --concurrency=8 --logfile=${logging_location}/celery/%N.log --pidfile=${celery_root}/%N.pid --uid=${celery_user} --gid=${celery_group}

.. _Celery: http://www.celeryproject.org/

******
Apache
******

Setting up Apache and mod_wsgi to serve Django is quite a challenge.
Luckily, there is some excellent documentation available online.
Be sure to update settings.py and settings_local.py according to your settings.
You can collect static files using the ``collectstatic`` management command::

    python manage.py collectstatic

======
Puppet
======

We have a Puppet module available that will install the application:
you'll only have to install the dependencies, and afterwards the complete application environment will be created.
Drop us an e-mail if you're interested in that.
