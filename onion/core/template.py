#coding=utf-8

import os
from jinja2 import Environment, FileSystemLoader
from tornado.template import BaseLoader


class FileLoader(BaseLoader):

    def __init__(self,  root_directory, **kwargs):                                                                                                      
        BaseLoader.__init__(self, **kwargs)
        self.root = os.path.abspath(root_directory)

        self.loader = FileSystemLoader(self.root)
        self.env = Environment(loader=self.loader)

    def load(self, template_name, parent_path=None):

        tmpl = self.env.get_template(template_name)
        if tmpl is not None:
            setattr(tmpl, 'generate', tmpl.render)

        return tmpl

    def reset(self):
        if hasattr(self.env, 'bytecode_cache')and self.env.bytecode_cache:
            self.env.bytecode_cache.clear()

