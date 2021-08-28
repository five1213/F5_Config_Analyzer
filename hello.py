import json
import re
import configparser

ipv4_gtm_config_open = open('C:\\Users\\Administrator\\Desktop\\F5_peizhi\\ipv4_gtm.txt', encoding='utf-8')
ipv6_gtm_config_open = open('C:\\Users\\Administrator\\Desktop\\F5_peizhi\\ipv6_gtm.txt', encoding='utf-8')

# poolconfig = open('ipv4_gtm_pool.txt', 'a', encoding='utf-8')

ipv4_gtm_config = ipv4_gtm_config_open.read()
ipv6_gtm_config = ipv6_gtm_config_open.read()

ipv4_gtm_config_open.close()
ipv6_gtm_config_open.close()

port_json_str_open = open('config/port.json', encoding='utf-8')
port_json_str = port_json_str_open.read()

port_json_str_open.close()

config = configparser.ConfigParser()
config.read('config/config.ini', encoding='utf-8')

GTM_VS_RE_STR = config.get('GTM', 'GTM_VS_RE_STR')
GTM_SERVER_RE_STR = config.get('GTM', 'GTM_SERVER_RE_STR')
GTM_MEMBER_RE_STR = config.get('GTM', 'GTM_MEMBER_RE_STR')
GTM_POOL_RE_STR = config.get('GTM', 'GTM_POOL_RE_STR')
GTM_WIDEIP_RE_STR = config.get('GTM', 'GTM_WIDEIP_RE_STR')

vs_pattern = re.compile(GTM_VS_RE_STR, re.MULTILINE)
server_pattern = re.compile(GTM_SERVER_RE_STR, re.MULTILINE)
member_pattern = re.compile(GTM_MEMBER_RE_STR, re.MULTILINE)
pool_pattern = re.compile(GTM_POOL_RE_STR, re.MULTILINE)
wideip_pattern = re.compile(GTM_WIDEIP_RE_STR, re.MULTILINE)

ports_dir = json.loads(port_json_str)
ports_data = dict([val, key] for key, val in ports_dir.items())

server_ip_data_v4 = {}
server_ip_data_v6 = {}
server_ip_data_disable_v4 = {}
server_ip_data_disable_v6 = {}
pool_a_data_v4 = {}
pool_cname_data_v4 = {}
pool_mx_data_v4 = {}
pool_aaaa_data_v6 = {}
pool_cname_data_v6 = {}
pool_mx_data_v6 = {}
server_ip_data_v4_new = {}


def servers_format(vs_info, server_name, server_ip, server_status,version):
    vs_info_ret = {}
    vs_infos = vs_pattern.findall(vs_info)
    if len(list(vs_infos)) == 0:
        if server_status == 'enabled':
            if version == 'v4':
                server_ip_data_v4[server_name] = server_ip
            elif version == 'v6':
                server_ip_data_v6[server_name] = server_ip
        else:
            if version == 'v4':
                server_ip_data_disable_v4[server_name] = server_ip
            elif version == 'v6':
                server_ip_data_disable_v6[server_name] = server_ip

    for vs in vs_infos:
        vs_info_ret['vs_name'] = vs[0].strip()
        vs_info_ret['vs_ip_port'] = vs[1].strip()
        vs_info_ret['vs_status'] = vs[2].strip()
        vs_info_ret['vs_monitor'] = vs[3].strip()

        if vs[2].strip() == 'enabled' and server_status == 'enabled':
            if version == 'v4':
                server_ip_data_v4[server_name] = server_ip
            elif version == 'v6':
                server_ip_data_v6[server_name] = server_ip
        else:
            if version == 'v4':
                server_ip_data_disable_v4[server_name] = server_ip
            elif version == 'v6':
                server_ip_data_disable_v6[server_name] = server_ip

    return vs_info_ret


def get_gtm_servers(version):
    gtm_servers = []
    if version == 'v4':
        gtm_servers = server_pattern.findall(ipv4_gtm_config)
    elif version == 'v6':
        gtm_servers = server_pattern.findall(ipv6_gtm_config)
    get_gtm_servers_rt = {}
    print(len(list(gtm_servers)))
    for item in gtm_servers:
        get_gtm_servers_rt['server_name'] = item[0].strip()
        get_gtm_servers_rt['server_ip'] = item[1].strip()
        get_gtm_servers_rt['datacenter'] = item[2].strip()
        get_gtm_servers_rt['server_status'] = item[3].strip()
        get_gtm_servers_rt['server_monitor'] = item[4].strip()
        get_gtm_servers_rt['vs_info'] = servers_format(item[6].strip(), item[0].strip(), item[1].strip(),
                                                       item[3].strip(), version)

    return get_gtm_servers_rt


def members_format(members_info, pool_name, pool_type, pool_status,version):
    pool_members = []
    members_infos = member_pattern.findall(members_info)
    ips = ''
    for member in members_infos:
        pool_member = {}
        server_vs = member[0].strip()
        member_status = member[1].strip()
        member_order = member[2].strip()
        member_ratio = member[3].strip()
        server = ''
        vs = ''
        if pool_type == 'a' or pool_type == 'aaaa':
            spl = re.split(':',server_vs)
            server = spl[0]
            vs = spl[1]
            if member_status == 'enabled':
                if pool_type == 'a' and server in server_ip_data_v4.keys():
                    ips = ips + '\n' + server_ip_data_v4[server]
                elif pool_type == 'aaaa' and server in server_ip_data_v6.keys():
                    ips = ips + '\n' + server_ip_data_v6[server]
        elif pool_type == 'cname' or pool_type == 'mx':
                ips = ips + '\n' + server_vs + '_' + member_status

        pool_member['server_vs'] = server_vs
        pool_member['server'] = server
        pool_member['vs'] = vs
        pool_member['member_status'] = member_status
        pool_member['member_order'] = member_order
        pool_member['member_ratio'] = member_ratio
        pool_members.append(pool_member)

    if pool_status == 'enabled':
        if version == 'v4':
            if pool_type == 'a':
                pool_a_data_v4[pool_name] = ips.strip('\n')
            elif pool_type == 'cname':
                pool_cname_data_v4[pool_name] = ips.strip('\n')
            elif pool_type == 'mx':
                pool_mx_data_v4[pool_name] = ips.strip('\n')
        if version == 'v6':
            if pool_type == 'aaaa':
                pool_aaaa_data_v6[pool_name] = ips.strip('\n')
            elif pool_type == 'cname':
                pool_cname_data_v6[pool_name] = ips.strip('\n')
            elif pool_type == 'mx':
                pool_mx_data_v6[pool_name] = ips.strip('\n')

    return pool_members


def get_gtm_pools(version):
    gtm_pools = []
    if version == 'v4':
        gtm_pools = pool_pattern.findall(ipv4_gtm_config)
    elif version == 'v6':
        gtm_pools = pool_pattern.findall(ipv6_gtm_config)

    # print(len(gtm_pools))

    gtm_pools_ret = []
    for item in gtm_pools:
        pool = {}
        pool['pool_type'] = item[0].strip()
        pool['pool_name'] = item[1].strip()

        pool['pool_status'] = item[2].strip()
        pool['fallback_mode'] =  item[3].strip()
        pool['load_balancing_mode'] = item[4].strip()
        pool['ttl'] = item[6].strip()
        pool['members_info'] = members_format(item[5].strip(), item[1].strip(), item[0].strip(), item[2].strip(), version)
        gtm_pools_ret.append(pool)
    return gtm_pools_ret


def get_gtm_wideip(version):
    gtm_wideip = []
    if version == 'v4':
        gtm_wideip = wideip_pattern.findall(ipv4_gtm_config)
    elif version == 'v6':
        gtm_wideip = wideip_pattern.findall(ipv6_gtm_config)
    gtm_wideip_ret = []
    for item in gtm_wideip:
        wideip = {}
        wideip['type'] = item[0].strip()
        wideip['wideip'] = item[1].strip()
        wideip['status'] = item[2].strip()
        wideip['pool-lb-mode'] = item[3].strip()
        wideip['pools'] = item[4].strip()
        wideip['pools-cname'] = item[6].strip()
        gtm_wideip_ret.append(wideip)
    return gtm_wideip_ret


def main():
    # get_gtm_servers('v6')
    # get_gtm_servers('v6')
    # get_gtm_pools('v6')
    # poolconfig.close()
    # get_gtm_pools('v6')
    it1 = get_gtm_wideip('v4')
    it2 = get_gtm_wideip('v6')
    print(len(list(it1)))
    print(len(list(it2)))
    #
    # for v in server_ip_data_v4_new.keys():
    #     poolconfig.write(v + '\n')
    # print(pool_cname_data_v4['pool_CDNS_mmerchant.ccb.com'])
    # print(pool_cname_data_v6['pool_CDNS_mmerchant.ccb.com'])
    # print(server_ip_data)
    # print(server_ip_data_disable_v4)
    # print(server_ip_data_disable_v6)
    # for item in items:
    #     pass
    # # print(server_ip_data)
    # print(server_ip_data_disable)
    #     if item['server_name'] == '"ctc_host_ open.buy.ccb.com"':
    #         print(item)
    #         print(type(item['vs_info']))
    #         print(item['vs_info'])
    #     if item['server_name'] == '3ds.acqwbts.ccb.com_server':
    #         print(item)
    #         print(type(item['vs_info']))
    #         print(item['vs_info'])
    #     if item['server_name'] == 'BJCA-CUC-GSLB_ns4':
    #         print(item)
    #         print(type(item['vs_info']))
    #         print(item['vs_info'])
    #
    # print(server_ip_data['"ctc_host_ open.buy.ccb.com"'])
    # print(server_ip_data['3ds.acqwbts.ccb.com_server'])
    # print('BJCA-CUC-GSLB_ns4' in server_ip_data.keys())


if __name__ == '__main__':
    main()
