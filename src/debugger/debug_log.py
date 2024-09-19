import time

def debugLog(string, parameters=()):
    now = time.strftime("%H:%M:%S")
    p = (now,) + parameters
    s = "[%s] " + string
    print(s % p)