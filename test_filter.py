import requests
from worker_filter import Filter

f = Filter()


url = 'https://www.amazon.com/'

r = requests.get(url)

print f.filter_encoding(url, r.headers, r.content)
