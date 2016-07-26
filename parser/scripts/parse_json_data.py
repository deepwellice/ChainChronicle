#!python3
#!/usr/bin/python3

import os
import json
import sqlite3
import requests
from datetime import datetime

import common
from paths import PathFinder
from arukana import ArukanaDownloader

def write_download_history(cid):
    print('New arukana found: {0:05d}'.format(cid))

def get_skill_value(flag1, flag2):
    max_int = int('0xffffffff', 16)
    bit_offset = int('0x20', 16)
    skill_value = flag1 & max_int
    skill_value |= flag2 << bit_offset
    return skill_value

def get_charainfo_data(schema, charainfo):
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
        if schema.get(key) != 'TEXT':
            values_string += value_string + ', '
        else:
            values_string += '"' + value_string + '", '
        if key in skills.keys():
            skills[key] = value
    skill1 = get_skill_value(skills['skillflag0_0'], skills['skillflag0_1'])
    keys_string += 'skill1' + ','
    values_string += str(skill1) + ','
    skill2 = get_skill_value(skills['skillflag1_0'], skills['skillflag1_1'])
    keys_string += 'skill2'
    values_string += str(skill2)
    return keys_string, values_string

if __name__ == "__main__":
    #read unpacked json data
    path_finder = PathFinder()
    unpack_data_dir = path_finder.get_unpacked_data_folder()
    charainfo_data_path = os.path.join(unpack_data_dir, 'charainfo_jp.json')
    with open(charainfo_data_path, 'tr', encoding='utf-8') \
                                                        as charainfo_fobj:
        charainfo_content = charainfo_fobj.read()
    charainfo_content = charainfo_content.replace('\n', '')
    charainfo_json = json.loads(charainfo_content)
    if type(charainfo_json) is not dict:
        common.exit_if_wrong_json_format()
    if not 'charainfo' in charainfo_json.keys():
        common.exit_if_wrong_json_format()
    charainfo_list = charainfo_json.get('charainfo')
    if type(charainfo_list) is not list:
        common.exit_if_wrong_json_format()

    #create database
    me_path = os.path.abspath(__file__)
    me_dir = os.path.dirname(me_path)
    config_dir = os.path.join(me_dir, 'schema')
    charainfo_schema_path = os.path.join(config_dir, 'charainfo.schema')
    with open(charainfo_schema_path,'tr',encoding='utf-8') \
                                                as charainfo_schema_fobj:
        charainfo_schema = json.load(charainfo_schema_fobj)
        charainfo_schema = charainfo_schema.get('charainfo_schema')
    db_file = path_finder.get_db_path()

    need_create_db = False
    if not os.path.exists(db_file):
        need_create_db = True

    db_conn = sqlite3.connect(db_file)
    db_cur = db_conn.cursor()
    if need_create_db:
        create_script = "CREATE TABLE charainfo("
        for schema_key in charainfo_schema.keys():
            key_type = charainfo_schema[schema_key]
            create_script += schema_key + ' ' + key_type + ', '
        create_script = create_script[:len(create_script) - 2]
        create_script += ")"
        db_cur.execute(create_script)

    arukana_downloader = ArukanaDownloader()
    update_time = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    for charainfo in charainfo_list:
        if type(charainfo) is not dict:
            continue
        insert_sql = 'INSERT OR REPLACE INTO charainfo ('
        cid = charainfo.get('cid')
        if cid >= 70000:
            break
        arukana_downloader.download(cid)
        col_names, col_values = \
                            get_charainfo_data(charainfo_schema, charainfo)
        col_names += ', update_time'
        col_values += ', ' + update_time
        insert_sql += col_names + ') VALUES (' + col_values + ')'
        db_cur.execute(insert_sql)
        db_conn.commit()
        print('Added to database: {0}'.format(cid))
    db_conn.close()
