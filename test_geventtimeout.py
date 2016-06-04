import requests
import gevent
#import gevent.monkey
from gevent import monkey
#import urllib
 
#gevent.monkey.patch_all(thread=False)
monkey.patch_all(thread=False)
 
def test():
    try:
        #    urllib.urlopen("http://www.twitter.com")
        url = 'http://www.google.com'
        with gevent.Timeout(1, False) as timeout:
            req = requests.get(url, timeout=(3,5))
            print url, len(req.content)
    except Exception ,e:
        print e
        #url = 'http://www.github.com'
                    

if __name__ == "__main__":
    g = gevent.spawn(test)
    g.join()
