#!/usr/bin/python
import requests, sys



def checkDNSAPI(api=None):
    test_dom = 'baidu.com'
    api_url = api
    data = {
        'get_domains': test_dom,
    }

    try:
        data_val = requests.post(api_url, data=data, timeout=120).json()
        return 0
    except Exception as e:
        return 1


if __name__ == '__main__':
    if sys.argv[1] == "idc_api":
        print(checkDNSAPI(api="http://127.0.0.1:8002/domain-checker/"))
    elif sys.argv[1] == "china_api":
        print(checkDNSAPI(api="http://120.24.167.117:8050/domain-checker/"))


