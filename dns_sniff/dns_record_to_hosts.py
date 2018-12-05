import os
import re
import time
import subprocess
import dns.resolver
from threading import Lock
from datetime import datetime
from queue import PriorityQueue, Empty
from concurrent.futures import ThreadPoolExecutor


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


def is_fullmatch_in_list(pattern_list, string):
    for pattern in pattern_list:
        try:
            if re.fullmatch(pattern, string) is not None:
                return True
        except:
            pass
    return False


class DnsGet:
    lock = Lock()
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
        DnsGet.lock.acquire()
        for s in DnsGet.dns_server_list if dns_servers is None else dns_servers:
            try:
                resolver = dns.resolver.Resolver(configure=True)
                resolver.lifetime = 2
                resolver.nameservers = [s]
                try:
                    res_ips = resolver.query(domain, "A", raise_on_no_answer=False)
                except:
                    res_ips = []

                for res_ip in res_ips:
                    res.add(res_ip)
            except dns.exception.Timeout:
                pass
        DnsGet.lock.release()
        return res


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


class HostRecord:
    def __init__(self, filename):
        self.lock = Lock()
        self.record = {}
        with open(filename, 'r') as f:
            for item in f.readlines():
                if len(item.strip()) == 0 or item.strip()[0] == '#' or ':' in item:
                    continue
                ip, name = [s.strip() for s in item.split()]
                self.record[name] = ip
            f.close()

    def get_ip_by_name(self, name):
        self.lock.acquire()
        if name in self.record:
            res = self.record[name]
        else:
            res = None
        self.lock.release()
        return res

    def add(self, name, ip):
        self.lock.acquire()
        self.record[name] = ip
        self.lock.release()

    def items(self):
        self.lock.acquire()
        res = self.record.items()
        self.lock.release()
        return res


def get_domain_record_from_file(filename):
    res = []
    if os.path.exists(filename):
        with open(filename, 'r') as f_dns:
            for line in f_dns.readlines():
                c, t, n = [s.strip() for s in line.split('|')]
                res.append(DomainRec(n, c, t))
            f_dns.close()
    return res


def ping_ip_cb(q, ip):
    q.put((cus_ping(ip), ip))


def find_best_ip(hosts, domain, blk_list, idx, total):
    assert(isinstance(hosts, HostRecord))
    assert(isinstance(domain, DomainRec))
    if not is_fullmatch_in_list(blk_list, domain.name):
        ip = hosts.get_ip_by_name(domain.name)
        if ip == '127.0.0.1' or (ip is not None and cus_ping(ip) < 1500):
            print('({}/{}: {}  {}'.format(idx.count(), total, domain.name, ip))
            return
        ips = DnsGet.ip_get(domain.name)
        q = PriorityQueue()
        with ThreadPoolExecutor(10) as exec:
            for ip in ips:
                exec.submit(ping_ip_cb, q, str(ip))
        try:
            item = q.get(block=False)
            if item[0] < 1500:
                hosts.add(domain.name, item[1])
                print('({}/{}: {}  {} ({})'.format(idx.count(), total, domain.name, item[1], item[0]))
                return
        except Empty:
            pass
    else:
        hosts.add(domain.name, '127.0.0.1')
        print('({}/{}: {}  (In Black List)'.format(idx.count(), total, domain.name))
        return
    if hosts.get_ip_by_name(domain.name) is None:
        hosts.add(domain.name, '127.0.0.1')
    print('({}/{}: {}  No available in {} IPs'.format(idx.count(), total, domain.name, len(ips)))


class ThreadIdx:
    def __init__(self):
        self.lock = Lock()
        self.i = 1

    def count(self):
        self.lock.acquire()
        res = self.i
        self.i += 1
        self.lock.release()
        return res


DNS_CACHE_FILE_NAME = 'dns_query_rec.txt'
BLK_FILE_NAME = 'blk_domain.list'
HOST_FILE_NAME = '/etc/hosts'
blk_list = []
domain_record = get_domain_record_from_file(DNS_CACHE_FILE_NAME)
hosts_record = HostRecord(HOST_FILE_NAME)
if os.path.exists(BLK_FILE_NAME):
    with open(BLK_FILE_NAME, 'r') as f:
        blk_list = [s.strip() for s in f.readlines()]
        f.close()
with ThreadPoolExecutor(50) as executor:
    thead_idx = ThreadIdx()
    for i in range(len(domain_record)):
        executor.submit(find_best_ip, hosts_record, domain_record[i], blk_list, thead_idx, len(domain_record))

with open('hosts', 'w') as f:
    for k, v in hosts_record.items():
        f.write('{}\t{}\n'.format(v, k))
    f.close()
