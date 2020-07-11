#!/usr/bin/env python3
#-*-encoding:utf-8*-

import npyscreen as nps

# https://npyscreen.readthedocs.io/application-objects.html
class MenuHandler(nps.NPSAppManaged):
    STARTING_FORM = "select_project"

    def __init__(self, config):
        self.config = config
        self.test_var = "test var"

        self.project_selected = "toto"
        self.projects_configs = dict()
        self.final_project = None
        nps.NPSAppManaged.__init__(self)

    def onStart(self):
        self.addForm("select_project", MenuForm, name="Home Sweet Home")
        self.addForm("start_project", StartProj, name="Start project", title="test title")

    def start_project(self):
        self.switchForm(None)
        self.final_project = (self.project_selected, self.projects_configs[self.project_selected])

    def get_project_configs(self, project_name):
        # TODO      Grab configuration from stored file of the project tmuxp freeze
        cfgs = {"test":"a", "test2":5, "test3":["abcdef", "akzel", "paopzeraz"]}
        if project_name not in self.projects_configs.keys():
            self.projects_configs[project_name] = cfgs
        return cfgs

# https://npyscreen.readthedocs.io/form-objects.html
class MenuForm(nps.FormBaseNew):
    def __init__(self, *args, **kwargs):
        self.ml_values = ["A", "B", "C"]
        self.curr_project = None

        nps.Form.__init__(self, *args, **kwargs)

    def create(self):
        self.project_choose = self.add(ProjectSelector, name="selection_project", values=self.ml_values, height=(len(self.ml_values)+1))
        self.text = self.add(nps.Textfield, value="")
        self.projectinfo = self.add(ProjectInfo, name="project_information")
        self.projectinfo.get_info(self.ml_values[0])

class ProjectInfo(nps.FixedText):
    def create(self):
        self.value = "Not implemented yet"

    def get_info(self, project):
        cfgs = self.parent.parentApp.get_project_configs(project)
        self.value = "Project: " + project
        self.value += "\n" + ", ".join(cfgs.keys())
        self.display()

class ProjectSelector(nps.MultiLineAction):
    def actionHighlighted(self, act_on_this, key_press):
        self.parent.parentApp.project_selected = act_on_this
        self.parent.parentApp.switchForm("start_project")

    def when_cursor_moved(self, *args, **kwargs):
        self.parent.projectinfo.get_info(self.values[self.cursor_line])

class StartProj(nps.FormBaseNew):
    def create(self):
        self.start_butt = self.add(create_button(self.button_dispatcher, "start"), name="Launch Project")
        self.start_butt = self.add(create_button(self.button_dispatcher, "abort"), name="Exit")
        self.text = self.add(nps.FixedText, value=self.get_text(), editable=False)
        self.text.set_editable(False)

    def button_dispatcher(self, ident):
        if ident == "start":
            self.parentApp.start_project()
        elif ident == "abort":
            self.parentApp.switchForm(None)

    def get_text(self):
        return "The selected project is: " + str(self.parentApp.project_selected)

    def while_editing(self, widg):
        self.text.value = self.get_text()
        self.text.display()

def create_button(callback, ident):
    class CustomButton(nps.ButtonPress):
        CUST_BUTTON_ID = ident
        CUST_CUTTON_CALLBACK = callback
        def whenPressed(self):
            self.CUST_CUTTON_CALLBACK(self.CUST_BUTTON_ID)
    return CustomButton
