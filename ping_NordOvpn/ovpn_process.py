from cus_ping import cus_ping
import subprocess
import datetime
import getpass
import signal
import time
import os


class Ovpn:
    def __init__(self, username, password,
                 cfg_file_path='/home/user/Downloads/vpn_cfg/',
                 tmp_auth_file='/tmp/tmp-vpn-00001.tmp'):
        signal.signal(signal.SIGINT, self.kill_process)
        signal.signal(signal.SIGQUIT, self.kill_process)
        self.TOUT_SETUP = 30
        self.DELAY_KILL = 5
        self.MAX_NO_RESPONSE = 30
        self.username = username
        self.password = password
        self.tmp_auth_file = tmp_auth_file
        self.cfg_files = [cfg_file_path + name for name in os.listdir(cfg_file_path) if '.ovpn' in name]
        self.dead_server_rec = [0 for _ in self.cfg_files]
        self.dead_server_limit = 5
        self.cfg_idx = 0
        self.process_ovpn = None
        self.run()

    def kill_process(self, sig=signal.SIGINT, frame='Not Quit'):
        if (sig == signal.SIGINT or sig == signal.SIGQUIT) and self.process_ovpn is not None:
            os.kill(self.process_ovpn.pid, signal.SIGINT)
            self.process_ovpn = None
            self.cfg_idx = (self.cfg_idx + 1) % len(self.cfg_files)
        if sig == signal.SIGINT and frame != 'Not Quit':
            os._exit(0)

    def create_process(self):
        self.debug("Connecting to {}({})".format(*self.get_name_ip(self.cfg_files[self.cfg_idx])))
        self.create_auth_file()
        self.process_ovpn = subprocess.Popen([
                'openvpn',
                '--config', self.cfg_files[self.cfg_idx],
                '--auth-user-pass', self.tmp_auth_file,
                '--ping-restart', '30',
                '--ping', '2'
            ],
            stdout=subprocess.PIPE)
        time.sleep(0.1)
        self.delete_auth_file()

    def run(self):
        try:
            while True:
                self.check_server()
                self.create_process()
                if self.check_setup():
                    self.block_connectivity()
                self.kill_process(frame='Not Quit')
                time.sleep(self.DELAY_KILL)
        except Exception as e:
            self.debug(e)
        finally:
            self.kill_process()

    @staticmethod
    def get_name_ip(path):
        pos_ip_in_line = 1
        ip_mark_in_line = 'remote '
        ip = None
        try:
            with open(path, 'r')as fr:
                for line in fr.readlines():
                    if ip_mark_in_line in line:
                        items = line.replace('\n', '').split(' ')
                        ip = items[pos_ip_in_line].replace('\n', '').strip()
                        break
            fr.close()
        except FileNotFoundError:
            pass
        return os.path.basename(path).split('.')[0], ip

    def check_server(self):
        while True:
            path = self.cfg_files[self.cfg_idx]
            name, ip = self.get_name_ip(path)
            if self.dead_server_rec[self.cfg_idx] > self.dead_server_limit:
                if self.dead_server_rec[self.cfg_idx] > 30:
                    self.dead_server_rec[self.cfg_idx] = 0
                print('Skip dead server: {}({})'.format(name, ip))
            elif ip is not None and cus_ping(ip, c=2) < 5000:
                return
            else:
                print('Skip no responding server: {}({})'.format(name, ip))
            self.dead_server_rec[self.cfg_idx] += 1
            self.cfg_idx = (self.cfg_idx + 1) % len(self.cfg_files)
            time.sleep(1)

    def check_setup(self):
        for i in range(self.TOUT_SETUP * 2):
            if self.process_ovpn is not None:
                if self.is_tun_setup():
                    self.dead_server_rec[self.cfg_idx] = 0
                    self.debug('Openvpn setup success !')
                    return True
            else:
                self.debug('Process not running !')
                return False
            time.sleep(0.5)
        self.debug('Openvpn setup timeout !')
        self.dead_server_rec[self.cfg_idx] += 1
        return False

    def block_connectivity(self):
        last_time = time.time()
        while True:
            if not self.is_tun_setup():
                self.debug('Link Down !')
                return
            elif self.is_ping_ok():
                last_time = time.time()
                time.sleep(5)
            else:
                cur_time = time.time()
                if cur_time - last_time > self.MAX_NO_RESPONSE:
                    self.debug('Internet no response !')
                    return

    def create_auth_file(self):
        os.system('echo "{}\n{}" > {}'.format(self.username, self.password, self.tmp_auth_file))

    def delete_auth_file(self):
        os.system('echo "******************************" > ' + self.tmp_auth_file)

    @staticmethod
    def debug(string):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        print('\r' + now, string)
        os.system('notify-send "{}"'.format(string))

    @staticmethod
    def is_tun_setup(dev_rec_file='/proc/net/dev', dev_name='tun'):
        with open(dev_rec_file, 'r') as f:
            lines = f.readlines()
            f.close()
            for line in lines:
                if dev_name in line:
                    return True
        return False

    @staticmethod
    def is_ping_ok(max_delay=2000):
        return cus_ping('8.8.8.8', c=4) < max_delay

if __name__ == '__main__':
    if os.path.exists('pwdrec'):
        f = open('pwdrec', 'r')
        text = f.readlines()
        f.close()
        user = text[0].strip()
        pwd = text[1].strip()
        Ovpn(user, pwd)
    else:
        Ovpn(
            getpass.getpass('Input username: '),
            getpass.getpass('Input password: ')
        )
