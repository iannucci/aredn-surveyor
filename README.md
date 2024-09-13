# AREDN Wardriving

A set of tools for collecting AREDN signal strength data, geo-referencing it, and displaying the data on a map.  This code was initially developed to run on a Mac, but it is being maintained to run on a Raspberry Pi (tested on a Pi 3 running 64 bit Raspberry Pi OS).

## Hardware Configuration

You will need
- the Raspberry Pi -- a 3B+ is a good choice.  Pi 4 is overkill.  Pi 5 is way overkill.
- a GPS receiver
- an AREDN node
- an ethernet hub

If you are actually doing data collection from a vehicle, a convenient setup is to use a 12v powered PoE hub which, in turn, can power the other devices -- you will need a PoE HAT for your Pi.  Waveshare makes a nice, small HAT that works well on the Pi 3B+ (won't work on a 3B!). 

A HiLetgo VK172 USB GPS/GLONASS USB GPS Receiver (available through Amazon and others) should be plugged into an available USB port.  The receiver needs a clear sky view, and a USB extension cable may be needed.  The baud rate you will need to set in the config file will be `115200`.  Check `/dev` to find the port.  `/dev/ttyACM0` is typical.  Make a note of it.

An AREDN node with an honest-to-goodness omnidirectional antenna is needed.  Any directional antenna will render your readings nonsensical.  Ubiquiti makes a great 10 dBi omni that works well with the Rocket 5AC (assuming you will be surveying 5 GHz AREDN nodes).  Be aware that a high-gain omni antenna achieves its gain by having a narrow vertical beamwidth.  If you are surveying hilly terrain, you would do well to use a **lower** gain omni that has a broader vertical pattern.

## Software Installation

### Database

The code uses SQLite to record measurements.  `sudo apt install sqlite3` usually does the trick to install it.

### This Repo

- Clone this repo to a convenient place on your Pi.  You will need to create `aredn_wardriving/conf/config.ini` and fill it in.  Start by copying `aredn_wardriving/conf/config-example.ini`.  

- Create a virtual environment for Python.  In a directory of your choice, run `python3 -m venv <envname>`, where <envname> will become the name of the directory that holds the virtual environment's files.  

- Install the project dependencies from within `aredn_wardriving/` by running `<full-path-to-venv>/bin/pip install .`

- Create the database file and table by running `create_sqlite_database.py` 
