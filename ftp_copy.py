import ftplib
import json
import threading
from queue import Queue


class Copier:

    def __init__(self, json_name):
        self.file_name = json_name
        self.data = None
        self.q = Queue()
        self.read_json()

    def log(self):
        try:
            ftp = ftplib.FTP()  # Установка соединения с FTP сервером
            ftp.connect(self.data['host'], int(self.data['port']))
            ftp.login(self.data['username'], self.data['password'])
        except ftplib.error_perm:
            print('FTP error')
        else:
            return ftp

    def read_json(self):
        try:
            with open(self.file_name, 'r') as f:  # Для каждого потока считываем свои данные из json
                self.data = json.load(f)
                for file in self.data['file_to_copy']:  # Заполняем очередь файлами, которые необходимо скопировать
                    self.q.put(file)
        except IsADirectoryError:
            print('It is a directory')
        except FileNotFoundError:
            print('File not found')
        except OSError as err:
            print(f'System error:\n{err}')

    def threading_files(self):
        ftp = self.log()
        for _ in range(len(self.data['file_to_copy'])):
            threading.Thread(target=self.file_upload(ftp)).start()  # Запускаем столько потоков, сколько файлов нам
            # нужно скопировать

    def file_upload(self, ftp):  # Заходим в папку, которая нужна и отсылаем в нее файл в бинарном виде
        while True:
            if self.q.empty():  # Если очередь пустая заканчиваем работу
                break
            file = self.q.get()  # Достаем название файла из очереди
            try:
                ftp.cwd(self.data['path_to'])
            except ftplib.all_errors:  # Заходим в папку на сервере, в которую надо скопировать файл
                ftp.mkd(self.data['path_to'])  # Если папки такой нет, создаем
                ftp.cwd(self.data['path_to'])
            try:
                with open(self.data['path_from'] + file, 'rb') as f:
                    ftp.storbinary('STOR ' + file, f)
            except FileNotFoundError:
                print('File not found', file)
            except ftplib.error_perm:
                print('File was not uploaded', file)
            else:
                print('File was uploaded', file)
                self.q.task_done()
        ftp.close()


if __name__ == '__main__':
    json_file = input('Enter json file name or exit: ')  # Пишем как называется конфигурационный файл
    if json_file == 'exit' or json_file == '':
        exit()
    copy = Copier(json_file)
    copy.threading_files()
