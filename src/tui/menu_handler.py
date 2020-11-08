#!/usr/bin/env python3
#-*-encoding:utf-8*-

import os
import curses
import npyscreen as nps

from .wrappers import create_button, get_filepath
from .popups import popup_binary_question

# https://npyscreen.readthedocs.io/application-objects.html
class MenuHandler(nps.NPSAppManaged):
    STARTING_FORM = "select_project"

    def __init__(self, config, project_list):
        self.config = config
        self.project_list = project_list

        self.project_selected = "toto"
        self.projects_configs = dict()
        self.final_project = None
        self.dispatch = None
        nps.NPSAppManaged.__init__(self)

    def onStart(self):
        self.addForm("select_project", ProjectSelectionForm, self.project_list, name="Home Sweet Home", height=(len(self.project_list)+5))
        self.addForm("open_project", StartProj, name="Start project")
        self.addForm("new_project", NewProj, name="New project")

    def set_dispatch_fct(self, fct):
        self.dispatch = fct

    def get_project_configs(self, project_name):
        if project_name not in self.projects_configs.keys():
            self.projects_configs[project_name] = self.dispatch("get_session_config", project_name)
        return self.projects_configs[project_name]

    def get_password(self, prompt="Enter your password:"):
        pwd_prompt = PasswordPrompt(prompt)
        pwd_prompt.edit()
        return pwd_prompt.get_result()

    def get_softwares_configs(self):
        return {"tmux":["base"], "nvim":["base", "C", "Python"]}   #TODO Load from CRT stored configurations

    def create_project(self, config):
        self.dispatch("new", config["name"], project_config=config)
        binquest = BinaryQuestion("Start the new project ?")
        binquest.edit()
        if (binquest.get_result() == "Yes"):
            self.dispatch("start", config["name"])
        else:
            self.switchForm("select_project")

# https://npyscreen.readthedocs.io/form-objects.html
class ProjectSelectionForm(nps.FormBaseNew):
    def __init__(self, projlist, *args, **kwargs):
        self.curr_project = None
        self.project_list = projlist#self.project_list
        self.new_project_string = "New project..."
        self.project_list.append(self.new_project_string)
        nps.Form.__init__(self, *args, **kwargs)

    def create(self):
        maxheight={"selector":10}
        self.project_choose = self.add(ProjectSelector, name="selection_project", values=self.project_list, height=min(maxheight["selector"], len(self.project_list)+1), scroll_exit=True, rely=2)

        self.projectinfo = self.add(ProjectInfo, name="Informations", editable=False, rely=3+self.project_choose.height)

    def pre_edit_loop(self):
        if (len(self.project_list) > 0):
            self.projectinfo.get_info(self.project_list[0])


class ProjectInfo(nps.BoxTitle):
    def get_info(self, project):
        if (project == self.parent.new_project_string):
            self.values = ["Create a new project"]
        else:
            cfgs = self.parent.parentApp.get_project_configs(project)
            maxklen = max([len(k) for k in cfgs.keys()])
            self.values = ["{}: {}".format(k.replace("_", " ").capitalize().ljust(maxklen+1), v) for k, v in cfgs.items()]
        self.display()


class ProjectSelector(nps.MultiLineAction):
    def actionHighlighted(self, act_on_this, key_press):
        if (act_on_this == self.parent.new_project_string):
            self.parent.parentApp.switchForm("new_project")
        else:
            self.parent.parentApp.project_selected = act_on_this
            self.parent.parentApp.switchForm("open_project")

    def when_cursor_moved(self, *args, **kwargs):
        self.parent.projectinfo.get_info(self.values[self.cursor_line])


class ButtonList(nps.MultiLineAction):
    def actionHighlighted(self, act_on_this, key_press):
        self.parent.button_dispatcher(act_on_this.lower())

    def update_buttons(self):
        self.values = list()
        for n in self.parent.buttons_names:
            if not self.parent.update_button_name(n):
                continue
            self.values.append(n.capitalize())
        self.update()

class FormFlags:
    PASSWORD_INPUT=0

class NewProj(nps.FormBaseNew):
    def __init__(self, *args, **kwargs):
        softconf = self.parentApp.get_softwares_configs()
        form_fields = {
                "name":("Name",    "", "What name will appear on the menu", None),
                "descr":("Description", "", "Short text explaining the project", None),
                "priority":("Priority",    0, "The higher, the more on top of the list",None),

                "secured":("Secured", ["Yes", "No"], "Protected by a password (for every data saved)", None),
                "password":("Password", FormFlags.PASSWORD_INPUT, "Password of the project", lambda f: (f["secured"]=="Yes")),

                "backup":("Backup",  ["Enabled", "Disabled"], "Automatic backup", None),
                "logging":("Logging", ["Disabled", "Enabled"], "Log and save the logs of the shell", None),

                "fromgit":("From git",    ["Yes", "No"], "Import the project from a remote git repository ?", None),
                "remote_git_url":("Remote Git URL",  "", "URL of the remote git to clone", lambda f: (f["fromgit"]=="Yes")),
                "create_git_repo":("Create a Git repository", ["Yes", "No"], "Automatically setup a git repository", lambda f: (f["fromgit"]=="No")),
                }

        for soft, configs in softconf.keys():
            form_fields[soft + "_config"] = ("Configuration of " + soft, ["No pre-config"] + configs, "Select the configuration to use for the software " + soft, None)

        self.config_form = ConfigurationTool(form_fields)

        self.buttons_names = ["create", "return"]
        nps.FormBaseNew.__init__(self, *args, **kwargs)
        self.butt_list = self.add(ButtonList)

    def update_button_name(self, name):
        return True

    def button_dispatcher(self, ident):
        if ident == "return":
            self.parentApp.switchForm("select_project")
        elif ident == "create":
            self.parentApp.create_project(self.config_form.config)

class StartProj(nps.FormBaseNew):
    def __init__(self, *args, **kwargs):
        self.buttons_names = ["start", "return", "edit", "backup", "restore", "delete"]
        self.actions_kwargs = {k:dict() for k in self.buttons_names}
        nps.FormBaseNew.__init__(self, *args, **kwargs)
        self.butt_list = self.add(ButtonList)

    def update_button_name(self, name):
        if (n == "restore") and not self.parent.parentApp.dispatch("check_backup_exist", self.parent.parentApp.project_selected):
            return False
        return True

    def pre_edit_loop(self):
        self.butt_list.update_buttons()

    def button_dispatcher(self, ident):
        if ident == "return":
            self.parentApp.switchForm("select_project")
        else:
            self.prepare_kwargs(ident, self.parentApp.project_selected)
            self.parentApp.dispatch(ident, self.parentApp.project_selected, **self.actions_kwargs[ident])
            self.butt_list.update_buttons()

    def prepare_kwargs(self, ident, project):
        if ident in ["backup", "restore"]:
            self.actions_kwargs[ident]["pwd"] = str(self.parentApp.get_password())
        if ident == "backup":
            self.actions_kwargs[ident]["project_path"] = os.path.abspath(self.parentApp.projects_configs[project]["project_path"])
        if ident == "restore":
            self.actions_kwargs[ident]["restore_path"] = get_filepath("Place to restore project",
                    info="Will create a new directory inside the one selected", isfile=False, choose_existing=False)

class BinaryQuestion(nps.Form):
    def __init__(self, msg, *args, options=["Yes", "No"], **kwargs):
        nps.Form.__init__(self, *args, **kwargs)
        self.buttons_names = options
        self.text = self.add(nps.FixedText, editable=False)
        self.text.value = msg
        self.text.set_editable(False)
        self.text.display()
        self.add(ButtonList)
        self.result = None

    def get_result(self):
        return self.result

    def update_button_name(self, name):
        return True

    def button_dispatcher(self, name):
        self.result = name

class PasswordPrompt(nps.Form):
    def __init__(self, msg, *args, **kwargs):
        nps.Form.__init__(self, *args, **kwargs)
        self.text = self.add(nps.FixedText, editable=False)
        self.text.value = msg
        self.text.set_editable(False)
        self.text.display()
        self.prompt = self.add(nps.PasswordEntry)

    def get_result(self):
        return self.prompt.value


class NotImplementedForm(nps.ActionForm):
    def create(self):
        self.text = self.add(nps.FixedText, value="Not implemented yet", editable=False)
        self.text.set_editable(False)

    def on_ok(self):
        self.parentApp.switchForm("select_project")

    def on_cancel(self):
        self.on_ok()
