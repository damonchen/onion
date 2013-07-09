#coding=utf-8

'''
@date: 2013-07-06
@author: damon.chen
'''

import logging


logger = logging.getLogger('onion')


_receivers = {}
_called = {}

def bind(topic, signal=None, nice=1):

    def _(func):
        if not topic in _receivers:
            receivers = _receivers[topic] = []
        else:
            receivers = _receivers[topic]

        if callable(func):
            func_name = '%s.%s' %(func.__module__, func.__name__)
        else:
            func_name = func
            func = None

        _f = {'func': func, 'signal': signal, 'func_name':  func_name}
        receivers.append(_f)
        return func

    return _


def call(sender, topic, *args, **kwargs):
    if not topic in _receivers:
        return None

    items = _receivers[topic]
    
    for item in items:
        func = item['func']

        if callable(func):
            kw = kwargs.copy()
            try:
                func(sender, *args, **kw)
            except Exception as e:
                logger.exception("Calling dispatch point [%s] %s(%r, %r) with error %s!"  %(topic, func, args, kw, e.message))
                raise e

    
def call_once(sender, topic, *args, **kwargs):
    signal = kwargs.get('signal')
    key = '%s-%s' %(topic, signal)

    if key in _called:
        return None
    else:
        call(sender, topic, *args, **kwargs)
        _called[key] = True


