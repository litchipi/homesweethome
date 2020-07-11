#!/usr/bin/env python3
#-*-encoding:utf-8*-

from menu_handler import MenuHandler

class Core:
    default_config = {}

    def __init__(self, config):
        self.config = dict.copy(self.default_config)
        self.config.update(config)

        self.menu = MenuHandler(self.config)

    def run(self):
        self.menu.run()

def launch_hsh(args):
    core = Core(args.__dict__)
    core.run()
