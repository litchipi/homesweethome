#!/usr/bin/env python3
#-*-encoding:utf-8*-

import os
import json

from menu_handler import MenuHandler

from cantreadth1s import CantReadThis

class GUICore(MenuHandler):
    default_config = {
            "crt_seclevel":10,
            "backup_dir":"./backup/",
            "sessions_dir":"./sessions/"
            }

    def __init__(self, config):
        self.config = dict.copy(self.default_config)
        self.config.update(config)
        self.setup_filesystem()
        projlist = list()
        for _, _, f in os.walk(self.config["sessions_dir"]):
            projlist += f
        MenuHandler.__init__(self, self.config, projlist)

        self.crt = CantReadThis(sec_level=self.config["crt_seclevel"])

    def setup_filesystem(self):
        for d in ["sessions_dir", "backup_dir"]:
            self.config[d] = os.path.abspath(self.config[d])
            if not os.path.isdir(self.config[d]):
                os.mkdir(self.config[d])

    def run(self):
        self.set_dispatch_fct(self.dispatch_menu_actions)
        super().run()
        print(self.final_project)

    def dispatch_menu_actions(self, action, project_name, **kwargs):
        if action == "start":
            self.switchForm(None)
            self.final_project = (self.project_selected, self.projects_configs[self.project_selected])

        elif action == "backup":
            orig_dir = os.path.abspath(os.path.curdir)
            os.chdir(kwargs["project_path"] + "/..")
            self.crt.setup_preset_pwd(kwargs["pwd"])
            self.crt.handle_directory(kwargs["project_path"], out=os.path.join(os.path.join(self.config["backup_dir"], "renew_test"), project_name) + ".hshbck")
            self.popup_message("Project backed up successfully")
            os.chdir(orig_dir)

        elif action == "restore":
            self.crt.setup_preset_pwd(kwargs["pwd"])
            curd = os.path.abspath(os.curdir)
            os.chdir(kwargs["restore_path"])
            self.crt.handle_file(os.path.join(self.config["backup_dir"], project_name))
            os.chdir(curd)
            self.popup_message("Project restored successfully")

        elif action == "get_session_config":
            cfg_fname = None
            for path, dirs, files in os.walk(self.config["sessions_dir"]):
                if project_name in files:
                    cfg_fname = os.path.abspath(os.path.join(path, project_name))
                break
            with open(cfg_fname, "r") as f:
                cfg = json.load(f)
            return cfg


def launch_hsh_gui(args):
    core = GUICore(args.__dict__)
    core.run()



# GET SAVED SNAPSHOTS
# for _,_,f in os.walk(tmuxp.cli.get_config_dir() + "/"):
#     print(f)

# Freeze a session as json to a specific file
#s = libtmux.Server(socket_name="homesweethome_socket")
#d = tmuxp.workspacebuilder.freeze(s.list_sessions()[0])
#with open("homesweethome_session", "w") as f:
#   json.dump(d, f)
