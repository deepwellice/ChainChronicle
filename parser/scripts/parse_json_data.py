#!python3
#!/usr/bin/python3

from arukana import ArukanaDownloader
from chara import CharaInfoParser, CharaInfoDB

def parse_chara_info():
    charainfo_parser = CharaInfoParser()
    charainfo_db = CharaInfoDB()
    arukana_downloader = ArukanaDownloader()

    charainfo_list = charainfo_parser.get_charainfo_list()
    for charainfo in charainfo_list:
        if type(charainfo) is not dict:
            continue
        cid = charainfo.get('cid')
        if cid >= 70000:
            break
        arukana_downloader.download(cid)
        charainfo_db.insert_data(charainfo)

if __name__ == "__main__":
    parse_chara_info()
