from zipfile import ZipFile

OVPN_ZIP_PATH = 'D:\\Download'
OVPN1_NAME = '\\ovpn.zip'
OVPN2_NAME = '\\ovpn (1).zip'

if __name__ == '__main__':
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
        print('{} server(s) deleted: \n\tD  {}'.format(len(diff1), '\n\tD  '.join([str(s) for s in diff1])))
    else:
        print('Nothing removed')
    diff2 = [i for i in set(file_list2) - set(file_list1)]
    diff2.sort()
    if len(diff2) > 0:
        print('{} server(s) added: \n\tA  {}'.format(len(diff2), '\n\tA  '.join([str(s) for s in diff2])))
    else:
        print('Nothing added')
