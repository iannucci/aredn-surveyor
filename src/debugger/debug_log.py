import time
import configparser as c
import pathlib
import sys
import os

projectDir = pathlib.Path(__file__).parent.parent.resolve()
configFilePath = '%s/config/config.ini' % projectDir
sys.path.append(os.fspath(projectDir))

config = c.ConfigParser()
config.read(configFilePath)

def debugLog(string, parameters=()):
    now = time.strftime("%H:%M:%S")
    p = (now,) + parameters
    s1 = "<%s> " + string
    s2 = s1 % p
    print(s2)
    try:
        logFilePath = config['debugLog']['logFilePath']
        with open(logFilePath, 'a') as logFile:
            logFile.write(s2)
            logFile.write('\n')
    except Exception as e:
        print("[debugLog] Failed to append message to log file: %s" % e)
        
def debugError(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
