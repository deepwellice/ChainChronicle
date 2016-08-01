import os
import json
from datetime import datetime

import common
from paths import PathFinder

class DramaParser():
    def __init__(self):
        path_finder = PathFinder()
        unpack_data_folder = path_finder.get_unpacked_data_folder()
        self.drama_file = os.path.join(unpack_data_folder, 'drama_jp.json')
        self.dramas_folder = path_finder.get_dramas_folder()
        self.token = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        self.history_path = path_finder.get_dramas_history_path()
        self.history_json = None

    def __get_drama_dict(self):
        with open(self.drama_file, 'tr', encoding='utf-8') as drama_fobj:
            dramas_content = drama_fobj.read()
        dramas_content = dramas_content.replace('\n', '')
        dramas_dict = json.loads(dramas_content)
        if type(dramas_dict) is not dict:
            common.exit_if_wrong_json_format()
        return dramas_dict

    def __save(self, drama_id, drama_content):
        for chapter_content in drama_content:
            chapter_id = chapter_content.get('chapter')
            chapter_path = os.path.join(self.dramas_folder, drama_id,
                                        'chapter{0}'.format(chapter_id))
            if not os.path.exists(chapter_path):
                os.makedirs(chapter_path, exist_ok = True)
            for item in ['opening', 'ending']:
                item_content = chapter_content.get(item)
                if item_content is None:
                    continue
                item_path = os.path.join(chapter_path, item + '.txt')
                if os.path.exists(item_path):
                    continue
                with open(item_path, 'wt', encoding='utf-8') as item_fobj:
                    for item_script in item_content:
                        item_fobj.write(item_script + '\r')
                    self.__log_history('{0}-{1}-{2}'.format(
                                            drama_id, chapter_id, item))

    def __init_history(self):
        if os.path.exists(self.history_path):
            return
        with open(self.history_path, 'wt', encoding='utf-8') as history_fd:
            json.dump({self.token: []}, history_fd)

    def __log_history(self, drama_name):
        self.__init_history()
        if (self.history_json is None):
            with open(self.history_path, 'rt', encoding='utf-8') \
                                                            as history_fd:
                self.history_json = json.load(history_fd)
        if self.history_json.get(self.token) is None:
            self.history_json[self.token] = [drama_name]
        else:
            self.history_json.get(self.token).append(drama_name)
        with open(self.history_path, 'wt', encoding='utf-8') as history_fd:
            json.dump(self.history_json, history_fd)

    def parse(self):
        for drama_id, drama_content in self.__get_drama_dict().items():
            self.__save(drama_id, drama_content)

if __name__ == "__main__":
    drama_parser = DramaParser()
    drama_parser.parse()
