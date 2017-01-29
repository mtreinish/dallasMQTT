==========
dallasMQTT
==========
dallasMQTT is a service that will periodically poll an arbitray number of
dallas 1 wire sensors and publish the data to an MQTT broker.

Installation
============

dallasMQTT is availably via pypi, so all you need to do is run::

    pip install -U dallasMQTT

assuming you have pip installed. (which is the recommended way to install.
If you need to use a development version of dallasMQTT you can clone the repo and install it locally with::

    git clone https://github.com/mtreinish/dallasMQTT.git

and then install it with::

    pip install -e dallasMQTT

which will install dallasMQTT in your python environment in editable mode for
local development.

If you don't have pip installed you can manually install dallasMQTT by
cloning the repo and installing it from the repo base dir with::

    python setup.py install

but, note installing via pip is the recommended and supported method of
installing dallasMQTT. (even from a local git clone)

Configuration
=============
To configure dallasMQTT you need to create configuration yaml file that will
tell dallasMQTT how to access sensors, how to use MQTT, etc. The basic format
of the file with the 3 sections is::

  mqtt:
      hostname: foo

  sensors:
      - id: id number
        name: 'My Sensor'

  default:
      poll_rate: 60
      base_topic: a_topic


MQTT Section Configuration
--------------------------
This section is used to configure how dallasMQTT will connect to an MQTT broker.
To configure the ``mqtt`` section there are 3 options it currently takes:

 * ``hostname``
 * ``username``
 * ``password``

of these only ``hostname`` is **required**. The other 2 options are **optional**
you can use ``username and`` ``password`` if client auth is desired (or
required by your mqtt broker).

Sensor Section Configuration
----------------------------
The ``sensor`` section of the yaml config file is used to specify which sensors
are to be polled and how to label them in the mqtt topics. It takes in a list
of sensors of arbitrary size that takes in a combination of sensor ids and names
for example if there were 3 sensors it would look something like::

    sensors:
        - id: 28-000001
          name: Sensor1
        - id: 28-000002
          name: Sensor2
        - id: 28-000003
          name: Sensor3

This pattern is just repeated for how ever many sensors you want dallasMQTT to
poll. The ``name`` field is fairly self explanatory, and it is just the name
of the sensor that will be used as the second half of the topic on mqtt, like::

    $base_topic/$name

The id field is used to specify the sensor id to poll. dallasMQTT will poll
the sensor file at::

    /sys/bus/w1/devices/``$id``/w1_slave

So ensuring you put the proper id here is important otherwise dallasMQTT will
not be able to read the sensor data.

This section was written to be sufficiently broad so that in the future
additional sensor types could be added to dallasMQTT. This would be a very
simple addition and would just require adding an optional driver field to each
list element which would tell dallasMQTT which class to use for polling sensors.
(these additional sensor wouldn't necessarily have to be dallas 1 wire either)
But, as of right now there is only 1 class, DallasTemp, for 1 wire temperature
sensors, so this field doesn't exist. However, if/when dallasMQTT is updated
to include other sensor types the documentation will be updated. (and backwards
compatibility will be adhered to so as to not break anyone)

Default Section configuration
-----------------------------
The default section is where you configure settings that contol the basic
operation of dallasMQTT. There are 3 options in this section right now:

 * ``base_topic``
 * ``poll_rate``
 * ``max_threads``

All 3 options are optional.

``base_topic`` is used to set the basic topic used on MQTT for sending sensor
data. The messages will be sent on mqtt like::

    $base_topic/$sensor_name

by default this is set to ``dallasMQTT``.

``poll_rate`` is used to specify a time in seconds to wait between polling
the sensors on a worker thread. Note this is not time between individual sensors
but between polling all the sensors being handled by a single thread. Each
sensor in that group will be polled serially without any wait time between
them.

``max_threads`` is used to specify the maximum number of threads that dallasMQTT
will launch to poll sensors with. If there are less sensors in the configuration
file a single worker thread will be launched for each sensor. If there are more
sensors than threads the sensors will be equally distributed to the number of
workers specified. Each worker will handle polling the list of sensors it
received.

Usage
=====

To run dallasMQTT is fairly straightforward. After dallasMQTT is installed
you just run::

    dallasMQTT config.yaml

where config.yaml is the path to your yaml config file.
