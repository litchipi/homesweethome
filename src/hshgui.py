#!/usr/bin/env python3
#-*-encoding:utf-8*-

import os
import time
import json

from tui.menu_handler import MenuHandler
from tui.popups import popup_information, popup_error

from cantreadth1s import CantReadThis

class Core:
    default_config = {
            "crt_seclevel":1,
            "data_dir":"~/.local/share/homesweethome/"
            }

    default_config["archive"] = os.path.join(default_config["data_dir"], "archive.crt")
    default_config["database"] = os.path.join(default_config["data_dir"], "database")
    default_config["hsh_tools"] = os.path.join(default_config["data_dir"], "tools")

    def __init__(self, config):
        self.config = dict.copy(self.default_config)
        self.config.update(config)

        if os.path.isfile(self.config["archive"]):
            with open(self.config["archive"], "r") as jdata:
                self.archive = json.loads(jdata)
        else:
            self.setup_new_archive()
        self.menuhandler = MenuHandler(self.config, projlist)

    def get_system_name(self):
        return os.uname().nodename

    def setup_new_archive(self):
        metadata = {
                "systems":{self.get_system_name():self.config["database"]},
                "seeds":{
                    #"project_name":<crt_password_seed>
                    }
                "crt_config":{
                    # General configuration for CRT
                    }
                }

        projects = {
                #"project_name":{
                #   ####### CRT #######     -> Not secured -> password = project name
                #   "tmux_env":"tmuxp_env_data",                       #hsh save
                #   "tools_config":{"tmux":"basic", "nvim":"python"},  #hsh change config <tool> <config name>
                #   "custom_aliases":{"ll":"ls -lah"},                 #hsh set alias <alias> <command>
                #   "configuration":{
                #       "general":{
                #           "auto_backup":True,                 # Project config
                #           "bck_purge_after": nb_saves         # Project config
                #           "auto_log":True,                    # Project config
                #           "auto_log_systems":None             # Project config        None -> All systems     list -> list of systems
                #           "log_purge_after":time_in_secs      # Project config
                #           },
                #       "sparta":{
                #           "auto_log":False        # Project config
                #           }
                #       }
                #   "remote_git":{
                #       "url":"https://github.com/litchipi/homesweethome",      # Project config     or   hsh set remote_git url <url>
                #       "ssh_key":<ssh key>                                     # hsh set remote_git ssh    ->  Secure prompt for ssh key
                #   }
                #   "notes":{
                #       <ident>:<note>              #hsh note <ident> <data>
                #   }
                #   "todo":{
                #       <ident>:<priority>          #hsh todo add <ident> <priority=0>
                #                                   #hsh todo done <ident>
                #                                   #hsh todo list
                #       }
                #   }
                }

        tools = {
                "tmux":{    #hsh add tool <name>    -> Prompt for configuration (custom config + command)
                    "custom_config_param":"-f",
                    "command":"tmux",
                    "saved_configurations":{
                        #"basic":configuration_file_dump                                                        #hsh set config <tool> <config name> <path to config>
                        },
                    "installation_script":None      #If user save installation script, store it here            #hsh set install <tool> <path to script>
                }
        
        backups = {
            #"project_name":{
            #   "autobck":{
            #       ####### Compressed #######
            #       <time_in_secs_0>:{
            #           "0001-azelkfjazle.patch":<patch_data>,
            #           "0002-laezkjfleak.patch":<patch_data>
            #           },
            #       ####### Compressed #######
            #       <time_in_secs_1>:...
            #       }
            #   "manual":{
            #       <ident>:<crt backup of the project>
            #       }
            }

        logs = {
            #"project_name":{                       # Project config
            #   ####### CRT #######
            #   "manual":{                          # hsh log <entry> <data>
            #       <entry>:(<timestamp>,<data>)
            #   }
            #   <time_in_secs_0>:{
            #       ####### Compressed #######
            #       "windows0_pane0":<logs>,
            #       ####### Compressed #######
            #       "windows1_pane0":<logs>,
            #       ####### Compressed #######
            #       "windows1_pane1":<logs>
            #       }
            #   <time_in_secs_1>:{
            #       ####### Compressed #######
            #       "windows0_pane0":<logs>,
            #       ####### Compressed #######
            #       "windows1_pane0":<logs>,
            #       ####### Compressed #######
            #       "windows1_pane1":<logs>
            #       }
            #   }
            }
        self.archive = {"metadata":metadata, "projects":projects, "tools":tools, "backups":backups, "logs":logs}

    def run(self):
        self.menuhandler.run()
        print(self.final_project)

class GUICore(MenuHandler):
    def run(self):
        self.set_dispatch_fct(self.dispatch_menu_actions)
        super().run()

    def dispatch_menu_actions(self, action, project_name, **kwargs):
        if action == "start":
            self.save_session_data(project_name, "last_used", time.asctime())
            self.switchForm(None)
            self.final_project = (self.project_selected, self.projects_configs[self.project_selected])

        elif action == "new":
            pass

        elif action == "backup":
            pass

        elif action == "restore":
            pass

        elif action == "get_session_config":
            return {}

        elif action == "check_backup_exist":
            return True

def launch_hsh_gui(args):
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
