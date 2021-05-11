import requests
import os
import sys


__all__ = [
    'get',
]
FILE_PATH = './'


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
            return False
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
    return True


def get(url):
    file_url = url
    file_name1 = os.path.basename(file_url)
    file_name2 = file_name1 + '.tmp'
    if not (os.path.exists(p(FILE_PATH + file_name1))):
        print('No file found, just download one ...')
        print('Downloading \'%s\'...' % file_name1)
        download(file_url, p(FILE_PATH + file_name1), 0)
    else:
        print('Downloading \'%s\'...' % file_name1)
        if download(file_url, p(FILE_PATH + file_name2), os.path.getsize(p(FILE_PATH + file_name1))) is False:
            return
        print('\nReplace old file by new one: {} -> {}'.format(p(FILE_PATH + file_name2), p(FILE_PATH + file_name1)))
        os.remove(p(FILE_PATH + file_name1))
        os.rename(p(FILE_PATH + file_name2), p(FILE_PATH + file_name1))


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('Usage: %s URL')
        exit(-1)
    get(url=sys.argv[1])
