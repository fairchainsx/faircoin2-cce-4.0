============================
CCE 4  - Open Source Version
============================

.. contents::

This package is the basic open source version of CryptoCoin Explorer 4.0.

The purpose of a block chain explorer is to setup and maintain a
web application friendly database of a cryptocoin block chain.
A basic database loader and explorer web server is included.

This package is intended to be a foundation in creating a feature rich
explorer. However, it can be used as a basic explorer as-is.

The closed source production version in development is much more robust and feature rich.
In the time up to the roll out/upgrade of cryptocoinexplorer.com from 3.5 to 4.0, some features
will be added to this open source package.


Requirements for Database Loader
--------------------------------
* Python 3.x
* MySQL-Server
* Simplejson
* PyMySql
* Interrupting cow
* Requests

Requirements for Web Server
---------------------------
* All the requirements for the Database Loader
* CherryPy >= 3.6
* Jinja2
* DBUtils 1.1

Installation
-------------------------
* follow the instructions [/docs/installation.md](/docs/installation.md)

Usage
-------------------------
* follow the instructions [/docs/usage.md](/docs/usage.md)

Documentation Files
-------------------
* some more detailed informations are located in the the docs folder

        - dbload.rst (Setup, configuration and operation of the database loader)

        - web_server.rst (Setup, configuration and operation of the web server)
