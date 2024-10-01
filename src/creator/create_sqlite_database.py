# Component of AREDN Survey by Bob Iannucci
#
# See LICENSE.md for license information

import sqlite3
import pathlib
import configparser
import os
import sys

projectDir = pathlib.Path(__file__).parent.parent.resolve()
sys.path.append(os.fspath(projectDir))

from debugger.debug_log import debugLog

configPath = '%s/config/config.ini' % projectDir
config = configparser.ConfigParser()
config.read(configPath)

dbPath = config['database']['databasePath']

sqlStringReadingsTable = 'CREATE TABLE "Readings" ( '\
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
 
 
sqlStringSessionsTable = 'CREATE TABLE "Sessions" ( '\
	'"Index"	INTEGER, '\
	'"Session_Name"	TEXT, '\
	'"Start_Time"	INTEGER, '\
    '"Stop_Time"	INTEGER, '\
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
create_sqlite_table(dbPath, sqlStringReadingsTable)
create_sqlite_table(dbPath, sqlStringSessionsTable)
