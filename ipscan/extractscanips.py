#! /bin/python
import pickle
from redis_inc import RedisConnection, RedisQueueConnection


def test():
    runque = RedisQueueConnection('scan').conn
    #########runque.flushdb()
    size =  runque.qsize()
    t = 0
    cnt = 0
    port = 0
    data = []
    if size == 0:
        return
    tmp = runque.get()
    runque.put(tmp)
    port, iph, ipl = tmp.split(' ') 

    print port, size

    raw_input('confirm:')

    while runque.qsize() > 0:
        tmp =  runque.get()
        try:
            t += len(tmp.split(' ')[-1].split(','))
            data.append(tmp)
        except:
            pass
        cnt += 1

   
    f = "china%s_%s_%s.txt" % (port, size, t)
    fp = open(f, 'w')
    for item in data:
        fp.write(item + '\n')

    fp.close()


test()
