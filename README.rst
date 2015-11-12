==========
Woodpecker
==========

.. image:: https://codeclimate.com/github/steromano87/Woodpecker/badges/gpa.svg
    :target: https://codeclimate.com/github/steromano87/Woodpecker
    :alt: Code Climate

.. image:: https://badge.fury.io/py/woodpecker.svg
    :target: https://badge.fury.io/py/woodpecker


Woodpecker is a Python package that aims to be a lightweight --- but complete --- load generator and analysis tool for various environments.

While other far more famous tools like HP LoadRunner(R) or Apache JMeter either propose a complex and heavy application to perform load tests or require a very expensive license to work, Woodpecker's main focus is on easiness of use, small memory footprint and smartness in data analysis --- and, most of all, it is an Open Source Software since is released under the GNU LGPL version 3 license.

This project is still in development phase, but first benchmarks shows that the memory footprint for each Virtual User (here called *spawn*) is about 516 Kb. When the first development phase will be completed, this package will become publicly available for download from PyPi.


------------
Requirements
------------
At the moment the libraries required to run Woodpecker are the following:
- python-dateutil

- colorama

- click

- psutil

- requests

All of them are hosted on PyPi and can be installed using ``pip`` or ``easy_install``:

``pip install -r requirements.txt``


----------------
Planned features
----------------
- Command-line interface to initialize scenarios, create transactions from HAR files, start/stop controller and remote spawners and analyze results
- Fully portable results storage in a single SQLite3 file
- Generic load profile generation by combination of basic ramp elements
- Capability to generate load on:
    - Web pages using HTTP protocol
    - SOA services
    - Databases
    - Web Video Streams
    - Sockets
- Powerful HTML report creation using the Jinja2 templating engine (with PDF output, too)
- SLA support and real-time or *a posteriori* check
- Easy parameters retrieval and reuse, also in different transactions
- Custom transactions support
- Requests result assertions
- Different spawning logic (using threads or sub-processes) to optimize memory consumption different architectures
- Easily switch between different load configurations by changing one parameter in command-line invocation
