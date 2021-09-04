import configparser
import fnmatch
import os
import re
import pandas as pd
from openpyxl import load_workbook  # 导入openpyxl


config_path = 'C:\\Users\\Administrator\\Desktop\\nas'

analyzer_path = 'C:\\Users\\Administrator\\Desktop\\NAS配置文件设备列表.xlsx'

config = configparser.ConfigParser()
config.read('config/config.ini', encoding='utf-8')

nas_fliename_list_path = 'C:\\Users\\Administrator\\Desktop\\'
NAS_FILENAME = config.get('NAS', 'NAS_FILENAME')

nas_filename_pattern = re.compile(NAS_FILENAME, re.MULTILINE)

ls_config_path = os.listdir(config_path)

NAS_DEVICE_DIR = {}

def get_nas_device_list():
    nas_fliename_list = []
    for name in ls_config_path:
        filename = nas_filename_pattern.findall(name)
        if filename[0].find('FW') < 0 and filename[0].find('fw') < 0 and filename[0].find('TAP') < 0 and filename[0].find('tap') < 0 and filename[0].find('RT') < 0:
            nas_fliename_list.append(filename[0])

    df = pd.DataFrame(nas_fliename_list, columns=['设备名称'])
    df.to_excel(nas_fliename_list_path+'NAS配置文件设备列表.xlsx', index=False)

def get_nas_filename_list():
    nas_fliename_list = {}
    for name in ls_config_path:
        filename = nas_filename_pattern.findall(name)
        nas_fliename_list[filename[0]] = name
    return nas_fliename_list

def get_device_data(path):
    wb = load_workbook(path)  # 打开Excel
    sheet = wb['NAS配置文件列表']  # 定位表单
    for row in range(2, sheet.max_row + 1):
        device = {}
        name = sheet.cell(row, 1).value.strip()
        device['name'] = name
        device['type']  = sheet.cell(row, 2).value.strip()
        device['version'] = sheet.cell(row, 3).value.strip()
        NAS_DEVICE_DIR[name] = device

    ltm_device_list = []
    sheet2 = wb['LTM解析设备列表']
    for row in range(2, sheet2.max_row + 1):
        ltm_device_list.append(sheet2.cell(row, 1).value.strip())
    return ltm_device_list

def get_ltm_config(filepath,type,version):
    ltm_config = {}
    ltm_config_open = open(filepath, encoding='utf-8')
    # if version == 'v12':

    pass

def main():
    nas_fliename_list = get_nas_filename_list()
    ltm_device_list = get_device_data(analyzer_path)

    for device in ltm_device_list:
        if device not in nas_fliename_list.keys():
            print(device+"设备名不正确，请填入正确的设备名称！")
            break
        print(nas_fliename_list[device])
        print(NAS_DEVICE_DIR[device]['version'])


if __name__ == '__main__':
    main()






