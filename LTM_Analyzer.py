import configparser
import datetime
import fnmatch
import os
import re
import pandas as pd
from openpyxl import load_workbook  # 导入openpyxl

result_path = 'E:\\result\\'

config_path = 'C:\\Users\\Administrator\\Desktop\\nas'

analyzer_path = 'C:\\Users\\Administrator\\Desktop\\NAS配置文件设备列表.xlsx'

config = configparser.ConfigParser()
config.read('config/config.ini', encoding='utf-8')

nas_fliename_list_path = 'C:\\Users\\Administrator\\Desktop\\'
NAS_FILENAME = config.get('NAS', 'NAS_FILENAME')
LTM_V12_ROUTE_RE_STR = config.get('LTM', 'LTM_V12_ROUTE_RE_STR')
LTM_V10_ROUTE_RE_STR = config.get('LTM', 'LTM_V10_ROUTE_RE_STR')
LTM_V12_SELF_IP_RE_STR = config.get('LTM', 'LTM_V12_SELF_IP_RE_STR')
LTM_V10_SELF_IP_RE_STR = config.get('LTM', 'LTM_V10_SELF_IP_RE_STR')
NSAE_IP_RE_STR = config.get('LTM', 'NSAE_IP_RE_STR')
NSAE_ROUTE_RE_STR = config.get('LTM', 'NSAE_ROUTE_RE_STR')

nas_filename_pattern = re.compile(NAS_FILENAME, re.MULTILINE)
ltm_v12_route_pattern = re.compile(LTM_V12_ROUTE_RE_STR, re.MULTILINE)
ltm_v10_route_pattern = re.compile(LTM_V10_ROUTE_RE_STR, re.MULTILINE)
ltm_v12_self_ip_pattern = re.compile(LTM_V12_SELF_IP_RE_STR, re.MULTILINE)
ltm_v10_self_ip_pattern = re.compile(LTM_V10_SELF_IP_RE_STR, re.MULTILINE)
nsae_ip_pattern = re.compile(NSAE_IP_RE_STR, re.MULTILINE)
nsae_route_pattern = re.compile(NSAE_ROUTE_RE_STR, re.MULTILINE)

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
        device['type']  = sheet.cell(row, 2).value
        device['version'] = sheet.cell(row, 3).value
        device['real_name'] = sheet.cell(row, 4).value
        device['mgmt_ip'] = sheet.cell(row, 5).value
        NAS_DEVICE_DIR[name] = device

    ltm_device_list = []
    sheet2 = wb['LTM解析设备列表']
    for row in range(2, sheet2.max_row + 1):
        ltm_device_list.append(sheet2.cell(row, 1).value)
    return ltm_device_list


def get_ltm_config(filepath,type,version):
    ltm_config = {}
    ltm_config_open = open(filepath, encoding='utf-8')
    ltm_config_open_str = ltm_config_open.read()
    routes = ''
    self_ips = ''
    float_ips = ''
    if type == 'F5':
        if version == 'V12' or version == 'V11' or version == 'V13':
            ltm_v12_route = ltm_v12_route_pattern.findall(ltm_config_open_str)
            for item in ltm_v12_route:
                network = item[1].strip()
                gw = item[0].strip()
                routes = routes + network + ' gw ' + gw + '\n'

            ltm_v12_self_ip = ltm_v12_self_ip_pattern.findall(ltm_config_open_str)
            for item in ltm_v12_self_ip:
                ip = item[0].strip()
                is_float = item[1].strip()
                traffic_group = item[2].strip()
                vlan = item[3].strip()
                if is_float == 'enabled':
                    float_ips = float_ips + ip + ' ' + traffic_group + '\n'
                else:
                    self_ips = self_ips + ip + ' ' + vlan + '\n'

        elif version == 'V10':
            ltm_v10_route = ltm_v10_route_pattern.findall(ltm_config_open_str)
            for item in ltm_v10_route:
                network = item[0].strip()
                gw = item[1].strip()
                routes = routes + network + ' gw ' + gw + '\n'

            ltm_v10_self_ip = ltm_v10_self_ip_pattern.findall(ltm_config_open_str)
            for item in ltm_v10_self_ip:
                ip = item[0].strip()
                is_float = item[1].strip()
                unit = item[2].strip()
                vlan = item[3].strip()
                if is_float == 'enabled':
                    float_ips = float_ips + ip  + '\n'
                else:
                    self_ips = self_ips + ip + ' ' + vlan + '\n'

    elif type == 'NSAE':
        nsae_ip = nsae_ip_pattern.findall(ltm_config_open_str)
        for item in nsae_ip:
            interface = item[0].strip().replace('"','')
            ip = item[1].strip()
            mask = item[2].strip()
            self_ips = self_ips + ip + '/' + mask + ' ' + interface + '\n'

        nsae_route = nsae_route_pattern.findall(ltm_config_open_str)
        for item in nsae_route:
            type = item[0].strip()
            route = item[1].strip()
            if type == 'default':
                routes = routes + 'default' + ' gw ' + route + '\n'
            elif type == 'static':
                patterns = r' +'
                network = re.split(patterns,route)
                routes = routes + network[0] + '/' + network[1] + ' gw ' + network[2] + '\n'

    ltm_config['route'] = routes
    ltm_config['self_ip'] = self_ips
    ltm_config['float_ip'] = float_ips
    ltm_config_open.close()
    return ltm_config


def main():
    nas_fliename_list = get_nas_filename_list()
    ltm_device_list = get_device_data(analyzer_path)

    networks = {}
    for device in ltm_device_list:
        if device not in nas_fliename_list.keys():
            print(device+"设备名不正确，请填入正确的设备名称！")
            break
        filepath = config_path + '\\' + nas_fliename_list[device]
        device_net_info = [''] * 5
        version = NAS_DEVICE_DIR[device]['version']
        real_name = NAS_DEVICE_DIR[device]['real_name']
        mgmt_ip = NAS_DEVICE_DIR[device]['mgmt_ip']
        device_type = NAS_DEVICE_DIR[device]['type']
        ltm_config = get_ltm_config(filepath,device_type,version)
        device_net_info[0] = real_name
        device_net_info[1] = mgmt_ip
        device_net_info[2] = ltm_config['self_ip']
        device_net_info[3] = ltm_config['float_ip']
        device_net_info[4] = ltm_config['route']
        networks[device] = device_net_info

    result_all_networks_list = networks.values()
    df = pd.DataFrame(result_all_networks_list, columns=['设备名称','管理ip','互联ip','浮动ip','路由'])
    now_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    respath = result_path + "result_all_networks_" + now_time + ".xlsx"
    df.to_excel(respath, index=False)
    print('解析完成：'+respath)


if __name__ == '__main__':
    main()






