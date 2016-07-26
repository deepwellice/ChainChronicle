import os
import json
import datetime
import requests

import common
from paths import PathFinder

class ArukanaDownloader:

    def __init__(self):
        path_finder = PathFinder()
        self.download_folder = path_finder.get_arukana_folder()
        self.history_path = path_finder.get_arukana_download_history_path()
        self.url = 'http://dl.sega-pc.com/chruser/Resource/Card/'
        self.token = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
        self.json = None

    def download(self, cid):
        local_path = os.path.join(self.download_folder,
                                  '{0:05d}.scr'.format(cid))
        if os.path.exists(local_path):
            return 304
        download_url = '{0}cha_2d_card_{1:05d}.scr'.format(self.url, cid)
        retry_count = 10
        while retry_count > 0:
            retry_count -= 1
            try:
                download_response = requests.get(download_url, stream=True,
                                                 timeout=180)
                ret_code = download_response.status_code
                if ret_code != 200:
                    return ret_code
                with open(local_path, 'wb') as local_fd:
                    for chunk in download_response.iter_content(1024):
                        local_fd.write(chunk)
                self.log_history(cid)
                print('Download successfully: {0}'.format(cid))
                return ret_code
            except requests.RequestException:
                print('Download timeout: {0}'.format(cid))
                continue
        return ret_code

    def init_history(self):
        if os.path.exists(self.history_path):
            return
        with open(self.history_path, 'wt', encoding='utf-8') as history_fd:
            json.dump({self.token: []}, history_fd)

    def log_history(self, cid):
        self.init_history()
        if (self.json is None):
            with open(self.history_path, 'rt', encoding='utf-8') \
                                                        as history_fd:
                self.json = json.load(history_fd)
        if self.json.get(self.token) is None:
            self.json[self.token] = [cid]
        else:
            self.json.get(self.token).append(cid)
        with open(self.history_path, 'wt', encoding='utf-8') as history_fd:
            json.dump(self.json, history_fd)

if __name__ == "__main__":
    test_downloader = ArukanaDownloader()
    for cid in range(111, 120):
        test_downloader.log_history(cid)
