import os
import shutil
import requests
import re
from queue import Queue, Empty

CODE_PATH = '../ping_NordOvpn/'
UNZIP_FILENAME = 'zipfile.py'
SCAPY_GET_PATH = 'https://github.com/secdev/scapy/archive/v2.4.0.zip'
DNSPY_GET_PATH = 'https://github.com/rthalley/dnspython/archive/master.zip'
SCAPY_FILENAME = 'scapy.zip'
DNSPY_FILENAME = 'dnspython.zip'

def cus_ping(host):
    p = subprocess.Popen(["ping", "-c", "4", host], stdout=subprocess.PIPE)
    p_bytes = str(p.communicate()[0])
    delay_list = list(str(p_bytes).split('ms'))
    if len(delay_list) > 1:
        if '/' in delay_list[-2]:
            delay = delay_list[-2].split('/')[-3]
        else:
            delay = '8799'
    else:
        delay = '8799'
    lost = list(str(p_bytes).split('%')[0].split(' '))[-1]
    return int(int(lost)/100*1200 + int(float(delay)))

def check_file(code_path, filename):
    if not os.path.exists(filename):
        if os.path.exists(code_path + filename):
            shutil.copyfile(code_path + filename, filename)
        else:
            print('Code missing!')
            os._exit(0)

def check_zip(download_path, filename):
    if not os.path.exists(filename):
        print('Downloading', filename)
        r = requests.get(download_path, allow_redirects=True)
        open(filename, 'wb').write(r.content)

check_file(CODE_PATH, UNZIP_FILENAME)
check_zip(SCAPY_GET_PATH, SCAPY_FILENAME)
check_zip(DNSPY_GET_PATH, DNSPY_FILENAME)

from zipfile import ZipFile

def unzip_packet(zip_name, folder_name):
    if not os.path.exists('./' + folder_name):
        del_folder_name = None
        with ZipFile(zip_name, 'r') as zf:
            for file in zf.namelist():
                if '/'+folder_name+'/' in file:
                    zf.extract(file, './')
                    del_folder_name = str(file).split('/')[0]
        try:
            shutil.move(del_folder_name+'/'+folder_name+'/', './')
        except:
            pass
        try:
            shutil.rmtree(del_folder_name)
        except:
            pass

unzip_packet(DNSPY_FILENAME, 'dns')
unzip_packet(SCAPY_FILENAME, 'scapy')
import dns.resolver

class DnsGet:
    dns_server_list = [
        '103.86.96.100',
        '103.86.99.100',
        '156.154.70.1',
        '156.154.71.1',
        '4.2.2.1',
        '4.2.2.2',
    ]

    @staticmethod
    def ip_get(domain, dns_servers=None):
        res = set()
        for s in DnsGet.dns_server_list if dns_servers is None else dns_servers:
            try:
                resolver = dns.resolver.Resolver(configure=True)
                resolver.lifetime = 1
                resolver.nameservers = [s]
                res_ips = resolver.query(domain, "A", raise_on_no_answer=False)
                for res_ip in res_ips:
                    res.add(res_ip)
            except dns.exception.Timeout:
                pass
        return res

from scapy.all import *

def dns_record_cb(pkt):
    try:
        if 'IP' in pkt and pkt.haslayer('DNS') and pkt.getlayer('DNS').qr == 0:
            name = str(pkt.getlayer('DNS').qd.qname)[2:-2]
            q.put(name)
    except Exception as err:
        print(err)

def dns_sniff(interface, callback):
    while True:
        if interface in os.listdir('/sys/class/net/'):
            try:
                filter_bpf = 'udp and port 53'
                sniff(filter=filter_bpf, store=0,  prn=callback, iface=interface)
            except OSError or RuntimeError as err:
                print(err)
        else:
            time.sleep(3)

class DomainRec:
    def __init__(self, name, count=1, visit_time=None):
        self.name = name
        self.visit_time = \
            datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S') \
            if visit_time is None else visit_time
        self.visit_count = int(count)

    def update(self, visit_time=None):
        self.visit_count += 1
        self.visit_time = \
            datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S') \
            if visit_time is None else visit_time

def save_rec_to_file(record, file_name):
    try:
        shutil.move(file_name, file_name+'.bk')
    except:
        pass
    with open(file_name, 'w', encoding='utf-8') as f:
        vv = [v for k, v in record.items()]
        vv.sort(key=lambda d: d.visit_count, reverse=True)
        for v in vv:
            f.write('{:5} | {} | {}\n'.format(v.visit_count, v.visit_time, v.name))
        f.close()
        print('file {} recorded.'.format(file_name))

def is_fullmatch_in_list(pattern_list, string):
    for pattern in pattern_list:
        try:
            if re.fullmatch(pattern, string) is not None:
                return True
        except:
            pass
    return False

def callback(name_queue, file_name, name_rec=None, ign_list=None):
    assert(isinstance(name_queue, Queue))
    record_timer_cnt = 0
    name_rec = {} if name_rec is None else name_rec
    record_flag = False
    while True:
        try:
            name = name_queue.get(timeout=20)
            if ign_list is None or not is_fullmatch_in_list(ign_list, name):
                if name not in name_rec:
                    name_rec[name] = DomainRec(name)
                else:
                    name_rec[name].update()
                record_flag = True
                print('{:5} | {} | {}'.format(name_rec[name].visit_count, name_rec[name].visit_time, name))
        except Empty:
            pass
        record_timer_cnt += 1
        if record_timer_cnt >= 60:
            if record_flag:
                record_timer_cnt = 0
                save_rec_to_file(name_rec, file_name)
                record_flag = False

if __name__ == '__main__':
    q = Queue()
    DNS_CACHE_FILE_NAME = 'dns_query_rec.txt'
    IGN_FILE_NAME = 'ign_domain.list'
    name_record = {}
    ign_list = []
    if os.path.exists(DNS_CACHE_FILE_NAME):
        with open(DNS_CACHE_FILE_NAME, 'r') as f_dns:
            for line in f_dns.readlines():
                c, t, n = [s.strip() for s in line.split('|')]
                print('Load {}  {}  {}'.format(c, t, n))
                name_record[n] = DomainRec(n, c, t)
            f_dns.close()
    if os.path.exists(IGN_FILE_NAME):
        with open(IGN_FILE_NAME, 'r') as f_ign:
            ign_list = [s.strip() for s in f_ign.readlines()]
            f_ign.close()
    Thread(target=callback, args=[q, DNS_CACHE_FILE_NAME, name_record, ign_list]).start()
    Thread(target=dns_sniff, args=['tun0', dns_record_cb]).start()
    Thread(target=dns_sniff, args=['wlp5s0', dns_record_cb]).start()
    Thread(target=dns_sniff, args=['wlp4s0', dns_record_cb]).start()
