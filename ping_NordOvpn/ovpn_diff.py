from zipfile import ZipFile
import requests
import os

OVPN_ZIP_PATH = 'D:\\Download'
OVPN1_NAME = '\\ovpn.zip'
OVPN2_NAME = '\\ovpn (1).zip'
OVPN_ZIP_URL = 'https://downloads.nordcdn.com/configs/archives/servers/ovpn.zip'

if __name__ == '__main__':
    if not (os.path.exists(OVPN_ZIP_PATH + OVPN1_NAME) or os.path.exists(OVPN_ZIP_PATH + OVPN2_NAME)):
        print('No ovpn.zip found, just download one ...')
        print('Downloading ovpn.zip ...')
        r = requests.get(OVPN_ZIP_URL, allow_redirects=True)
        open(OVPN_ZIP_PATH + OVPN1_NAME, 'wb').write(r.content)
        print('Finish downloading !')
    else:
        if os.path.exists(OVPN_ZIP_PATH + OVPN2_NAME):
            if os.path.exists(OVPN_ZIP_PATH + OVPN1_NAME):
                os.remove(OVPN_ZIP_PATH + OVPN1_NAME)
            os.rename(OVPN_ZIP_PATH + OVPN2_NAME, OVPN_ZIP_PATH + OVPN1_NAME)
        url = 'https://downloads.nordcdn.com/configs/archives/servers/ovpn.zip'
        print('Downloading ovpn.zip ...')
        r = requests.get(OVPN_ZIP_URL, allow_redirects=True)
        open(OVPN_ZIP_PATH + OVPN2_NAME, 'wb').write(r.content)
        file_list1 = []
        with ZipFile(OVPN_ZIP_PATH + OVPN1_NAME, 'r') as zf:
            for file in zf.namelist():
                if '.tcp.ovpn' in file:
                    file_list1.append(file)
        file_list2 = []
        with ZipFile(OVPN_ZIP_PATH + OVPN2_NAME, 'r') as zf:
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

        print('\nReplace old file by new one: {} -> {}'.format(OVPN_ZIP_PATH + OVPN2_NAME, OVPN_ZIP_PATH + OVPN1_NAME))
        os.remove(OVPN_ZIP_PATH + OVPN1_NAME)
        os.rename(OVPN_ZIP_PATH + OVPN2_NAME, OVPN_ZIP_PATH + OVPN1_NAME)
