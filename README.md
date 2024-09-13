# AREDN Wardriving

A set of tools for collecting AREDN signal strength data, geo-referencing it, and displaying the data on a map.

To install from the top level of the project directory:
  
- Create aredn_wardriving/conf/config.ini and fill in the parameters
- $ sudo apt install sqlite3
- Copy config-example.ini to config.ini in the conf directory.
- Run create_sqlite_database.py to create the database and table.
- $ python3 -m venv python-environment
- $ cd aredn-wardriving
- $ ../python-environment/bin/pip install .