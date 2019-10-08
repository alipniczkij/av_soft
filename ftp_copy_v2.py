import ftplib
import json
from pathlib import Path
from multiprocessing import Pool


class Copier:

    def __init__(self, files):
        self.file_path, self.path_to = files

    def log(self, data):
        try:
            ftp = ftplib.FTP()  # Установка соединения с FTP сервером
            ftp.connect(data['host'], int(data['port']))
            ftp.login(data['username'], data['password'])
        except ftplib.error_perm:
            print('FTP error')
        else:
            return ftp

    def upload_file(self, data):
        ftp = self.log(data)
        filename = Path(self.file_path).name
        try:
            ftp.cwd(self.path_to)
        except ftplib.all_errors:  # Заходим в папку на сервере, в которую надо скопировать файл
            ftp.mkd(self.path_to)  # Если папки такой нет, создаем
            ftp.cwd(self.path_to)
        try:
            with open(self.file_path, 'rb') as f:
                ftp.storbinary('STOR ' + filename, f)
        except FileNotFoundError:
            print('File not found', self.file_path)
        except ftplib.error_perm:
            print('File was not uploaded', self.file_path)
        else:
            print('File was uploaded', self.file_path)


class ProcessFTP:  # Нужно, чтобы каждый процесс создавал свое собственное подключение к серверу

    def __init__(self, json_name):
        self.data = None
        self.PROCESSES_COUNT = 5
        self.read_json(json_name)

    def read_json(self, file_name):
        try:
            with open(file_name, 'r') as f:  # считываем данные из json
                self.data = json.load(f)
        except IsADirectoryError:
            print('It is a directory')
        except FileNotFoundError:
            print('File not found')
        except OSError as err:
            print(f'System error:\n{err}')

    def copy(self, files):
        Copier(files).upload_file(self.data["ftp"])

    def processing(self):
        pool = Pool(self.PROCESSES_COUNT)  # Создаем процессы и с помощью метода map
        pool.map(self.copy, self.data['files'])  # закидываем каждому процессу свой файл, который ему нужно скопировать


if __name__ == '__main__':
    json_file = input('Enter json file name or exit: ')  # Пишем как называется конфигурационный файл
    if json_file == 'exit' or json_file == '':
        exit()
    copy = ProcessFTP(json_file)
    copy.processing()
