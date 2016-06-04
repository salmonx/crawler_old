
from worker_filter import Filter

urls = open('top-1m.txt.csv').read().strip().split('\n')
for url in urls:
    url = url.split(',')[1]
    if url.endswith('.cn'):
        print url

