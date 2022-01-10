.. 
    oncodash-backend documentation master file, created by
    sphinx-quickstart on Thu Nov 25 11:48:16 2021.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.
..
    Python's recommended sections marks:
        # with overline, for parts
        * with overline, for chapters
        =, for sections
        -, for subsections
        ^, for subsubsections
        ", for paragraphs

##############################
Oncodash backend documentation
##############################

************
Architecture
************

Django's Model-View-Template
============================

Oncodash' backend is based on the `Django <https://www.djangoproject.com/>`_ framework.
Django is a high-level Python framework for implementing server-side web application,
which separates core features in several, loosely coupled, programming tools.

A few concepts are key to understand how Oncodash is architectured with Django (see :numref:`Figure {number}<Django_MVT>`):

Models
    encapsulate every aspects of an object of interest, for instance wrapping a row in a database,
    encapsulating the database access and adding some domain logic to the data.

Templates
    are tools that control presentation of the Human-Machine Interface and the data (and the underlying logic).

Views
    receive requests from the client, gather the related data from models and inject them into the templates.

API
    the Application Programming Interface is a set of URL, which are all coupled to an underlying Python code.


.. _Django_MVT:

.. figure:: _static/django_MVT.svg
    :class: diagram

    The *Model-View-Template* architecture used by Django to build web application.

Note that in this view, the *client* can be the frontend application used by the operator or another kind of application.
More precisely, the client may be a widget of the frontend application,
requesting new data to display (e.g. a new set of patients)
or an update of the data (e.g. a new patient).
Depending on the API, the answer may be a JSON message or an HTML section.

Every other data that goes through the internal application is a Python object.
Note also that external data access may be done through the same kind of Web API
(i.e. function calls on a URL, through HTTP, sending JSON and getting JSON back).


************
Main modules
************

.. toctree::
    :maxdepth: 3
    :caption: Main modules:

    clinical
    explainer


******************
Complete Reference
******************

.. toctree::
    :maxdepth: 3
    :caption: Complete Reference

    reference


******************
Index and Tables
******************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
