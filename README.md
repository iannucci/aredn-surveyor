# AREDN Wardriving

A set of tools for collecting AREDN signal strength data, geo-referencing it, and displaying the data on a map.  This code was initially developed to run on a Mac, but it is being maintained to run on a Raspberry Pi (tested on a Pi 3 running 64 bit Raspberry Pi OS).

## Hardware Configuration

A HiLetgo VK172 USB GPS/GLONASS USB GPS Receiver should be plugged into an available USB port.  It needs a clear sky view, and a USB extension cable may be needed.  The baud rate is 115200.  Check /dev to find the port.  /dev/ttyACM0 is typical

## Software installation

### Database

The code uses SQLite to record measurements.  `sudo apt install sqlite3` usually does the trick to install it.

### This repo

- Clone this repo to a convenient place on your Pi.  You will need to create `aredn_wardriving/conf/config.ini` and fill it in.  Start by copying `aredn_wardriving/conf/config-example.ini`.  

- Create a virtual environment for Python.  In a directory of your choice, run `python3 -m venv <envname>`, where <envname> will become the name of the directory that holds the virtual environment's files.  

- Install the project dependencies from within `aredn_wardriving/` by running `<full-path-to-venv>/bin/pip install .`

- Create the database file and table by running `create_sqlite_database.py` 
