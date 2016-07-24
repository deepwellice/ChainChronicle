#!python3
#!/usr/bin/python3

import os
import json
import sqlite3
import requests

import common
from paths import PathFinder

def download_arukana(cid, arukana_path):
    local_path = os.path.join(arukana_path, '{0:05d}.scr'.format(cid))
    if os.path.exists(local_path):
        return 304
    download_url = 'http://dl.sega-pc.com/chruser/Resource/Card/cha_2d_card_{0:05d}.scr'.format(cid)
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
            return ret_code
        except requests.RequestException:
            continue
    return ret_code

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

#read unpacked json data
path_finder = PathFinder()
unpack_data_dir = path_finder.get_unpacked_data_folder()
charainfo_data_path = os.path.join(unpack_data_dir, 'charainfo_jp.json')
with open(charainfo_data_path, 'tr', encoding='utf-8') as charainfo_fobj:
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
for charainfo in charainfo_list:
    insert_sql = 'INSERT OR REPLACE INTO charainfo ('
    if type(charainfo) is not dict:
        continue
    print(charainfo.get('cid'))
    if charainfo.get('cid') >= 70000:
        continue
    download_arukana(charainfo.get('cid'), path_finder.get_arukana_folder())
    col_names, col_values = get_charainfo_data(charainfo_schema, charainfo)
    insert_sql += col_names + ') VALUES (' + col_values + ')'
    db_cur.execute(insert_sql)
db_conn.commit()
db_conn.close()
