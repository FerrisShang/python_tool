from os import system as system_call
from platform import system as system_name
import subprocess
try:
    from darwin_ping import darwin_ping as ping
except:
    def ping(*args):
        pass


def cus_ping(host, c=24):
    if system_name().lower() == "windows":
        p = subprocess.Popen(["ping", "-n", c.__str__(), host], stdout=subprocess.PIPE)
    elif system_name().lower() == "darwin":
        return ping(host, count=c.__str__())
    else:
        p = subprocess.Popen(["ping", "-c", c.__str__(), host], stdout=subprocess.PIPE)
    p_bytes = str(p.communicate()[0])
    delay_list = list(str(p_bytes).split('ms'))
    if len(delay_list) > 1:
        if system_name().lower() == "windows":
            delay = delay_list[-2].split('= ')[-1]
        else:
            if '/' in delay_list[-2]:
                delay = delay_list[-2].split('/')[-3]
            else:
                delay = '8799'
    else:
        delay = '8799'
    if system_name().lower() == "windows":
        lost = list(str(p_bytes).split('%')[0].split('('))[-1]
    else:
        lost = list(str(p_bytes).split('%')[0].split(' '))[-1]
    return int(int(lost)/100*1200 + int(float(delay)))
    # return int(lost), int(float(delay))

import datetime
if __name__ == '__main__':
    while True:
        now = datetime.datetime.now()
        res = cus_ping('8.8.8.8', c=4)
        if res < 500:
            print('\r', now, res, end='')
