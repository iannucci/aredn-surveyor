import requests
import pandas as pd
from bs4 import BeautifulSoup

nodeIP = '10.5.222.97'
username = "root"
password = "SurSocNet99"

def fetch_wifi_survey(host):
    '''
    Accesses the node's WiFI survey page, scrapes it, and
    returns a dictionary of the surveyed stations
    '''
    url = 'http://%s/cgi-bin/scan' % (host,)
    html = requests.get(url, auth=(username, password))
    soup = BeautifulSoup(html.text, 'html.parser')
    tables = pd.read_html(str(soup))
    table = tables[0]
    print(table)

fetch_wifi_survey(nodeIP)
