#coding=utf-8

'''
@date: 2013-07-06
@author: damon.chen
'''

class Middleware(object):
    NICE = 500

    def __init__(self, application, settings):
        self.application = application
        self.settings = settings
