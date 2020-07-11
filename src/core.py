#!/usr/bin/env python3
#-*-encoding:utf-8*-

import os

from menu_handler import MenuHandler

from cantreadth1s import CantReadThis

class Core(MenuHandler):
    default_config = {}

    def __init__(self, config):
        self.config = dict.copy(self.default_config)
        self.config.update(config)
        MenuHandler.__init__(self, self.config)

        self.crt = CantReadThis(sec_level=self.toolcfg["crt_seclevel"])

    def run(self):
        super().run()
        print(self.final_project)

    def dispatch_menu_actions(self, action, *args, **kwargs):
        if action == "backup":
            project_path, pwd, project_name = args
            self.crt.setup_preset_pwd(pwd)
            self.crt.handle_directory(project_path, out=os.path.join(self.toolcfg["backup_directory"], project_name))

        elif action == "restore":
            project_name, pwd, restore_path = args
            self.crt.setup_preset_pwd(pwd)
            curd = os.path.abspath(os.curdir)
            os.chdir(restore_path)
            self.crt.handle_file(os.path.join(self.toolcfg["backup_directory"], project_name))
            os.chdir(curd)

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
