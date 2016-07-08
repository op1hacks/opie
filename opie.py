#!/usr/bin/env python3

import click
import os

plugin_folder = os.path.join(os.path.dirname(__file__), 'commands')

class OpieCLI(click.MultiCommand):
    def __init__(self, **attrs):
        click.MultiCommand.__init__(self, invoke_without_command=True, no_args_is_help=False, chain=False, **attrs)

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(plugin_folder):
            if filename.endswith('.py'):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        ns = {}
        fn = os.path.join(plugin_folder, name + '.py')
        with open(fn) as f:
            code = compile(f.read(), fn, 'exec')
            eval(code, ns, ns)
        return ns['cli']

cli = OpieCLI()

if __name__ == '__main__':
    cli()

