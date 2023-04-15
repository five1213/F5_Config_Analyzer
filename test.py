import re

ssl_vs ='10.6.2.10:443'
if re.match(r"^(10.6.20.[\s\S]*?)$", ssl_vs) or re.match(r"^(2404:bc0:3:114[\s\S]*?)$", ssl_vs):
    print('y')
else:
    print('n')