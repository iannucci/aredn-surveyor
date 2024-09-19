# AREDN Wardriving

A set of tools for collecting AREDN signal strength data, geo-referencing it, and displaying the data on a map.  This code was initially developed to run on a Mac, but it is being maintained to run on a Raspberry Pi (tested on a Pi 3 running 64 bit Raspberry Pi OS).

## Hardware Configuration

You will need
- the Raspberry Pi -- this has been tested with a Pi5.  A Pi 3B+ was found to be too slow to support remote debugging via VSCode.  YMMV.
- a GPS receiver
- an AREDN node
- an ethernet hub

If you are actually doing data collection from a vehicle, a convenient setup is to use a 12v powered PoE switch which, in turn, can power the other devices -- you will need a PoE HAT for your Pi.  Waveshare makes a nice, small HAT that works well on the Pi 3B+ (it **will not** work on a plain old 3B).  PoE HATs are specific to various Pi models.  Caveat emptor.

Pay attention to the PoE requirements of your devices and the ethernet switch you select.  Ubiquiti devices typically used for AREDN (e.g., the Rocket 5AC Lite) need passive PoE (24V, pins 4,5 positive; 7,8 negative).  The Raspberry PI PoE HATs typically use 802.3af (48V, 15W).  But beware.  There are two flavors of 802.3af -- Mode A (2 pair -- pins 1,2 positive; 3,6 negative with data and power sharing the same wires) and Mode B (4 pair -- data runs separately over pins 4,5,7,8).  The Waveshare device I used is Type A, and the switch needs to provide Type A power (not all do).  Also, some PoE switches provide 802.3af/at but **do not** support passive PoE.  Ubiquiti sells an 802.3af-to-PoE converter to solve that problem.  Be careful not to plug an 802.3af/at device into a switch port that is sourcing passive PoE.  You will probably let out magic blue smoke if you do.  

A HiLetgo VK172 USB GPS/GLONASS USB GPS Receiver (available through Amazon and others) should be plugged into an available USB port.  The receiver needs a clear sky view, and a USB extension cable may be needed.  The baud rate you will need to set in the config file will be `115200`.  Check `/dev` to find the port.  `/dev/ttyACM0` is typical.  Make a note of it.

An AREDN node with an honest-to-goodness omnidirectional antenna is needed.  Any directional antenna will render your readings nonsensical.  Ubiquiti makes a great 10 dBi omni that works well with the Rocket 5AC Lite(assuming you will be surveying 5 GHz AREDN nodes).  Be aware that a high-gain omni antenna achieves its gain by having a narrow vertical beamwidth.  If you are surveying hilly terrain, you would do well to use a **lower** gain omni that has a broader vertical pattern.

## Software Installation

### Database

The code uses SQLite to record measurements.  `sudo apt install sqlite3` usually does the trick to install it.

### This Repo

- Clone this repo to a convenient place on your Pi.  You will need to create `config/config.ini` and fill it in.  Start by copying `config/config-example.ini`.  

- Initialize the Python VSCode extension for this cloned folder.

- Install Conda.  Go to the [Anaconda archive](https://repo.anaconda.com/archive/) and find the most recent Linux-aarch64.sh link and copy it.  ssh to your Pi and `curl -O` that link.  Once this file is downloaded, run `bash <filename>` to install it.  It will take 10-15 minutes.

- If you have a Remote session already running in VSCode that is attached to your Pi, either restart the session or restart VSCode so that the Conda installation will be recognized.

- Create a virtual environment for Python.  Use the VSCode 'Create Environment' command and select Conda.  This will result in a `.conda` folder being created in the project folder. 

- Install the project dependencies from within the `src/` subdirectory by running `pip install .`

- In VSCode, open `create_sqlite_database.py` and run it.

- The user-id that will be running this code needs to be added to the dialout group to access the serial port: `sudo adduser <user-id> dialout`

- Install the SQLite Viewer in VSCode.  In the file explorer of VSCode, click on the database file.  You should see a table called `Readings` and by opening this, you should see the field names (e.g. Node_Name, Node_MAC_Address, ...)

- In VSCode, create a debug configuration for the module.

- Launch the module debugger.  This should bring up a pop-up in VSCode that provides access to the web UI (map).  With no readings in the database, the map will remain blank.  Once readings are recorded, the map will appear, centered on the readings.
