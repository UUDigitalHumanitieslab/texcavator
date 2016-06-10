============
Introduction
============

Texcavator is a text mining web application.
Its back-end is written in the Django_ framework, while the front-end relies heavily upon the Dojo_ toolkit.
The web application allows users to fire queries on an Elasticsearch index and will convert the responses into visualizations (for which we use D3.js_).
For larger requests (i.e. word cloud generation on multiple documents) we use Celery_ as a background task queue.

======
Python
======

Texcavator uses the following Python packages (see ``requirements.in``):

- Django_: web framework.
- elasticsearch_: elasticsearch connector for Python.
- Celery_: distributed task queue.
- redis_: key-value store, connects Django with Celery.
- MySQL-python_: MySQL connector for Python. Can be replaced with a connector to any other RDMS (e.g. pyscopg2)
- sqlparse_: allows raw SQL operations on databases.
- requests_: makes API requests more easy.
- DAWG_: allows creation of direct acyclic word graphs, which allows us to efficiently save frequencies of all words in the corpus.
- dicttoxml: converts dictionaries to XML; used for generating XML output in the download functionality.
- Sphinx_: documentation generator.
- nose_: test enhancement suite.
- django-nose_: nose connector for Django.

.. _Django: https://www.djangoproject.com/
.. _Celery: http://www.celeryproject.org/
.. _redis: http://redis.io/
.. _elasticsearch: http://elasticsearch-py.readthedocs.io/en/master/
.. _MySQL-python: https://pypi.python.org/pypi/MySQL-python
.. _sqlparse: https://sqlparse.readthedocs.io/en/latest/
.. _requests: http://docs.python-requests.org/en/latest/
.. _DAWG: https://github.com/kmike/DAWG
.. _dicttoxml: https://pypi.python.org/pypi/dicttoxml
.. _Sphinx: http://www.sphinx-doc.org/en/stable/
.. _nose: http://nose.readthedocs.io/en/latest/
.. _django-nose: https://django-nose.readthedocs.io/en/latest/

==========
JavaScript
==========

Texcavator heavily uses the Dojo_ toolkit for its frontend.
jQuery_ is used on places where Dojo doesn't have readily solutions available.

For our visualizations we leverage D3.js_ (word clouds and time lines), nvd3_ (metadata visualizations) and Cal-HeatMap_ (heatmaps).

To aids users in using correct syntax when querying the elasticsearch index, we have created a parsing expression grammar in PEG.js_.

.. _Dojo: https://dojotoolkit.org/
.. _jQuery: http://jquery.com/
.. _D3.js: https://d3js.org/
.. _nvd3: http://nvd3.org/
.. _Cal-HeatMap: http://cal-heatmap.com/
.. _PEG.js: http://pegjs.org/
