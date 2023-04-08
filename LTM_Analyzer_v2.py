import configparser
import json
import re
import datetime
import os
import pandas as pd
from openpyxl import load_workbook


config_os = 'linux'
config_path = '/Users/device'
#config_os = 'windows'
#config_path = 'E:\\config'


device_analyzer_list = []
device_list_map = {}
device_path_map = {}

device_list_path = ''
config_path_os = ''
result_path = ''
if config_os == 'windows':
    config_path_os = config_path + '\\'
    result_path = config_path_os + 'result\\'
elif config_os == 'linux':
    config_path_os = config_path + '/'
    result_path = config_path_os + 'result/'

device_list_path = config_path_os + '设备列表.xlsx'

port_json_str_open = open('config/port.json', encoding='utf-8' ,errors='ignore')
port_json_str = port_json_str_open.read()
ports_dir = json.loads(port_json_str)
ports_data = dict([val, key] for key, val in ports_dir.items())
port_json_str_open.close()

config = configparser.ConfigParser()
config.read('config/config_v2.ini', encoding='utf-8')

LTM_V12_SOURCE_PERSIST_RE_STR = config.get('LTM', 'LTM_V12_SOURCE_PERSIST_RE_STR')
LTM_V12_COOKIE_PERSIST_RE_STR = config.get('LTM', 'LTM_V12_COOKIE_PERSIST_RE_STR')
LTM_V12_HTTP_PROFILE_RE_STR = config.get('LTM', 'LTM_V12_HTTP_PROFILE_RE_STR')
LTM_V12_TCP_PROFILE_RE_STR = config.get('LTM', 'LTM_V12_TCP_PROFILE_RE_STR')
LTM_V12_FASTL4_PROFILE_RE_STR = config.get('LTM', 'LTM_V12_FASTL4_PROFILE_RE_STR')
LTM_V12_POOL_RE_STR = config.get('LTM', 'LTM_V12_POOL_RE_STR')
LTM_V12_POOL_MEMBER_RE_STR = config.get('LTM', 'LTM_V12_POOL_MEMBER_RE_STR')
LTM_V12_VS_RE_STR = config.get('LTM', 'LTM_V12_VS_RE_STR')

NSAE_SLB_REAL_RE_STR = config.get('LTM', 'NSAE_SLB_REAL_RE_STR')
NSAE_SLB_REAL_DISABLE_RE_STR = config.get('LTM', 'NSAE_SLB_REAL_DISABLE_RE_STR')
NSAE_SLB_GROUP_MEMBER_RE_STR = config.get('LTM', 'NSAE_SLB_GROUP_MEMBER_RE_STR')
NSAE_SLB_VIRTUAL_RE_STR = config.get('LTM', 'NSAE_SLB_VIRTUAL_RE_STR')
NSAE_SLB_POLICY_RE_STR = config.get('LTM', 'NSAE_SLB_POLICY_RE_STR')
NSAE_SSL_HOST_RE_STR = config.get('LTM', 'NSAE_SSL_HOST_RE_STR')

ltm_v12_source_persist_pattern = re.compile(LTM_V12_SOURCE_PERSIST_RE_STR, re.MULTILINE)
ltm_v12_cookie_persist_pattern = re.compile(LTM_V12_COOKIE_PERSIST_RE_STR, re.MULTILINE)
ltm_v12_http_profile_pattern = re.compile(LTM_V12_HTTP_PROFILE_RE_STR, re.MULTILINE)
ltm_v12_tcp_profile_pattern = re.compile(LTM_V12_TCP_PROFILE_RE_STR, re.MULTILINE)
ltm_v12_fastl4_profile_pattern = re.compile(LTM_V12_FASTL4_PROFILE_RE_STR, re.MULTILINE)
ltm_v12_pool_pattern = re.compile(LTM_V12_POOL_RE_STR, re.MULTILINE)
ltm_v12_pool_member_pattern = re.compile(LTM_V12_POOL_MEMBER_RE_STR, re.MULTILINE)
ltm_v12_vs_pattern = re.compile(LTM_V12_VS_RE_STR, re.MULTILINE)

nsae_slb_real_pattern = re.compile(NSAE_SLB_REAL_RE_STR, re.MULTILINE)
nsae_slb_real_disable_pattern = re.compile(NSAE_SLB_REAL_DISABLE_RE_STR, re.MULTILINE)
nsae_slb_group_member_pattern = re.compile(NSAE_SLB_GROUP_MEMBER_RE_STR, re.MULTILINE)
nsae_slb_virtual_pattern = re.compile(NSAE_SLB_VIRTUAL_RE_STR, re.MULTILINE)
nsae_slb_policy_pattern = re.compile(NSAE_SLB_POLICY_RE_STR, re.MULTILINE)
nsae_ssl_host_pattern = re.compile(NSAE_SSL_HOST_RE_STR, re.MULTILINE)

def get_device_list():
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
        new_file_path = config_path_os + file
        if os.path.isdir(new_file_path):
            devices = os.listdir(new_file_path)
            for device in devices:
                devicename,extension = os.path.splitext(device)
                if extension == '.txt' or extension == '.TXT':
                    if config_os == 'windows':
                        device_path_map[devicename] = new_file_path +'\\'+ device
                    elif config_os == 'linux':
                        device_path_map[devicename] = new_file_path + '/' + device



def get_ltm_config(filepath,type,version):

    ltm_config_open = open(filepath, encoding='utf-8' ,errors='ignore')
    ltm_config_open_str = ltm_config_open.read()
    ltm_config_open.close()

    ltm_v12_source_persist_map = {}
    ltm_v12_source_persist_map['source_addr'] = '3600'
    ltm_v12_source_persist = ltm_v12_source_persist_pattern.findall(ltm_config_open_str)
    for item in ltm_v12_source_persist:
        name = item[0].strip()
        source_persist_info = item[1]
        source_persist_pattern = re.compile("\s*timeout\s(\d*)", re.MULTILINE)
        time_out = ''.join(source_persist_pattern.findall(source_persist_info))
        if time_out == '':
            time_out = '3600'
        ltm_v12_source_persist_map[name] = time_out

    ltm_v12_cookie_persist_map = {}
    ltm_v12_cookie_persist_map['cookie'] = '##encrypt#disabled##name#null##method#insert##'
    ltm_v12_cookie_persist = ltm_v12_cookie_persist_pattern.findall(ltm_config_open_str)
    for item in ltm_v12_cookie_persist:
        name = item[0].strip()
        cookie_persist_info = item[1]
        is_encrypt_pattern = re.compile("\s*cookie-encryption\s(\w*)", re.MULTILINE)
        is_encrypt = ''.join(is_encrypt_pattern.findall(cookie_persist_info))
        cookie_name_pattern = re.compile("\s*cookie-name\s(\w*)", re.MULTILINE)
        cookie_name = ''.join(cookie_name_pattern.findall(cookie_persist_info))
        method_pattern = re.compile("\s*method\s(\w*)", re.MULTILINE)
        method = ''.join(method_pattern.findall(cookie_persist_info))
        if method == '':
            method = 'insert'
        ltm_v12_cookie_persist_map[name] = '##encrypt#'+is_encrypt+'##name#'+cookie_name+'##method#'+method+'##'

    ltm_v12_http_profile_map = {}
    ltm_v12_http_profile_map['http'] = 'disabled'
    ltm_v12_http_profile = ltm_v12_http_profile_pattern.findall(ltm_config_open_str)
    for item in ltm_v12_http_profile:
        name = item[0].strip()
        http_profile_info = item[1]
        http_profile_pattern = re.compile("\s*insert-xforwarded-for\s(\w*)", re.MULTILINE)
        xforwarded = ''.join(http_profile_pattern.findall(http_profile_info))
        ltm_v12_http_profile_map[name] = xforwarded

    ltm_v12_tcp_profile_map = {}
    ltm_v12_tcp_profile_map['tcp'] = '300'
    ltm_v12_tcp_profile = ltm_v12_tcp_profile_pattern.findall(ltm_config_open_str)
    for item in ltm_v12_tcp_profile:
        name = item[0].strip()
        tcp_profile_info = item[1]
        idle_timeout_pattern = re.compile("\s*idle-timeout\s(\d*)", re.MULTILINE)
        idle_timeout = ''.join(idle_timeout_pattern.findall(tcp_profile_info))
        if idle_timeout == '':
            idle_timeout = '300'
        ltm_v12_tcp_profile_map[name] = idle_timeout

    ltm_v12_fastl4_profile_map = {}
    ltm_v12_fastl4_profile_map['fastL4'] = '##timeout#300##pva#full##'
    ltm_v12_fastl4_profile = ltm_v12_fastl4_profile_pattern.findall(ltm_config_open_str)
    for item in ltm_v12_fastl4_profile:
        name = item[0].strip()
        fastl4_profile_info = item[1]
        idle_timeout_pattern = re.compile("\s*idle-timeout\s(\d*)", re.MULTILINE)
        idle_timeout = ''.join(idle_timeout_pattern.findall(fastl4_profile_info))
        if idle_timeout == '':
            idle_timeout = '300'
        pva_pattern = re.compile("\s*pva-acceleration\s(\w*)", re.MULTILINE)
        pva = ''.join(pva_pattern.findall(fastl4_profile_info))
        if pva == '':
            pva = 'full'
        ltm_v12_fastl4_profile_map[name] = '##timeout#'+idle_timeout+'##pva#'+pva+'##'

    ltm_v12_pool_map = {}
    ltm_v12_pool = ltm_v12_pool_pattern.findall(ltm_config_open_str)
    for item in ltm_v12_pool:
        name = item[0].strip()
        pool_info = item[1]
        balanc_mode_pattern = re.compile("\s*load-balancing-mode\s([\s\S]*?)\n", re.MULTILINE)
        balanc_mode = ''.join(balanc_mode_pattern.findall(pool_info))
        if balanc_mode == '':
            balanc_mode = 'round-robin'

        monitor_pattern = re.compile("\s*monitor\s([\s\S]*?)\n", re.MULTILINE)
        monitor = ''.join(monitor_pattern.findall(pool_info))

        members_str_pattern = re.compile("\s*members\s(none|{[\s\S]*?}\n\s*monitor)", re.MULTILINE)
        members_str = ''.join(members_str_pattern.findall(pool_info))

        members_info = 'none'
        if members_str != 'none' and  members_str != '':
            ltm_v12_pool_member = ltm_v12_pool_member_pattern.findall(members_str)
            members_info_detail = ''
            members_info_simple = ''
            for item2 in ltm_v12_pool_member:
                ip_port_str = item2[0].strip()
                ip_port_info = ''
                if re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}:[\s\S]*?$",ip_port_str):
                    ipports = ip_port_str.split(":")
                    ip = ipports[0]
                    port = ipports[1]
                    if port in ports_data.keys():
                        port = ports_data[port]
                    ip_port_info = ip + ":" + port
                else:
                    ipports = ip_port_str.split(".")
                    ip = ipports[0]
                    port = ipports[1]
                    if port in ports_data.keys():
                        port = ports_data[port]
                    ip_port_info = ip + "." + port

                info_member = item2[1].strip()

                session_pattern = re.compile("\s*session\s([\s\S]*?)\n", re.MULTILINE)
                session = ''.join(session_pattern.findall(info_member))

                state_pattern = re.compile("\s*state\s([\s\S]*?)\n", re.MULTILINE)
                state = ''.join(state_pattern.findall(info_member))

                con_limit_pattern = re.compile("\s*connection-limit\s(\d*)", re.MULTILINE)
                con_limit = ''.join(con_limit_pattern.findall(info_member))
                if con_limit == '':
                    con_limit = '0'

                priority_pattern = re.compile("\s*priority-group\s(\d*)", re.MULTILINE)
                priority = ''.join(priority_pattern.findall(info_member))
                if priority == '':
                    priority = '0'

                ratio_pattern = re.compile("\s*ratio\s(\d*)", re.MULTILINE)
                ratio = ''.join(ratio_pattern.findall(info_member))
                if ratio == '':
                    ratio = '0'

                members_info_detail = members_info_detail + ip_port_info + ' ' + session + ' ' + state + ' l:' + con_limit + ' p:' + priority + ' r:' + ratio  + '\n'
                if session == 'user-enabled' or session == 'monitor-enabled':
                    members_info_simple  = members_info_simple + ip_port_info + '\n'

                members_info = '##members_info_simple#' + members_info_simple + '##members_info_detail#' + members_info_detail + '##'

        ltm_v12_pool_map[name] = '##balanc_mode#'+balanc_mode+'##monitor#'+monitor + members_info

    ltm_v12_vs_list = []
    ltm_v12_vs = ltm_v12_vs_pattern.findall(ltm_config_open_str)

    for item in ltm_v12_vs:
        vs = ['']*28
        name = item[0].strip()
        vs[0] = name
        vs_info = item[1]

        vs_conn_limit_pattern = re.compile("\s*connection-limit\s(\d*)", re.MULTILINE)
        vs_conn_limit = ''.join(vs_conn_limit_pattern.findall(vs_info))
        if vs_conn_limit == '':
            vs_conn_limit = '0'
        vs[1] = vs_conn_limit

        vs_ip_port_str_pattern = re.compile("\s*destination\s([\s\S]*?)\n", re.MULTILINE)
        vs_ip_port_str = ''.join(vs_ip_port_str_pattern.findall(vs_info))

        vs_ip_port_info = ''
        if re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}:[\s\S]*?$", vs_ip_port_str):
            ipports = vs_ip_port_str.split(":")
            ip = ipports[0]
            port = ipports[1]
            if port in ports_data.keys():
                port = ports_data[port]
            vs_ip_port_info = ip + ":" + port
        else:
            ipports = vs_ip_port_str.split(".")
            ip = ipports[0]
            port = ipports[1]
            if port in ports_data.keys():
                port = ports_data[port]
            vs_ip_port_info = ip + "." + port
        vs[2] = vs_ip_port_info

        vs_status_pattern = re.compile("\s*(disabled)\n", re.MULTILINE)
        vs_status = ''.join(vs_status_pattern.findall(vs_info))
        if vs_status.strip() == '':
            vs_status = 'enabled'
        vs[3] = vs_status

        vs_protocol_pattern = re.compile("\s*ip-protocol\s([\s\S]*?)\n", re.MULTILINE)
        vs_protocol = ''.join(vs_protocol_pattern.findall(vs_info))
        vs[4] = vs_protocol

        vs_persist_str_pattern = re.compile("\s*persist\s(none|{[\s\S]*?})\n", re.MULTILINE)
        vs_persist_str = ''.join(vs_persist_str_pattern.findall(vs_info))

        vs_persist_name = 'none'
        vs_persist_mothod = 'none'
        vs_persist_timeout = ''
        persist_cookie_encrypt = ''
        persist_cookie_name = ''
        persist_cookie_method = ''
        if vs_persist_str != 'none' and vs_persist_str != '':
            vs_persist_str_pattern = re.compile("{\s*([\s\S]*?)\s{\n", re.MULTILINE)
            vs_persist_name = ''.join(vs_persist_str_pattern.findall(vs_persist_str))
            if vs_persist_name in ltm_v12_source_persist_map.keys():
                vs_persist_mothod = 'source_addr'
                vs_persist_timeout = ltm_v12_source_persist_map[vs_persist_name]
            elif vs_persist_name in ltm_v12_cookie_persist_map.keys():
                vs_persist_mothod = 'session_cookie'
                cookie_persist_str = ltm_v12_cookie_persist_map[vs_persist_name]
                cookie_encrypt_pattern = re.compile("##encrypt#([\s\S]*?)##", re.MULTILINE)
                persist_cookie_encrypt = ''.join(cookie_encrypt_pattern.findall(cookie_persist_str))
                cookie_name_pattern = re.compile("##name#([\s\S]*?)##", re.MULTILINE)
                persist_cookie_name = ''.join(cookie_name_pattern.findall(cookie_persist_str))
                cookie_method_pattern = re.compile("##method#([\s\S]*?)##", re.MULTILINE)
                persist_cookie_method = ''.join(cookie_method_pattern.findall(cookie_persist_str))

        vs[5] = vs_persist_name
        vs[6] = vs_persist_mothod
        vs[7] = vs_persist_timeout
        vs[8] = persist_cookie_encrypt
        vs[9] = persist_cookie_name
        vs[10] = persist_cookie_method

        vs_pool_pattern = re.compile("[^{]\n\s*pool\s([\s\S]*?)\n", re.MULTILINE)
        vs_pool = ''.join(vs_pool_pattern.findall(vs_info))

        vs_pool_name = 'none'
        vs_balanc_mode = ''
        vs_pool_monitor = ''
        members_info_simple = ''
        members_info_detail = ''
        if vs_pool != 'none' and vs_pool != '':
            vs_pool_name = vs_pool
            if vs_pool_name in ltm_v12_pool_map.keys():
                vs_pool_info_str = ltm_v12_pool_map[vs_pool_name]
                vs_balanc_mode_pattern = re.compile("##balanc_mode#([\s\S]*?)##", re.MULTILINE)
                vs_balanc_mode = ''.join(vs_balanc_mode_pattern.findall(vs_pool_info_str))
                vs_pool_monitor_pattern = re.compile("##monitor#([\s\S]*?)##", re.MULTILINE)
                vs_pool_monitor = ''.join(vs_pool_monitor_pattern.findall(vs_pool_info_str))
                members_info_simple_pattern = re.compile("##members_info_simple#([\s\S]*?)##", re.MULTILINE)
                members_info_simple = ''.join(members_info_simple_pattern.findall(vs_pool_info_str))
                members_info_detail_pattern = re.compile("##members_info_detail#([\s\S]*?)##", re.MULTILINE)
                members_info_detail = ''.join(members_info_detail_pattern.findall(vs_pool_info_str))

        vs[11] = vs_pool_name
        vs[12] = vs_balanc_mode
        vs[13] = vs_pool_monitor
        vs[14] = members_info_simple.strip('\n')
        vs[15] = members_info_detail.strip('\n')

        vs_profiles_pattern = re.compile("\s*profiles\s{([\s\S]*?{\s}\n)\s*}\n", re.MULTILINE)
        vs_profiles = ''.join(vs_profiles_pattern.findall(vs_info))

        fastl4_profile_name = ''
        fastl4_timeout = ''
        fastl4_pva = ''
        tcp_profile_name = ''
        tcp_profile_timeout = ''
        http_profile_name = ''
        http_profile_xforwarded = ''
        other_profile = ''
        profiles_info_pattern = re.compile("\s*([\s\S]*?)\s{\s}\n", re.MULTILINE)
        profiles_list = profiles_info_pattern.findall(vs_profiles)
        for profile in profiles_list:
            profile_name = profile.strip()
            if profile_name in ltm_v12_fastl4_profile_map.keys():
                fastl4_profile_name = profile_name
                fastl4_info_str = ltm_v12_fastl4_profile_map[profile_name]
                fastl4_timeout_pattern = re.compile("##timeout#([\s\S]*?)##", re.MULTILINE)
                fastl4_timeout = ''.join(fastl4_timeout_pattern.findall(fastl4_info_str))
                fastl4_pva_pattern = re.compile("##pva#([\s\S]*?)##", re.MULTILINE)
                fastl4_pva = ''.join(fastl4_pva_pattern.findall(fastl4_info_str))
            elif profile_name in ltm_v12_tcp_profile_map.keys():
                tcp_profile_name = profile_name
                tcp_profile_timeout = ltm_v12_tcp_profile_map[profile_name]
            elif profile_name in ltm_v12_http_profile_map.keys():
                http_profile_name = profile_name
                http_profile_xforwarded = ltm_v12_http_profile_map[profile_name]
            else:
                other_profile = other_profile + '\n' + profile_name

        vs[16] = fastl4_profile_name
        vs[17] = fastl4_timeout
        vs[18] = fastl4_pva
        vs[19] = tcp_profile_name
        vs[20] = tcp_profile_timeout
        vs[21] = http_profile_name
        vs[22] = http_profile_xforwarded
        vs[23] = other_profile.strip('\n')

        vs_rules_pattern = re.compile("\s*rules\s(none|{[\s\S]*?})\n", re.MULTILINE)
        vs_rules = ''.join(vs_rules_pattern.findall(vs_info))
        vs[24] = vs_rules

        vs_snat_pool_str_pattern = re.compile("\s*source-address-translation\s(none|{[\s\S]*?})\n", re.MULTILINE)
        vs_snat_pool_str = ''.join(vs_snat_pool_str_pattern.findall(vs_info))
        vs_snat_pool_name = 'none'
        if vs_snat_pool_str != 'none' and vs_snat_pool_str != '':
            vs_snat_pool_pattern = re.compile("\s*pool\s([\s\S]*?)\n", re.MULTILINE)
            vs_snat_pool_name = ''.join(vs_snat_pool_pattern.findall(vs_snat_pool_str))
        vs[25] = vs_snat_pool_name

        vs_source_port_pattern = re.compile("\s*source-port\s([\s\S]*?)\n", re.MULTILINE)
        vs_source_port = ''.join(vs_source_port_pattern.findall(vs_info))
        vs[26] = vs_source_port

        vs_vlans_pattern = re.compile("\s*vlans\s(none|{[\s\S]*?})\n", re.MULTILINE)
        vs_vlans = ''.join(vs_vlans_pattern.findall(vs_info))
        vs[27] = vs_vlans

        ltm_v12_vs_list.append(vs)

    return ltm_v12_vs_list

def get_nsae_ssl_config(filepath,type,version):
    ssl_config_open = open(filepath, encoding='utf-8' ,errors='ignore')
    ssl_config_open_str = ssl_config_open.read()
    nsae_slb_real_map = {}
    nsae_slb_real_list = nsae_slb_real_pattern.findall(ssl_config_open_str)
    for item in nsae_slb_real_list:
        nsae_slb_real_name = re.sub('\s*','',item[0])
        nsae_slb_real_ip = re.sub('\s*','',item[1])
        nsae_slb_real_port = re.sub('\s*','',item[2])
        nsae_slb_real_limit = re.sub('\s*','',item[3])
        nsae_slb_real_check = re.sub('\s*','',item[4])
        nsae_slb_real_map[nsae_slb_real_name] = "##ipport#" + nsae_slb_real_ip + ':' + nsae_slb_real_port + '##limit#' + nsae_slb_real_limit + "##check#" + nsae_slb_real_check + '##'

    nsae_slb_real_disable_map = {}
    nsae_slb_real_disable_list = nsae_slb_real_disable_pattern.findall(ssl_config_open_str)
    for item in nsae_slb_real_disable_list:
        nsae_slb_real_name = re.sub('\s*','',item)
        nsae_slb_real_disable_map[nsae_slb_real_name] = "disable"

    nsae_slb_group_member_map = {}
    nsae_slb_group_member_list = nsae_slb_group_member_pattern.findall(ssl_config_open_str)
    for item in nsae_slb_group_member_list:
        nsae_slb_pool_name = re.sub('\s*','',item[0])
        nsae_slb_pool_member = re.sub('\s*','',item[1])
        nsae_slb_pool_info = nsae_slb_pool_member + '\n'
        if nsae_slb_pool_name in nsae_slb_group_member_map.keys():
            nsae_slb_pool_info = nsae_slb_pool_info + nsae_slb_group_member_map[nsae_slb_pool_name]

        nsae_slb_group_member_map[nsae_slb_pool_name] = nsae_slb_pool_info

    nsae_slb_virtual_map = {}
    nsae_slb_virtual_list = nsae_slb_virtual_pattern.findall(ssl_config_open_str)
    for item in nsae_slb_virtual_list:
        nsae_slb_vs_name = re.sub('\s*','',item[0])
        nsae_slb_vs_ip = re.sub('\s*','',item[1])
        nsae_slb_vs_port = re.sub('\s*','',item[2])
        nsae_slb_vs_info = nsae_slb_vs_ip + ':' + nsae_slb_vs_port
        nsae_slb_virtual_map[nsae_slb_vs_name] = nsae_slb_vs_info

    nsae_slb_policy_map = {}
    nsae_slb_policy_list = nsae_slb_policy_pattern.findall(ssl_config_open_str)
    for item in nsae_slb_policy_list:
        nsae_slb_vs_name = re.sub('\s*','',item[0])
        nsae_slb_vs_pool = re.sub('\s*','',item[1])
        nsae_slb_policy_map[nsae_slb_vs_name] = nsae_slb_vs_pool

    nsae_ssl_host_map = {}
    nsae_ssl_host_list = nsae_ssl_host_pattern.findall(ssl_config_open_str)
    for item in nsae_ssl_host_list:
        nsae_ssl_host_name = re.sub('\s*','',item[0])
        nsae_slb_vs_name = re.sub('\s*','',item[1])
        nsae_ssl_host_map[nsae_slb_vs_name] = nsae_ssl_host_name

    nsae_ssl_vs_list = []
    for vs_name in nsae_slb_virtual_map.keys():
        nsae_ssl_vs_info = ['']*6
        nsae_ssl_vs_info[0] = nsae_slb_virtual_map[vs_name]
        nsae_ssl_vs_info[2] = vs_name
        nsae_ssl_vs_info[1] = ''
        if vs_name in nsae_ssl_host_map.keys():
            nsae_ssl_vs_info[1] = nsae_ssl_host_map[vs_name]
        nsae_ssl_vs_pool_name = ''
        nsae_ssl_vs_member_simple = ''
        nsae_ssl_vs_member_detail = ''
        if vs_name in nsae_slb_policy_map.keys():
            nsae_ssl_vs_pool_name = nsae_slb_policy_map[vs_name].strip()
            if nsae_ssl_vs_pool_name in nsae_slb_group_member_map.keys():
                real_members = nsae_slb_group_member_map[nsae_ssl_vs_pool_name].strip()
                real_members_list = real_members.split('\n')
                vs_member_detail_info = ''
                vs_member_simple_info = ''
                for real_member in real_members_list:
                    if real_member != '' and real_member is not None:
                        real_member_info = nsae_slb_real_map[real_member]
                        real_member_ipport_pattern = re.compile("##ipport#([\s\S]*?)##", re.MULTILINE)
                        real_member_ipport = ''.join(real_member_ipport_pattern.findall(real_member_info))
                        real_member_limit_pattern = re.compile("##limit#([\s\S]*?)##", re.MULTILINE)
                        real_member_limit = ''.join(real_member_limit_pattern.findall(real_member_info))
                        real_member_check_pattern = re.compile("##check#([\s\S]*?)##", re.MULTILINE)
                        real_member_check = ''.join(real_member_check_pattern.findall(real_member_info))
                        if real_member in nsae_slb_real_disable_map.keys():
                            vs_member_detail_info += real_member_ipport + ' disable' + ' l:' + real_member_limit + ' c:' + real_member_check + '\n'
                        else:
                            vs_member_detail_info += real_member_ipport + ' enable' + ' l:' + real_member_limit + ' c:' + real_member_check + '\n'
                            vs_member_simple_info += real_member_ipport + '\n'

                nsae_ssl_vs_member_simple = vs_member_simple_info.strip('\n')
                nsae_ssl_vs_member_detail = vs_member_detail_info.strip('\n')
            elif nsae_ssl_vs_pool_name in nsae_slb_real_map.keys():
                real_member_info = nsae_slb_real_map[nsae_ssl_vs_pool_name]
                real_member_ipport_pattern = re.compile("##ipport#([\s\S]*?)##", re.MULTILINE)
                real_member_ipport = ''.join(real_member_ipport_pattern.findall(real_member_info))
                real_member_limit_pattern = re.compile("##limit#([\s\S]*?)##", re.MULTILINE)
                real_member_limit = ''.join(real_member_limit_pattern.findall(real_member_info))
                real_member_check_pattern = re.compile("##check#([\s\S]*?)##", re.MULTILINE)
                real_member_check = ''.join(real_member_check_pattern.findall(real_member_info))
                vs_member_detail_info = real_member_ipport + ' enable' + ' l:' + real_member_limit + ' c:' + real_member_check
                vs_member_simple_info = ''
                if nsae_ssl_vs_pool_name in nsae_slb_real_disable_map.keys():
                    vs_member_detail_info = real_member_ipport + ' disable' + ' l:' + real_member_limit + ' c:' + real_member_check
                else:
                    vs_member_simple_info = vs_member_simple_info + real_member_ipport

                nsae_ssl_vs_member_simple = vs_member_simple_info
                nsae_ssl_vs_member_detail = vs_member_detail_info

        nsae_ssl_vs_info[3] = nsae_ssl_vs_pool_name
        nsae_ssl_vs_info[4] = nsae_ssl_vs_member_simple
        nsae_ssl_vs_info[5] = nsae_ssl_vs_member_detail
        nsae_ssl_vs_list.append(nsae_ssl_vs_info)

    ssl_config_open.close()
    return nsae_ssl_vs_list

def main():
    get_device_list()
    now_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    ltm_writer = pd.ExcelWriter(result_path + 'ltm_'+now_time+'.xlsx')
    nsae_writer = pd.ExcelWriter(result_path + 'nsae_'+now_time+'.xlsx')
    citrix_writer = pd.ExcelWriter(result_path + 'citrix_'+now_time+'.xlsx')
    gtm_writer = pd.ExcelWriter(result_path + 'gtm_'+now_time+'.xlsx')

    for device_name in device_analyzer_list:

        file_path = device_path_map[device_name]
        type = device_list_map[device_name]['type']
        version = device_list_map[device_name]['version']
        print(file_path)
        if type == 'ltm':
            ltm_list = get_ltm_config(file_path,type,version)
            ltm_df = pd.DataFrame(ltm_list, columns=['vs_name', 'vs_conn', 'vs的ip_port', 'vs_status', 'vs_protocol', 'vs_persist_name', 'vs_persist_mothod', 'vs_persist_timeout', 'persist_cookie_encrypt', 'persist_cookie_name', 'persist_cookie_method', 'vs_pool_name', 'vs_balanc_mode', 'vs_pool_monitor', 'members_info_simple', 'members_info_detail', 'fastl4_profile_name', 'fastl4_timeout', 'fastl4_pva', 'tcp_profile_name', 'tcp_profile_timeout', 'http_profile_name', 'http_profile_xforwarded', 'other_profile', 'vs_rules', 'vs_snat_pool_name', 'vs_source_port', 'vs_vlans'])
            ltm_df.to_excel(ltm_writer, sheet_name=device_name, index=False)
        elif type == 'nsae':
            nsae_ssl_vs_list = get_nsae_ssl_config(file_path, type, version)
            nsae_df = pd.DataFrame(nsae_ssl_vs_list, columns=['ssl_vs_ipport', 'ssl_host', 'ssl_vs_name', 'ssl_pool_name', 'members_info_simple', 'members_info_detail'])
            nsae_df.to_excel(nsae_writer, sheet_name=device_name, index=False)
        elif type == 'citrix':
            citrix_list = []
            citrix = [''] * 4
            citrix[0] = device_name
            citrix[1] = type
            citrix[2] = device_list_map[device_name]['version']
            citrix[3] = device_path_map[device_name]
            citrix_list.append(citrix)
            citrix_df = pd.DataFrame(citrix_list, columns=['device_name', 'type', 'version', 'path'])
            citrix_df.to_excel(citrix_writer, sheet_name=device_name, index=False)
        elif type == 'gtm':
            gtm_list = []
            gtm = [''] * 4
            gtm[0] = device_name
            gtm[1] = type
            gtm[2] = device_list_map[device_name]['version']
            gtm[3] = device_path_map[device_name]
            gtm_list.append(gtm)
            gtm_df = pd.DataFrame(gtm_list, columns=['device_name', 'type', 'version', 'path'])
            gtm_df.to_excel(gtm_writer, sheet_name=device_name, index=False)

    ltm_writer.close()
    nsae_writer.close()
    citrix_writer.close()
    gtm_writer.close()


if __name__ == '__main__':
    main()






