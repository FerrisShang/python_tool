#! python3
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from ftplib import FTP, error_perm, error_temp
# FTP host info
ftp_host = '192.168.0.1'
ftp_port = 21
ftp_user = 'user'
ftp_pwd = 'pwd'
# Sync info
PATH_TYPE_WINDOWS = 0
PATH_TYPE_LINUX   = 1
code_list_file_path = 'code_list.txt'
local_root_folder = 'local_root_folder'
local_path_type = PATH_TYPE_WINDOWS
remote_root_folder = 'remote_root_folder'
remote_path_type = PATH_TYPE_LINUX

file_set = set()
ftp = FTP()


def path_type(path, p_type):
    if PATH_TYPE_WINDOWS == p_type:
        return path.replace('/', '\\')
    else:
        return path.replace('\\', '/')


def update_file_list(files):
    with open(code_list_file_path, 'r') as fp:
        files.clear()
        for line in fp.readlines():
            line = line.strip().replace('./', '').replace('.\\', '')
            if len(line) > 0:
                files.add(path_type(local_root_folder + line, local_path_type))
                # print(path_type(local_root_folder + line, local_path_type))
        fp.close()
    print('Sync list: %d files' % len(file_set))


class WatchHandler(FileSystemEventHandler):
    def dispatch(self, event):
        if event.event_type != 'modified' and event.event_type != 'created':
            return
        file_name = path_type(event.src_path, local_path_type)

        if code_list_file_path in file_name:
            update_file_list(file_set)
        elif file_name in file_set:
            remote_name = remote_root_folder + file_name.replace(local_root_folder, '')
            remote_name = path_type(remote_name, remote_path_type)
            for _ in range(10):
                try:
                    print('Sync(%s): %s' % (event.event_type, file_name.replace(local_root_folder, '')))
                    fn = open(file_name, 'rb')
                    ftp.storbinary('STOR %s' % remote_name, fn)
                    return
                except AttributeError as e:
                    print(e)
                    ftp.close()
                    ftp.connect(ftp_host, ftp_port)
                except error_temp as e:
                    print(e)
                    ftp.connect(ftp_host, ftp_port)
                except error_perm as e:
                    print(e)
                    ftp.login(ftp_user, ftp_pwd)
                finally:
                    fn.close()
            assert False

if __name__ == '__main__':
    local_root_folder = path_type(local_root_folder, local_path_type)
    update_file_list(file_set)
    o = Observer()
    o.schedule(WatchHandler(), path_type(local_root_folder, local_path_type), recursive=True)
    o.start()
    o.join()