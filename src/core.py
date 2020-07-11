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



# GET SAVED SNAPSHOTS
# for _,_,f in os.walk(tmuxp.cli.get_config_dir() + "/"):
#     print(f)

# Freeze a session as json to a specific file
#s = libtmux.Server(socket_name="homesweethome_socket")
#d = tmuxp.workspacebuilder.freeze(s.list_sessions()[0])
#with open("homesweethome_session", "w") as f:
#   json.dump(d, f)
