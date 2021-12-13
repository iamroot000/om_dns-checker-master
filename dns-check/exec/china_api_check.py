#!/usr/bin/python



import requests



test_dom = 'baidu.com'

api_url = 'http://120.24.167.117:8050/domain-checker/'

data = {

                'get_domains': test_dom,

}





try:

	data_val = requests.post(api_url, data=data, timeout=120).json()

	print(0)

except Exception as e:

	print(1)


