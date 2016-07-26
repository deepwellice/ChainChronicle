import os

class PathFinder:

    def __init__(self):
        self.data_dir = ''
        self.unpack_dir = ''
        self.db_path = ''
        self.arukana_dir = ''
        self.arukana_history_path = ''

    def get_data_folder(self):
        if len(self.data_dir) == 0:
            script_path = os.path.abspath(__file__)
            script_dir = os.path.dirname(script_path)
            foundIndex = script_dir.find(os.sep + 'parser' + os.sep)
            self.data_dir = os.path.join(script_dir[:foundIndex], 'data')
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir, exist_ok=True)
        return self.data_dir

    def get_unpacked_data_folder(self):
        if len(self.unpack_dir) == 0:
            data_dir = self.get_data_folder()
            src_path = os.path.join(data_dir, 'unpacked', 'jp')
            self.unpack_dir = os.path.abspath(src_path)
        if not os.path.exists(self.unpack_dir):
            os.makedirs(self.unpack_dir, exist_ok=True)
        return self.unpack_dir

    def get_db_path(self):
        if len(self.db_path) == 0:
            data_dir = self.get_data_folder()
            src_path = os.path.join(data_dir, 'cc.db')
            self.db_path = os.path.abspath(src_path)
        return self.db_path

    def get_arukana_folder(self):
        if len(self.arukana_dir) == 0:
            data_dir = self.get_data_folder()
            self.arukana_dir = os.path.join(data_dir, 'arukana')
        if not os.path.exists(self.arukana_dir):
            os.makedirs(self.arukana_dir, exist_ok=True)
        return self.arukana_dir

    def get_arukana_download_history_path(self):
        if len(self.arukana_history_path) == 0:
            arukana_folder = self.get_arukana_folder()
            self.arukana_history_path = os.path.join(arukana_folder,
                                                     'arukana_history.txt')
        return self.arukana_history_path
