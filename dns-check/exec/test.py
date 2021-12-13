import requests, sys
r = sys.argv[1]
data = {'get_domains': str(r)}
idc = requests.post('http://127.0.0.1:8002/domain-checker/', data=data, timeout=120)
print idc.json()
