import requests

url = 'http://127.0.0.1:8000/domain-checker/'

x = requests.post(url, data=['jiab888.net','google.dom'])

# print('hey')
print(x.content)