import os
import pandas as pd
from openpyxl import load_workbook
config_os = 'linux'
config_path = '/Users/config'
#config_os = 'windows'
#config_path = 'E:\\config'

device_analyzer_list = []
device_list_map = {}
device_path_map = {}
def get_device_list():
    device_list_path = ''
    if config_os == 'windows':
        device_list_path = config_path + '\\' + '设备列表.xlsx'
    elif config_os == 'linux':
        device_list_path = config_path + '/' + '设备列表.xlsx'

    wb = load_workbook(device_list_path)  # 打开Excel
    sheet1 = wb['解析列表']
    for row in range(2, sheet1.max_row + 1):
        device_analyzer = sheet1.cell(row, 1).value.strip()
        if device_analyzer == '':
            print('解析列表为空，请填写要解析的设备！')
            return
        device_analyzer_list.append(device_analyzer)

    sheet2 = wb['设备列表']
    for row in range(2, sheet2.max_row + 1):
        name_device = sheet2.cell(row, 1).value.strip()
        if name_device != '':
            device_info = {}
            device_info['name'] = name_device
            device_info['type'] = sheet2.cell(row, 2).value.strip()
            device_info['version'] = sheet2.cell(row, 3).value.strip()
            device_list_map[name_device] = device_info

    files= os.listdir(config_path)
    for file in files:
        new_file_path = ''
        if config_os == 'windows':
            new_file_path = config_path + '\\' + file
        elif config_os == 'linux':
            new_file_path = config_path + '/' + file

        if os.path.isdir(new_file_path):
            devices = os.listdir(new_file_path)
            for device in devices:
                devicename,extension = os.path.splitext(device)
                if extension == '.txt' or extension == '.TXT':
                    if config_os == 'windows':
                        device_path_map[devicename] = new_file_path+'\\'+device
                    elif config_os == 'linux':
                        device_path_map[devicename] = new_file_path + '/' + device

def main():
    get_device_list()

    for device_name in device_analyzer_list:
        print(device_name)


if __name__ == '__main__':
    main()






