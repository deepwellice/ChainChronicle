import os

class PathFinder:
    def __init__(self):
        self.me_path = os.path.abspath(__file__)
        self.me_dir = os.path.dirname(self.me_path)

    def get_data_folder(self):
        foundIndex = self.me_dir.find(os.sep + 'parser' + os.sep)
        data_dir = os.path.join(self.me_dir[:foundIndex], 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        return data_dir

    def get_unpacked_data_folder(self):
        data_dir = self.get_data_folder()
        src_path = os.path.join(data_dir, 'unpacked', 'jp')
        unpack_dir = os.path.abspath(src_path)
        if not os.path.exists(unpack_dir):
            os.makedirs(unpack_dir, exist_ok=True)
        return unpack_dir

    def get_db_path(self):
        data_dir = self.get_data_folder()
        src_path = os.path.join(data_dir, 'cc.db')
        db_path = os.path.abspath(src_path)
        return db_path

    def get_arukana_folder(self):
        data_dir = self.get_data_folder()
        arukana_dir = os.path.join(data_dir, 'arukana')
        if not os.path.exists(arukana_dir):
            os.makedirs(arukana_dir, exist_ok=True)
        return arukana_dir

    def get_arukana_download_history_path(self):
        arukana_folder = self.get_arukana_folder()
        arukana_history_path = os.path.join(arukana_folder,
                                            'arukana_history.txt')
        return arukana_history_path

    def get_dramas_folder(self):
        data_dir = self.get_data_folder()
        drama_dir = os.path.join(data_dir, 'dramas')
        if not os.path.exists(drama_dir):
            os.makedirs(drama_dir, exist_ok=True)
        return drama_dir

    def get_dramas_history_path(self):
        dramas_dir = self.get_dramas_folder()
        history_path = os.path.join(dramas_dir, 'dramas_history.txt')
        return history_path
