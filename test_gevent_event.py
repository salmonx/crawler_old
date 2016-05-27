import gevent
from gevent.event import Event
evt = Event()
def setter():
    global e
    print('In setter')
    gevent.sleep(2)
    print("After first sleep")
    evt.set()     #first set
    evt.clear()
    e = Event()
    print 'second sleep'
    gevent.sleep(3)
    e.set()     #second set
    print 'end of setter'

def waiter():
    print("in waiter")
    evt.wait()     #first wait
    print 'after first wait'
    print 
    e.wait()     #second wait
    print 'end of waiter'

gevent.joinall([
    gevent.spawn(setter),
    gevent.spawn(waiter),
])
