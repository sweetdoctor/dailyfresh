from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client

class FdfsStorage(Storage):
    def __init__(self, client_conf=None, tracker_server=None):
        # if client_conf == None:
        #     client_conf = FDFS_CLIENT
        self.client_conf = './utils/fdfs/fdfs_client.conf'
        # self.client_conf = client_conf
        # if tracker_server == None:
        #     # tracker_server = 'http://192.168.28.129:8889/'
        #     tracker_server = TRACKER_SERVER
        self.tracker_server = 'http://192.168.28.129:8889/'

    def _open(self, name, mode='rb'):
        """
        Retrieves the specified file from storage.
        """
        pass

    def _save(self, name, content):

        f_client = Fdfs_client(self.client_conf)
        res = f_client.upload_by_buffer(content.read())
        # res 返回值
        # dict
        # {
        #     'Group name': group_name,
        #     'Remote file_id': remote_file_id,
        #     'Status': 'Upload successed.',
        #     'Local file name': '',
        #     'Uploaded size': upload_size,
        #     'Storage IP': storage_ip
        # }
        if res.get('Status') != 'Upload successed.':
            raise Exception('上传失败')
        filename = res.get('Remote file_id')
        print(filename)
        return self.tracker_server + filename.replace('\\', '/')

    def exists(self, name):
        return False

    def url(self, name):
        return name
