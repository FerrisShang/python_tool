from platform import system as system_name
from zipfile import ZipFile
import requests
import os

OVPN_ZIP_PATH = '.'
OVPN1_NAME = '/ovpn.zip'
OVPN2_NAME = '/ovpn (1).zip'

OVPN_ZIP_URL = 'https://downloads.nordcdn.com/configs/archives/servers/ovpn.zip'


def p(path):
    return os.path.relpath(path)


def download(url, filename, size):
    response = requests.get(url, stream=True)
    total = response.headers.get('content-length')

    if total is None:
        with open(filename, 'wb') as f:
            f.write(response.content)
            f.close()
    else:
        downloaded = 0
        total = int(total)
        if total == size:
            print("Same size, exit...")
            exit(0)
        data = []
        for d in response.iter_content(chunk_size=max(int(total/1000), 1024*128)):
            downloaded += len(d)
            data.append(d)
            print("\rDownloading: %.2f/%.2f" % (downloaded/1024/1024,total/1024/1024), end='')
        print("")
        with open(filename, 'wb') as f:
            for d in data:
                f.write(d)
            f.close()


if __name__ == '__main__':
    if not (os.path.exists(p(OVPN_ZIP_PATH + OVPN1_NAME)) or os.path.exists(p(OVPN_ZIP_PATH + OVPN2_NAME))):
        print('No ovpn.zip found, just download one ...')
        print('Downloading ovpn.zip ...')
        download(OVPN_ZIP_URL, p(OVPN_ZIP_PATH + OVPN1_NAME), 0)
    else:
        if os.path.exists(p(OVPN_ZIP_PATH + OVPN2_NAME)) and \
                os.stat(p(OVPN_ZIP_PATH + OVPN2_NAME)).st_size > 10 << 10:
            if os.path.exists(p(OVPN_ZIP_PATH + OVPN1_NAME)):
                os.remove(p(OVPN_ZIP_PATH + OVPN1_NAME))
            os.rename(p(OVPN_ZIP_PATH + OVPN2_NAME), p(OVPN_ZIP_PATH + OVPN1_NAME))
        print('Downloading ovpn.zip ...')
        download(OVPN_ZIP_URL, p(OVPN_ZIP_PATH + OVPN2_NAME), os.path.getsize(p(OVPN_ZIP_PATH + OVPN1_NAME)))
        file_list1 = []
        with ZipFile(p(OVPN_ZIP_PATH + OVPN1_NAME), 'r') as zf:
            for file in zf.namelist():
                if '.tcp.ovpn' in file:
                    file_list1.append(file)
        file_list2 = []
        with ZipFile(p(OVPN_ZIP_PATH + OVPN2_NAME), 'r') as zf:
            for file in zf.namelist():
                if '.tcp.ovpn' in file:
                    file_list2.append(file)
        diff1 = [i for i in set(file_list1) - set(file_list2)]
        diff1.sort()
        if len(diff1) > 0:
            print('\n\tD  {}'.format('\n\tD  '.join([str(s) for s in diff1])))
        diff2 = [i for i in set(file_list2) - set(file_list1)]
        diff2.sort()
        if len(diff2) > 0:
            print('\n\tA  {}'.format('\n\tA  '.join([str(s) for s in diff2])))

        if len(diff1) > 0:
            print('{} server(s) deleted.'.format(len(diff1)))
        else:
            print('Nothing removed')
        if len(diff2) > 0:
            print('{} server(s) added.'.format(len(diff2)))
        else:
            print('Nothing added')

        print('\nReplace old file by new one: {} -> {}'.format(p(OVPN_ZIP_PATH + OVPN2_NAME), p(OVPN_ZIP_PATH + OVPN1_NAME)))
        os.remove(p(OVPN_ZIP_PATH + OVPN1_NAME))
        os.rename(p(OVPN_ZIP_PATH + OVPN2_NAME), p(OVPN_ZIP_PATH + OVPN1_NAME))
