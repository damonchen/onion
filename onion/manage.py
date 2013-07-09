#coding=utf-8

import os, sys, logging, shlex
from optparse import make_option
from onion.utils.common import load_apps, extract_dirs
from onion.core.web import Application, run_simple
from onion.core.commands import Command, execute_command_line

logger = logging.getLogger('onion')

DEFAULT_APPS_NAME = 'apps'
__commands__ = {}


def make_application(debug=None, apps_name=DEFAULT_APPS_NAME, project_path=None,
                settings_file='settings.yaml'):

    apps_path = None
    if project_path is not None:
        apps_path = os.path.normpath(os.path.join(project_path, apps_name))

    if apps_path is not None and apps_path not in sys.path:
        sys.path.insert(0, apps_path)
        
    apps, settings = load_apps(apps_path, settings_file)

    debug_flag = settings.GLOBAL.DEBUG
    if debug or debug_flag:
        logger.setLevel(logging.DEBUG)
        logger.info('** Loading Application with debug ...')

    application = Application(apps, settings, project_path)
    return application


    
class MakeAppCommand(Command):
    name = 'makeapp'
    args = 'app_name'
    help = 'Create a new app according the appname parameter.'
    register = True

    option_list = (
        make_option('-f', action='store_true', dest='force',
            help='Force to create app directory.'),
    )
    has_options = True

    def handle(self, options, global_options, *args):
        if not args:
            appname = ''
            while not appname:
                appname = raw_input('Please enter an app name:')
        else:
            appname = args[0]


        app_path = appname.replace('.', '//')
        if os.path.exists(DEFAULT_APPS_NAME):
            path = os.path.join(DEFAULT_APPS_NAME, app_path)
        else:
            path = app_path

        ans = '-1'
        if os.path.exists(path):
            if options.force:
                ans = 'y'
            while ans not in ('y', 'n'):
                ans = raw_input('The app directory has been existed.  do you want to overwrite it?(y/N)')
                if not ans:
                    ans = 'n'
        else:
            ans = 'y'

        if ans == 'y':
            extract_dirs('onion', 'template_files/app', path, verbose=global_options.verbose)


class MakeProjectCommand(Command):
    name = 'makeproject'
    help = 'Create a new project directory according the project name.'
    args = 'project_name'

    option_list = (
        make_option('-f', action='store_true', dest='force',
            help='Force to create project directory.'),        
    )
    has_options = True
    register = True

    def handle(self, options, global_options, *args):
        if not args:
            project_name = ''
            while not project_name:
                project_name = raw_input('Please enter project name:')
        else:
            project_name = args[0]

        ans = -1
        if os.path.exists(project_name):
            if options.force:
                ans = 'y'
            while ans not in ('y', 'n'):
                ans = raw_input('The project directory has been existed, do you want to overwrite it?(y/N)')
                if not ans:
                    ans = 'n'
        else:
            ans = 'y'

        if ans == 'y':
            extract_dirs('onion', 'template_files/project', project_name,
                    verbose=global_options.verbose)
            os.rename(os.path.join(project_name, '.gitignore.template'), 
                    os.path.join(project_name, '.gitignore'))

class RunserverCommand(Command):
    name = 'runserver'
    help = 'Start a new development server.'
    args = ''
    has_options = True
    option_list = (
        make_option('-h', dest='hostname', default='localhost',
            help='Hostname or IP.'),
        make_option('-p', dest='port', type='int', default=8080,
            help='Port number.'),
        make_option('--no-reload', dest='reload', action='store_false', default=True,
            help='If auto reload the development server. Default is  True.'),
        make_option('--no-debug', dest='debug', action='store_false', default=False,
            help='Not used as debug model, Default is False'),
        make_option('-a', '--apps', dest='apps', action='store_true', default=DEFAULT_APPS_NAME,
            help='The real project apps folder name, Default is apps')
    )
    register = True
    develop = False

    def handle(self, options, global_options, *args):
        if self.develop:
            app = make_application(options.debug, project_path=global_options.project,
                        settings_file=global_options.settings)
        else:
            logger.debug(global_options.project)

            app = make_application(options.debug, project_path=global_options.project, apps_name=options.apps,
                    settings_file=global_options.settings)

        logger.info('start applicaiton with %s:%s' %(options.hostname, options.port)) 
        run_simple(options.hostname, options.port, app, options.reload)


def call(args=None):
    
    def callback(global_options):
        apps_path = global_options.apps_path or os.path.join(os.getcwd(), DEFAULT_APPS_NAME)
        if os.path.exists(apps_path) and apps_path not in sys.path:
            sys.path.insert(0, apps_path)

        #install_config(apps_path)

    if isinstance(args, (unicode, str)):
        args = shlex.split(args)

    execute_command_line(args or sys.argv, 'onion', callback)

def main():
    call()

if __name__ == '__main__':
    main()
