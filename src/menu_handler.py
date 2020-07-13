#!/usr/bin/env python3
#-*-encoding:utf-8*-

import os
import curses
import npyscreen as nps

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
        self.addForm("new_project", NotImplementedForm, name="New project")

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

    def get_filepath(self, prompt, info="", isfile=True, choose_existing=True):
        path_prompt = FilepathPrompt(prompt, info, isfile, choose_existing)
        path_prompt.edit()
        return path_prompt.get_result()

    def popup_message(self, msg):
        popup = PopupForm(msg)
        popup.edit()

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












class StartProj(nps.FormBaseNew):
    def __init__(self, *args, **kwargs):
        self.buttons_names = ["start", "return", "edit", "backup", "restore", "delete"]
        self.actions_kwargs = {k:dict() for k in self.buttons_names}
        nps.FormBaseNew.__init__(self, *args, **kwargs)


    def create(self):
        for n in self.buttons_names:
            self.butt = self.add(create_button(self.button_dispatcher, n), name=n.capitalize())

    def button_dispatcher(self, ident):
        if ident == "return":
            self.parentApp.switchForm("select_project")
        else:
            self.prepare_kwargs(ident, self.parentApp.project_selected)
            self.parentApp.dispatch(ident, self.parentApp.project_selected, **self.actions_kwargs[ident])

    def prepare_kwargs(self, ident, project):
        if ident in ["backup", "restore"]:
            self.actions_kwargs[ident]["pwd"] = str(self.parentApp.get_password())
        if ident == "backup":
            self.actions_kwargs[ident]["project_path"] = os.path.abspath(self.parentApp.projects_configs[project]["project_path"])
        if ident == "restore":
            dirpath = self.parentApp.get_filepath("Place to restore project", info="Will create a new directory inside the one selected", isfile=False, choose_existing=False)
            self.actions_kwargs[ident]["restore_path"] = dirpath

def create_button(callback, ident):
    class CustomButton(nps.ButtonPress):
        CUST_BUTTON_ID = ident
        CUST_CUTTON_CALLBACK = callback
        def whenPressed(self):
            self.CUST_CUTTON_CALLBACK(self.CUST_BUTTON_ID)
    return CustomButton




class PasswordPrompt(nps.Form):
    def __init__(self, msg, *args, **kwargs):
        nps.Form.__init__(self, *args, **kwargs)
        self.text = self.add(nps.FixedText, editable=False)
        self.text.value = msg
        self.text.set_editable(False)
        self.text.display()

    def get_result(self):
        return "password test"

class FilepathPrompt(nps.ActionForm):
    def __init__(self, msg, info, isfile, exist, *args, **kwargs):
        nps.Form.__init__(self, *args, **kwargs)
        self.text = self.add(nps.FixedText, editable=False)
        self.text.value = msg
        self.text.set_editable(False)
        self.text.display()

    def get_result(self):
        return "/home/eve/Documents/homesweethome/dirtest/"

class PopupForm(nps.Popup):
    def __init__(self, msg, *args, **kwargs):
        nps.Popup.__init__(self, *args, **kwargs)
        self.text = self.add(nps.FixedText, editable=False)
        self.text.value = msg
        self.text.set_editable(False)
        self.text.display()

class NotImplementedForm(nps.ActionForm):
    def create(self):
        self.text = self.add(nps.FixedText, value="Not implemented yet", editable=False)
        self.text.set_editable(False)

    def on_ok(self):
        self.parentApp.switchForm("select_project")

    def on_cancel(self):
        self.on_ok()
