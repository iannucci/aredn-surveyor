# Component of aredn_wardiving by Bob Iannucci
#
# See LICENSE.md for license information

import sqlite3
import pathlib
import configparser
from src.debugger.debug_log import debugLog

thisDir = pathlib.Path(__file__).parent.resolve()
configPath = '%s/config/config.ini' % thisDir
config = configparser.ConfigParser()
config.read(configPath)

dbPath = config['database']['databasePath']

sqlString = 'CREATE TABLE "Readings" ( '\
	'"Index"	INTEGER, '\
	'"Node_Name"	TEXT, '\
	'"Node_MAC_Address"	TEXT, '\
	'"Node_Mode"	TEXT, '\
	'"SSID"	TEXT, '\
	'"SNR"	INTEGER, '\
	'"Signal"	INTEGER, '\
	'"Channel"	INTEGER, '\
	'"Receiver_Latitude"	NUMERIC, '\
	'"Receiver_Longitude"	NUMERIC, '\
	'"Time"	INTEGER, '\
	'"Receiver_Antenna"	TEXT, '\
	'"Receiver_Mounting"	TEXT, '\
	'PRIMARY KEY("Index" AUTOINCREMENT))'


def create_sqlite_database(dbFilePath):
    conn = None
    try:
        conn = sqlite3.connect(dbFilePath)
        debugLog("[create-sqlite-database] %s" % sqlite3.sqlite_version)
    except sqlite3.Error as e:
        debugLog("[create-sqlite-database] %s" % e)
    finally:
        if conn:
            conn.close()

def create_sqlite_table(dbFilePath, sqlString):
    connection_obj = sqlite3.connect(dbFilePath)
    cursor_obj = connection_obj.cursor()
    cursor_obj.execute(sqlString)
    debugLog("[create-sqlite-database] Table is Ready")
    connection_obj.close()

create_sqlite_database(dbPath)
create_sqlite_table(dbPath, sqlString)
