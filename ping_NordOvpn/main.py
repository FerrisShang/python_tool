import shutil
import os
import queue
from threading import Thread, Lock
from cus_ping import *
from zipfile import ZipFile

OVPN_ZIP_PATH = 'D:\\Download'
OVPN_TMP_FORDER = OVPN_ZIP_PATH + '\\.nord.tmp'


def unzip_ovpn_zip(zip_path, tmp_folder, q_filelist = None):
    if not q_filelist:
        assert(isinstance(q_filelist, queue.Queue))
    with ZipFile(zip_path + '\\ovpn.zip', 'r') as zf:
        file_list = []
        for file in zf.namelist():
            if '.tcp.ovpn' in file:
                file_list.append(file)
        if False:
            if q_filelist:
                q_filelist.put(10)
            for i in range(10):
                zf.extract(file_list[i], tmp_folder)
                if q_filelist:
                    q_filelist.put(ServerInfo(tmp_folder + '\\' + file_list[i]))
        else:
            if q_filelist:
                q_filelist.put(len(file_list))
            for file in file_list:
                zf.extract(file, tmp_folder)
                if q_filelist:
                    q_filelist.put(ServerInfo(tmp_folder + '\\' + file))
        zf.close()


def get_ip_from_ovpn(path):
    POS_IP = 1
    IP_MARK = 'remote '
    fr = open(path, 'r')
    for line in fr.readlines():
        if IP_MARK in line:
            items = line.replace("\n", "").split(' ')
            return items[POS_IP].replace("\n", "").strip()
    fr.close()


class ServerInfo:
    def __init__(self, path, ip=None, delay=None):
        self.path = path
        self.name = os.path.basename(path)
        self.ip = ip
        self.delay = delay

    def __str__(self):
        return 'Delay:{}, Name:{}, IP:{}'.format(self.delay, self.name, self.ip)


class ParseOvpn(Thread):
    def __init__(self, q_ovpn, q_server):
        assert(isinstance(q_ovpn, queue.Queue))
        assert(isinstance(q_server, queue.Queue))
        Thread.__init__(self)
        self.q_server = q_server
        self.q_ovpn = q_ovpn
        try:
            self.total_num = q_ovpn.get(True, timeout=0.3)
            self.q_server.put(self.total_num)
        except queue.Empty:
            return
        self.start()

    def run(self):
        for _ in range(self.total_num):
            try:
                s_info = self.q_ovpn.get(True, timeout=0.3)
                assert(isinstance(s_info, ServerInfo))
                ip_str = get_ip_from_ovpn(s_info.path)
                s_info.ip = ip_str
                self.q_server.put(s_info)
            except queue.Empty:
                break
        shutil.rmtree(OVPN_TMP_FORDER)


class PingServer(Thread):
    def __init__(self,q_server, delay_list):
        assert(isinstance(q_server, queue.Queue))
        assert(isinstance(delay_list, list))
        Thread.__init__(self)
        self.data_lock = Lock()
        self.processed_num = 0
        self.q_server = q_server
        self.delay_list = delay_list
        try:
            self.total_num = self.q_server.get(True, timeout=0.3)
        except queue.Empty:
            return
        self.start()

    def inc_processed_num(self):
        self.data_lock.acquire()
        self.processed_num += 1
        res = self.processed_num
        self.data_lock.release()
        return res

    def get_processed_num(self):
        self.data_lock.acquire()
        res = self.processed_num
        self.data_lock.release()
        return res

    def th_ping_server(self):
        while True:
            try:
                s_info = self.q_server.get(True, timeout=0.1)
                assert(isinstance(s_info, ServerInfo))
                s_info.delay = cus_ping(s_info.ip)
                num = self.inc_processed_num()
                print('{}/{}: {}'.format(num, self.total_num, str(s_info)))
                self.delay_list.append((s_info.delay, s_info.name, s_info.ip, s_info.path))
            except queue.Empty:
                if self.get_processed_num() == self.total_num:
                    return

    def run(self):
        thread_num = 200
        thread_pool = []
        for _ in range(0, thread_num):
            th = Thread(target=self.th_ping_server)
            thread_pool.append(th)
            th.start()
        for idx_th in range(0, thread_num):
            th = thread_pool[idx_th]
            th.join()


if __name__ == '__main__':
    delay_list = []
    q_file = queue.Queue()
    q_server_info = queue.Queue()
    Thread(target=unzip_ovpn_zip, args=(OVPN_ZIP_PATH, OVPN_TMP_FORDER, q_file)).start()
    ParseOvpn(q_file, q_server_info)
    th = PingServer(q_server_info, delay_list)
    th.join()
    print('================================')
    delay_list.sort()
    for x in delay_list[0:10]:
        print(x)
