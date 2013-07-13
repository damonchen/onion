#coding=utf-8

'''
@date: 2013-07-06
@author: damon.chen
'''

import tornado.httpserver
from tornado.web import Application as Application_, RequestHandler as RequestHandler_


class Application(Application_):

    def __init__(self, apps, settings, project_path=None, debug=None):
        handlers = self.get_apps_handlers(apps)


        if project_path is not None:
            settings.PROJECT_PATH = project_path

        if debug is not None:
            settings.DEBUG = debug

        Application_.__init__(self, handlers, **settings)
        

    def get_apps_handlers(self, apps):
        handlers = []
        for app in apps:
            handlers.extend(app.route.handlers)

        return handlers


class BaseHandler(RequestHandler_):

    def render(self, template_name, **kwargs):
        namespace = self.get_template_namespace()
        namespace.update(kwargs)
        html = self.render_string(template_name, namespace)
        self.finish(html)


def run_simple(hostname, port, app, app_reload):
    #if app_reload:
        #app.settings.DEBUG = True

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()

