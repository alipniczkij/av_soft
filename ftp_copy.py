import ftplib
import json
import threading
from time import sleep


class CopierError(Exception):
    pass


class Copier:

    def __init__(self, json_name):
        self.file_name = json_name
        self.data = None
        self.read_json()
        try:
            self.ftp = ftplib.FTP()
            self.ftp.connect(self.data['host'], int(self.data['port']))
            self.ftp.login(self.data['username'], self.data['password'])
        except Exception as err:
            raise CopierError(f'error create connection. {err}')
        self.file_upload()

    def read_json(self):
        try:
            with open(self.file_name, 'r') as f:
                self.data = json.load(f)
        except Exception as err:
            raise CopierError(f'error read json. {err}')

    def file_upload(self):
        try:
            self.ftp.cwd(self.data['path_to'])
            with open(self.data['path_from'] + self.data['file_to_copy'], 'rb') as f:
                self.ftp.storbinary('STOR ' + self.data['file_to_copy'], f)
        except Exception as err:
            raise CopierError(f'error with uploading. {err}')
        else:
            sleep(10)
            print('File was uploaded', self.data['file_to_copy'])
            self.ftp.close()


if __name__ == '__main__':
    while True:
        json_file = input('Enter json file name or exit: ')
        if json_file == 'exit':
            break
        thr = threading.Thread(target=Copier, args=(json_file,))
        thr.start()
