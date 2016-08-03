import os
import json
import datetime
import requests
import threading

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
        self.log_lock = threading.Lock()

    def download_all(self, cid_range):
        for cid in cid_range:
            threading.Thread(target=self.download,
                             args=(range(cid, cid+1)),
                             daemon=True).start()

    def download(self, cid):
        local_path = os.path.join(self.download_folder,
                                  '{0:05d}.scr'.format(cid))
        if os.path.exists(local_path):
            print("download skipped: {0}".format(cid))
            return 304

        print("download started: {0}".format(cid))
        download_url = '{0}cha_2d_card_{1:05d}.scr'.format(self.url, cid)
        retry_count = 10
        while retry_count > 0:
            retry_count -= 1
            try:
                download_response = requests.get(download_url, stream=True,
                                                 timeout=180)
                ret_code = download_response.status_code
                if ret_code != 200:
                    print("downaload failure: {0}".format(ret_code))
                    return ret_code
                with open(local_path, 'wb') as local_fd:
                    for chunk in download_response.iter_content(1024):
                        local_fd.write(chunk)
                self.log_history(cid)
                print('Download successfully: {0}'.format(cid))
                return ret_code
            except requests.RequestException:
                continue
        print('Download timeout: {0}'.format(cid))
        return ret_code

    def init_history(self):
        if os.path.exists(self.history_path):
            return
        with open(self.history_path, 'wt', encoding='utf-8') as history_fd:
            json.dump({self.token: []}, history_fd)

    def log_history(self, cid):
        if self.log_lock.acquire(True, timeout=10):
            self.init_history()
            if (self.json is None):
                with open(self.history_path, 'rt', encoding='utf-8') \
                                                            as history_fd:
                    self.json = json.load(history_fd)
            if self.json.get(self.token) is None:
                self.json[self.token] = [cid]
            else:
                self.json.get(self.token).append(cid)
            with open(self.history_path, 'wt', encoding='utf-8') \
                                                            as history_fd:
                json.dump(self.json, history_fd)
            self.log_lock.release()

if __name__ == "__main__":
    test_downloader = ArukanaDownloader()
    test_downloader.download_all(range(1,70001))
    # for cid in range(1, 70001):
    #    test_downloader.download(cid)
