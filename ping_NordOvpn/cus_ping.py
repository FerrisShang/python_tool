from os import system as system_call
from platform import system as system_name
import subprocess


def cus_ping(host):
    if system_name().lower() == "windows":
        p = subprocess.Popen(["ping", "-n", "48", host], stdout=subprocess.PIPE)
    else:
        p = subprocess.Popen(["ping", "-c", "48", host], stdout=subprocess.PIPE)
    p_bytes = str(p.communicate()[0])
    delay_list = list(str(p_bytes).split('ms'))
    if len(delay_list) > 1:
        if system_name().lower() == "windows":
            delay = delay_list[-2].split('= ')[-1]
        else:
            if '/' in delay_list[-2]:
                delay = delay_list[-2].split('/')[-1]
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
