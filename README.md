# parkinglot
Parkinglot is a SAAS application which allow user to create, manage, maintain and sell parking spaces to the user. Owner can set custom prices based on duration (days, hour), pre paid charges and over due charge.

Requirements
------------

* **Python**: 3.4+
* **Django**: 2.0+
* **DRF**: 3.8+
* **DOCKER**: 18+

Installation
------------

Install using local environment:

Redirect to project folder from shell/terminal

.. code-block:: sh

    python3 -m venv .env

Activate environment

.. code-block:: sh

    source .env/bin/activate

Install dependancies

.. code-block:: sh

    pip install -r requirements.txt

Run migration to setup database

.. code-block:: sh

    python manage.py migrate

Create superuser in case of django admin access

.. code-block:: sh

    python manage.py createsuperuser

Now everything is setup, enable web server on specific port

.. code-block:: sh

    python manage.py runserver 0.0.0.0:8000

Install using docker:

Redirect to project folder. Enable docker service

.. code-block:: sh

    sudo systemctl docker start

Build docker-compose image

.. code-block:: sh

    docker-compose build

Once the build is done then run docker image

.. code-block:: sh

    docker-compose up

API Documentation
------------
We use swagger documentation to auto document request and response.
Following API serve API documentation

* http://<server_ip_address>:<server_port>/swagger
* http://<server_ip_address>:<server_port>/redoc
