import requests
import subprocess
import csv
import re
import threading
import time
import base64

API_URL = "https://api.ovpn.pw/csv"
_in = input('Enter server 1 or 2: ')
if _in == '2':
    API_URL = "https://www.vpngate.net/api/iphone/"

data = requests.get(API_URL).text
if _in == '2':
    data = data[14:]
data = csv.DictReader(data.split('\n'), delimiter=',')
data_json = []


def ping(row):
    ping = subprocess.run(['ping', '-c', '1', row['IP']],
                          stdout=subprocess.PIPE)
    if ping.returncode == 0:
        ping_time = re.search(
            'time=(.+?) ms', ping.stdout.decode('utf-8')).group(1)
        data_json.append({
            'IP': row['IP'],
            'Speed': row['Speed'],
            'CountryShort': row['CountryShort'],
            'CountryLong': row['CountryLong'],
            'Ping': int(ping_time),
            'OpenVPN_ConfigData_Base64': row['OpenVPN_ConfigData_Base64']
        })


for row in data:
    try:
        threading._start_new_thread(ping, (row, ))
    except:
        pass

time.sleep(5)
data_json = sorted(data_json,  key=lambda x : x['Ping'])

print('#\tPing\tSpeed\tIP\tCountry\n--------------------------------------------')
for i in range(1, 6):
    t = data_json[i]
    f = open(t['CountryShort'] + '[{}]'.format(t['IP']) + '.ovpn', 'w+')
    f.write(base64.b64decode(t['OpenVPN_ConfigData_Base64']).decode('utf-8'))
    f.close()
    print('{}\t{}\t{} Mbps\t{}\t{}'.format(i, t['Ping'], round(int(t['Speed'])/1000/1000, 2), t['IP'], t['CountryLong']))