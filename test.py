import re

test = '2018的下半年，9份， 27'
pattern = re.compile(r'(\d)+(年|月|日)')
res = pattern.findall(test)
print(res)