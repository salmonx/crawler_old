# get dict from dict.txt




def getdict():

    lines = open('dict.txt').read().strip().split('\n')

    urldict = dict()

    for line in lines:
        cnt, url = line.split()
        urldict[url] = int(cnt)
    
    return urldict


