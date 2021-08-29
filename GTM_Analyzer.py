import datetime
import json
import re
import configparser
import pandas as pd

ipv4_gtm_config_path = 'C:\\Users\\Administrator\\Desktop\\F5_peizhi\\ipv4_gtm.txt'
ipv6_gtm_config_path = 'C:\\Users\\Administrator\\Desktop\\F5_peizhi\\ipv6_gtm.txt'
result_path = 'E:\\result\\'



ipv4_gtm_config_open = open(ipv4_gtm_config_path, encoding='utf-8')
ipv6_gtm_config_open = open(ipv6_gtm_config_path, encoding='utf-8')

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
GTM_WIDEIP_POOLS_RE_STR = config.get('GTM', 'GTM_WIDEIP_POOLS_RE_STR')
GTM_WIDEIP_RE_STR = config.get('GTM', 'GTM_WIDEIP_RE_STR')

vs_pattern = re.compile(GTM_VS_RE_STR, re.MULTILINE)
server_pattern = re.compile(GTM_SERVER_RE_STR, re.MULTILINE)
member_pattern = re.compile(GTM_MEMBER_RE_STR, re.MULTILINE)
pool_pattern = re.compile(GTM_POOL_RE_STR, re.MULTILINE)
wideip_pools_pattern = re.compile(GTM_WIDEIP_POOLS_RE_STR, re.MULTILINE)
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
    ips = []
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
                    ips.append(server_ip_data_v4[server])
                elif pool_type == 'aaaa' and server in server_ip_data_v6.keys():
                    ips.append(server_ip_data_v6[server])
        elif pool_type == 'cname' or pool_type == 'mx':
                ips.append(server_vs + '_' + member_status)

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
                pool_a_data_v4[pool_name] = ips
            elif pool_type == 'cname':
                pool_cname_data_v4[pool_name] = ips
            elif pool_type == 'mx':
                pool_mx_data_v4[pool_name] = ips
        if version == 'v6':
            if pool_type == 'aaaa':
                pool_aaaa_data_v6[pool_name] = ips
            elif pool_type == 'cname':
                pool_cname_data_v6[pool_name] = ips
            elif pool_type == 'mx':
                pool_mx_data_v6[pool_name] = ips

    return pool_members


def get_gtm_pools(version):
    gtm_pools = []
    if version == 'v4':
        gtm_pools = pool_pattern.findall(ipv4_gtm_config)
    elif version == 'v6':
        gtm_pools = pool_pattern.findall(ipv6_gtm_config)

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


def wideip_pools_format(pools_str, wideip_type, version):
    wideip_pools_ret = []
    wideip_pools = wideip_pools_pattern.findall(pools_str)
    for item in wideip_pools:
        pool = {}
        ips = []
        name = item[0].strip()
        pool['name'] = name
        pool['order'] = item[1].strip()
        pool['ratio'] = item[2].strip()
        if version == 'v4':
            if wideip_type == 'a' and name in pool_a_data_v4.keys():
                ips = pool_a_data_v4[name]
            if wideip_type == 'cname' and name in pool_cname_data_v4.keys():
                ips = pool_cname_data_v4[name]
            if wideip_type == 'mx' and name in pool_mx_data_v4.keys():
                ips = pool_mx_data_v4[name]
        elif version == 'v6':
            if wideip_type == 'aaaa' and name in pool_aaaa_data_v6.keys():
                ips = pool_aaaa_data_v6[name]
            if wideip_type == 'cname' and name in pool_cname_data_v6.keys():
                ips = pool_cname_data_v6[name]
            if wideip_type == 'mx' and name in pool_mx_data_v6.keys():
                ips = pool_mx_data_v6[name]
        pool['ips'] = ips
        wideip_pools_ret.append(pool)

    return wideip_pools_ret

def wideip_pools_cname_format(pools_cname_str, version):
    wideip_pools_cname_ret = []
    wideip_pools_cname = wideip_pools_pattern.findall(pools_cname_str)
    for item in wideip_pools_cname:
        cname_pool = {}
        domains = []
        name = item[0].strip()
        cname_pool['name'] = name
        cname_pool['order'] = item[1].strip()
        cname_pool['ratio'] = item[2].strip()
        if version == 'v4':
            if name in pool_cname_data_v4.keys():
                domains = pool_cname_data_v4[name]
        elif version == 'v6':
            if name in pool_cname_data_v6.keys():
                domains = pool_cname_data_v6[name]

        cname_pool['domains'] = domains
        wideip_pools_cname_ret.append(cname_pool)

    return wideip_pools_cname_ret



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
        wideip['pool_lb_mode'] = item[3].strip()
        wideip['pools'] = wideip_pools_format(item[4].strip(), item[0].strip(), version)
        wideip['pools_cname'] = wideip_pools_cname_format(item[5].strip(), version)
        gtm_wideip_ret.append(wideip)
    return gtm_wideip_ret


def main():
    get_gtm_servers('v4')
    get_gtm_servers('v6')
    get_gtm_pools('v4')
    get_gtm_pools('v6')
    ipv4_wideips = get_gtm_wideip('v4')
    ipv6_wideips = get_gtm_wideip('v6')
    result_dir = {}

    for wideip in ipv4_wideips:
        if wideip['type'] == 'a' or wideip['type'] == 'mx':
            wideip_str = wideip['wideip']
            if wideip_str not in result_dir.keys():
                records = [''] * 8
                result_dir[wideip_str] = records

            pools = wideip['pools']
            ips = []
            a_order = 99999
            a_order_pool = ''
            for pool in pools:
                ips.append(pool['ips'])
                pool_order = int(pool['order'])
                if pool_order <= a_order:
                    a_order = pool_order
                    a_order_pool = pool['name']

            pools_cname = wideip['pools_cname']
            domains = []
            cname_order = 99999
            cname_order_domain_ga = ''
            cname_order_domain_top = ''
            for pool_cname in pools_cname:
                domas = pool_cname['domains']
                cnames = ''
                for item in domas:
                    it = re.split('_', item)
                    cname = it[0]
                    domains.append(cname)
                    cnames = cname + '\n' + cnames
                    if it[1].strip() == 'enabled':
                        cname_order_domain_top = cname

                    pool_order = int(pool_cname['order'])
                    if pool_order <= cname_order:
                        cname_order = pool_order
                        cname_order_domain_ga = cnames.strip()

            ips_list = []
            for ip in ips:
                ips_list = ips_list + ip
            ips_list = list(set(ips_list))
            ips_str = '\n'.join(ips_list)
            if wideip['type'] == 'mx':
                ips_str = ips_str.replace('_enabled','')

            domains_list = list(set(domains))
            domains_str = '\n'.join(domains_list)

            result_dir[wideip_str][0] = wideip_str
            if wideip['type'] == 'a':
                result_dir[wideip_str][1] = ips_str
                result_dir[wideip_str][3] = domains_str
                pool_lb_mode = wideip['pool_lb_mode'].strip()
                if cname_order_domain_ga != '' and pool_lb_mode == 'global-availability':
                    if cname_order < a_order:
                        result_dir[wideip_str][5] = cname_order_domain_ga
                    else:
                        result_dir[wideip_str][5] = a_order_pool
                elif cname_order_domain_top != '' and pool_lb_mode == 'topology':
                    result_dir[wideip_str][5] = cname_order_domain_top

            elif wideip['type'] == 'mx':
                result_dir[wideip_str][7] = ips_str


    for wideip in ipv6_wideips:

        if wideip['type'] == 'aaaa':
            wideip_str = wideip['wideip']
            if wideip_str not in result_dir.keys():
                records = [''] * 8
                result_dir[wideip_str] = records

            pools = wideip['pools']
            ips = []
            a_order = 99999
            a_order_pool = ''
            for pool in pools:
                ips.append(pool['ips'])
                pool_order = int(pool['order'])
                if pool_order <= a_order:
                    a_order = pool_order
                    a_order_pool = pool['name']

            pools_cname = wideip['pools_cname']
            domains = []
            cname_order = 99999
            cname_order_domain_ga = ''
            cname_order_domain_top = ''
            for pool_cname in pools_cname:
                domas = pool_cname['domains']
                cnames = ''
                for item in domas:
                    it = re.split('_', item)
                    cname = it[0]
                    cnames = cname + '\n' + cnames
                    domains.append(cname)
                    if it[1].strip() == 'enabled':
                        cname_order_domain_top = cname

                pool_order = int(pool_cname['order'])
                if pool_order <= cname_order:
                    cname_order = pool_order
                    cname_order_domain_ga = cnames.strip()

            ips_list = []
            for ip in ips:
                ips_list = ips_list + ip
            ips_list = list(set(ips_list))
            ips_str = '\n'.join(ips_list)


            domains_list = list(set(domains))
            domains_str = '\n'.join(domains_list)

            result_dir[wideip_str][0] = wideip_str
            result_dir[wideip_str][2] = ips_str
            result_dir[wideip_str][4] = domains_str
            pool_lb_mode = wideip['pool_lb_mode'].strip()
            if cname_order_domain_ga != '' and pool_lb_mode == 'global-availability':
                if cname_order < a_order:
                    result_dir[wideip_str][6] = cname_order_domain_ga
                else:
                    result_dir[wideip_str][6] = a_order_pool
            elif cname_order_domain_top != '' and pool_lb_mode == 'topology':
                result_dir[wideip_str][6] = cname_order_domain_top

    result_all_domain_list = result_dir.values()
    df = pd.DataFrame(result_all_domain_list, columns=['域名','A记录','AAAA记录','ipv4_CNAME_记录','ipv6_CNAME_记录','ipv4_优先_CNAME','ipv6_优先_CNAME','MX记录'])
    now_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    respath = result_path + "result_all_domain_" + now_time + ".xlsx"
    df.to_excel(respath, index=False)
    print('解析完成：'+respath)

if __name__ == '__main__':
    main()
