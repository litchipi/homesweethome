#!/usr/bin/env python3
#-*-encoding:utf-8*-

import os
import time
import json

from tui.menu_handler import MenuHandler
from tui.popups import popup_information, popup_error

from cantreadth1s import CantReadThis

class GUICore(MenuHandler):
    default_config = {
            "crt_seclevel":10,
            "backup_dir":"./backup/renew_test/",
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
        self.sessions_data = dict()
        self.load_sessions()
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

    def save_session_data(self, project, key, val):
        self.sessions_data[project][key] = val
        with open(os.path.join(self.config["sessions_dir"], project), "w") as jsf:
            json.dump(self.sessions_data[project], jsf)

    def load_sessions(self):
        for f in os.scandir(self.config["sessions_dir"]):
            with open(f.path, "r") as jsf:
                self.sessions_data[f.name] = json.load(jsf)

    def dispatch_menu_actions(self, action, project_name, **kwargs):
        if action == "start":
            self.save_session_data(project_name, "last_used", time.asctime())
            self.switchForm(None)
            self.final_project = (self.project_selected, self.projects_configs[self.project_selected])

        elif action == "backup":
            orig_dir = os.path.abspath(os.path.curdir)
            os.chdir(kwargs["project_path"] + "/..")
            self.crt.setup_preset_pwd(kwargs["pwd"])
            ret = self.crt.handle_directory(kwargs["project_path"], out=os.path.join(self.config["backup_dir"], project_name) + ".hshbck")
            os.chdir(orig_dir)
            if not ret[0]:
                popup_error("Cannot backup project", add_info=ret[1])
            else:
                popup_information("Project backed up successfully", wide=False)
                self.save_session_data(project_name, "last_backup", time.asctime())


        elif action == "restore":
            self.crt.setup_preset_pwd(kwargs["pwd"])
            curd = os.path.abspath(os.curdir)
            os.chdir(kwargs["restore_path"])
            ret = self.crt.handle_file(os.path.join(self.config["backup_dir"], project_name) + ".hshbck.cant_read_this")
            os.chdir(curd)
            if not ret[0]:
                popup_error("Cannot restore backup", add_info=ret[1])
                breakpoint()
            else:
                popup_information("Project restored successfully", wide=False)
                self.save_session_data(project_name, "last_restore", time.asctime())

        elif action == "get_session_config":
            if project_name in self.sessions_data.keys():
                return self.sessions_data[project_name]
            else:
                return None

        elif action == "check_backup_exist":
            return any([project_name in f.name for f in os.scandir(self.config["backup_dir"])])


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
