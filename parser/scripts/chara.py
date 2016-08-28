import os
import json
import sqlite3
import requests
from datetime import datetime

import common
from paths import PathFinder
from arukana import ArukanaDownloader

class CharaInfoDB:
    def __init__(self):
        self.__db_conn = None
        self.__db_cur = None
        self.__schema = self.__get_schema()
        self.__create_table();
        self.__update_time = datetime.utcnow().strftime('%Y%m%d%H%M%S')

    def __get_schema(self):
        me_path = os.path.abspath(__file__)
        me_dir = os.path.dirname(me_path)
        config_dir = os.path.join(me_dir, 'schema')
        charainfo_schema_path = os.path.join(config_dir,
                                             'charainfo.schema')
        with open(charainfo_schema_path,'tr',encoding='utf-8') \
                                            as charainfo_schema_fobj:
            db_schema_json = json.load(charainfo_schema_fobj)
            db_schema = db_schema_json.get('charainfo_schema')
        return db_schema

    def __create_table(self):
        path_finder = PathFinder()
        db_file = path_finder.get_db_path()
        self.__db_conn = sqlite3.connect(db_file)
        self.__db_cur = self.__db_conn.cursor()

        query_result = self.__db_cur.execute("SELECT * from sqlite_master \
                                            where name = 'charainfo' \
                                            and type = 'table'")
        if query_result.fetchone() is None:
            create_script = "CREATE TABLE charainfo("
            for schema_key in self.__schema.keys():
                key_type = self.__schema[schema_key]
                create_script += schema_key + ' ' + key_type + ', '
            create_script = create_script[:len(create_script) - 2]
            create_script += ")"
            self.__db_cur.execute(create_script)
            self.__db_conn.commit()

    def __get_skill_value(self, flag1, flag2):
        max_int = int('0xffffffff', 16)
        bit_offset = int('0x20', 16)
        skill_value = flag1 & max_int
        skill_value |= flag2 << bit_offset
        return skill_value

    def __get_charainfo_data(self, charainfo):
        keys_string = ''
        values_string = ''
        skills = {'skillflag0_0': 0, 'skillflag0_1': 0,
                  'skillflag1_0': 0, 'skillflag1_1': 0 }
        for key in charainfo.keys():
            value = charainfo.get(key)
            if value is not None:
                value_string = str(value)
            else:
                value_string = 'None'
            value_string = value_string.replace(',', '\\')
            value_string = value_string.replace('\n','')
            keys_string += key + ','
            if self.__schema.get(key) != 'TEXT':
                values_string += value_string + ', '
            else:
                values_string += '"' + value_string + '", '
            if key in skills.keys():
                skills[key] = value
        skill1 = self.__get_skill_value(skills['skillflag0_0'],
                                 skills['skillflag0_1'])
        keys_string += 'skill1' + ','
        values_string += str(skill1) + ','
        skill2 = self.__get_skill_value(skills['skillflag1_0'],
                                 skills['skillflag1_1'])
        keys_string += 'skill2'
        values_string += str(skill2)
        keys_string += ', update_time'
        values_string += ', ' + self.__update_time
        return keys_string, values_string

    def insert_data(self, charainfo):
        cid = charainfo.get('cid')
        select_sql = 'SELECT * from charainfo where cid = {0}'.format(cid)
        self.__db_cur.execute(select_sql)
        if self.__db_cur.fetchone() is not None:
            return
        colnames, colvalues = self.__get_charainfo_data(charainfo)
        insert_sql = 'INSERT OR REPLACE INTO charainfo ('
        insert_sql += colnames + ') VALUES (' + colvalues + ')'
        self.__db_cur.execute(insert_sql)
        self.__db_conn.commit()
        print('Added to database: {0}'.format(cid))

    def __del__(self):
        if self.__db_conn is not None:
            self.__db_conn.close()

class CharaInfoParser:
    def __init__(self):
        path_finder = PathFinder()
        data_dir = path_finder.get_unpacked_data_folder()
        self.data_path = os.path.join(data_dir, 'charainfo_jp.json')
        self.timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')

    def get_charainfo_list(self):
        with open(self.data_path, 'tr', encoding='utf-8') as charainfo_fobj:
            charainfo_content = charainfo_fobj.read()
        charainfo_content = charainfo_content.replace('\n', '')
        charainfo_json = json.loads(charainfo_content)
        if type(charainfo_json) is not dict:
            common.exit_if_wrong_json_format()
        if not 'charainfo' in charainfo_json.keys():
            common.exit_if_wrong_json_format()
        charainfo_list = charainfo_json.get('charainfo')
        if type(charainfo_list) is not list:
            return None
        return charainfo_list

def parse_chara_info():
    charainfo_parser = CharaInfoParser()
    charainfo_db = CharaInfoDB()

    charainfo_list = charainfo_parser.get_charainfo_list()
    for charainfo in charainfo_list:
        if type(charainfo) is not dict:
            continue
        if charainfo['cid'] > 70000:
            continue
        charainfo_db.insert_data(charainfo)

if __name__ == "__main__":
    parse_chara_info()
