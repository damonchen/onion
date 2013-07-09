#coding=utf-8

##############################################
# this module is desired by uliweb
##############################################

import sys, os, inspect
import logging
from optparse import make_option, OptionParser, IndentedHelpFormatter

import onion
#from onion.manage import make_application


logger = logging.getLogger('onion')


__commands__ = {}


def get_commands(global_options):
    global __commands__

    def check(c):
        return (inspect.isclass(c) and 
                issubclass(c, Command) and c is not Command and 
                c is not CommandManager)

    def find_mod_commands(mod):
        for name in dir(mod):
            c = getattr(mod, name)
            if check(c):
                register_command(c)

    def collect_commands():
        pass

    collect_commands()

    return __commands__

def register_command(klass):
    global __commands__
    __commands__[klass.name] = klass



def handle_default_options(options):
    if options.pythonpath and not options.pythonpath in sys.path:
        sys.path.insert(0, options.pythonpath)

class NewOptionParser(OptionParser):

    def _process_args(self, largs, rargs, values):
        while rargs:
            arg = rargs[0]
            longarg = False
            try:
                if arg[0:2] == "--" and len(arg) > 2:
                    # process a single long option (possibly with value(s))
                    # the superclass code pops the arg off rargs
                    longarg = True
                    self._process_long_opt(rargs, values)
                elif arg[:1] == "-" and len(arg) > 1:
                    # process a cluster of short options (possibly with
                    # value(s) for the last one only)
                    # the superclass code pops the arg off rargs
                    self._process_short_opts(rargs, values)
                else:
                    # it's either a non-default option or an arg
                    # either way, add it to the args list so we can keep
                    # dealing with options
                    del rargs[0]
                    raise Exception
            except:
                if longarg:
                    if '=' in arg:
                        del rargs[0]
                largs.append(arg)


class NewFormatter(IndentedHelpFormatter):
    def format_heading(self, heading):
        return "%*s%s:\n" %(self.current_indent, "", 'Global Options')


class CommandError(Exception): pass


class CommandMetaClass(type):

    def __init__(cls, name, bases, dct):
        option_list = list(dct.get('option_list', []))
        for c in bases:
            if hasattr(c, 'option_list') and isinstance(c.option_list, list):
                option_list.extend(c.option_list)
        cls.option_list = option_list

        if cls.register:
            register_command(cls)


class Command(object):
    __metaclass__ = CommandMetaClass

    option_list = ()
    help = ''
    args = ''
    check_apps_dirs = True
    has_options = False
    check_apps = False
    register = False

    def create_parser(self, prog_name, sub_command):
        return OptionParser(prog=prog_name,
                        usage=self.usage(sub_command),
                        version=self.get_version(),
                        add_help_option=False,
                        option_list=self.option_list)

    def get_version(self):
        return "Onion version is %s" %onion.version


    def usage(self, sub_command):
        if self.has_options:
            usage = '%%prog %s [options] %s' %(sub_command, self.args)
        else:
            usage = '%%prog %s %s' %(sub_command, self.args)

        if self.help:
            return '%s\n\n%s' %(usage, self.help)
        else:
            return usage

    def print_help(self, prog_name, sub_command):
        parser = self.create_parser(prog_name, sub_command)
        parser.print_help()

    def run_from_argv(self, prog, sub_command, global_options, argv):
        self.prog_name = prog
        parser = self.create_parser(prog, sub_command)
        options, args = parser.parse_args(argv)
        self.execute(args, options, global_options)

    def execute(self, args, options, global_options):
        try:
            self.handle(options, global_options, *args)
        except CommandError as e:
            logger.exception(e)
            sys.exit(1)

    def handle(self, options, global_options, *args):
        raise NotImplemented()


class CommandManager(Command):
    usage_info = '%prog [global_options] [sub_command [options] [args]]'

    def __init__(self, argv=None, commands=None, prog_name=None, global_options=None):
        self.argv = argv
        self.prog_name = prog_name or os.path.basename(self.argv[0])
        self.commands = commands
        self.global_options = global_options

    def get_commands(self, global_options):
        if callable(self.commands):
            commands = self.commands(global_options)
        else:
            commands = self.commands
        return commands


    def fetch_command(self, global_options, sub_command):
        commands = self.get_commands(global_options)
        try:
            klass = commands[sub_command]
        except KeyError:
            sys.stderr.write("Unknown command: %r\nType '%s help' for usage.\n" %(sub_command, self.prog_name))
            sys.exit(1)
        return klass

    def print_help_info(self, global_options):
        usage = ['', "Type '%s help <sub_command>' for help on a specific sub_command." %self.prog_name, '']
        usage.append('Available subcommands:')
        commands = self.get_commands(global_options).keys()
        commands.sort()

        for cmd in commands:
            usage.append('    %s' %cmd)
        return '\n'.join(usage)

    def execute(self, callback=None):
        parser = NewOptionParser(prog=self.prog_name,
                    usage=self.usage_info,
                    formatter = NewFormatter(),
                    add_help_option=False,
                    option_list=self.option_list)

        if not self.global_options:
            global_options, args = parser.parse_args(self.argv)
            global_options.apps_path = os.path.normpath(
                        os.path.join(global_options.project, 'apps'))
            handle_default_options(global_options)
            args = args[1:]
        else:
            global_options = self.global_options
            args = self.argv

        if callback is not None:
            callback(global_options)

        def print_help(global_options):
            parser.print_help()
            sys.stderr.write(self.print_help_info(global_options) + '\n')
            sys.exit(0)

        if len(args) == 0:
            if global_options.version:
                print self.get_version()
                sys.exit(0)
            else:
                print_help(global_options)

        try:
            sub_command = args[0]
        except IndexError:
            sub_command = 'help'

        command = None
        if sub_command == 'help':
            if len(args) > 1:
                command = self.fetch_command(global_options, args[1])
                if issubclass(command, CommandManager):
                    cmd = command(['help'], None, 
                                    '%s %s' %(self.prog_name, args[1]), global_options=global_options)
                    cmd.execute()
                else:
                    command().print_help(self.prog_name, args[1])
                sys.exit(0)
            else:
                print_help(global_options)
        
        if global_options.help:
            print_help(global_options)
        else:
            command = self.fetch_command(global_options, sub_command)
            if issubclass(command, CommandManager):
                cmd = command(['help'], None, 
                                '%s %s' %(self.prog_name, sub_command), global_options=global_options)
                cmd.execute()
            else:
                cmd = command()
                cmd.run_from_argv(self.prog_name, sub_command, global_options, args[1:])


class ApplicationCommandManager(CommandManager):
    option_list = (
        make_option('--help', action='store_true', dest='help',
            help='Show this help message and exit.'),
        make_option('-v', '--verbose', action='store_true',
            help='Output the result in verbose mode.'),
        make_option('-s', '--settings', dest='settings', default='settings.yaml',
            help='Settings file name, Default is "settings.yaml"'),
        make_option('--project', default='.', dest='project',
            help='Your project directory, default is current directory.'),
        make_option('--pythonpath', default='',
            help='A directory to add to the Python path, e.g. "/home/myproject". '),
        make_option('--version', action='store_true', dest='version',
            help="Show program's version number and exit."),
    )

    help = ''
    args = ''


def execute_command_line(argv=None, prog_name=None, callback=None):
    m = ApplicationCommandManager(argv, get_commands, prog_name)
    m.execute(callback)
