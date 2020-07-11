#!/usr/bin/env python3
#-*-encoding:utf-8*-

import npyscreen as nps

# https://npyscreen.readthedocs.io/application-objects.html
class MenuHandler(nps.NPSAppManaged):
    STARTING_FORM = "select_project"

    def __init__(self, config):
        self.config = config

        self.project_selected = "toto"
        nps.NPSAppManaged.__init__(self)

    def onStart(self):
        self.addForm("select_project", MenuForm, name="Home Sweet Home")
        self.addForm("start_project", StartProj, name="Start project")

# https://npyscreen.readthedocs.io/form-objects.html
class MenuForm(nps.Form):
    OK_BUTTON_TEXT='Launch'
    CANCEL_BUTTON_TEXT='Exit'

    def __init__(self, *args, **kwargs):
        self.ml_values = ["A", "B", "C"]
        self.curr_project = None

        nps.Form.__init__(self, *args, **kwargs)

    def create(self):
        self.project_choose = self.add(ProjectSelector, name="multiline_test", values=self.ml_values)

class ProjectSelector(nps.MultiLineAction):
    def actionHighlighted(self, act_on_this, key_press):
        self.parent.parentApp.project_selected = act_on_this
        self.parent.parentApp.switchForm("start_project")

class StartProj(nps.ActionForm):
    def create(self):
        self.text = self.add(nps.Textfield, value="tutu")
        self.text.set_editable(False)

    def while_editing(self, widg):
        self.text.value=self.parentApp.project_selected

    def on_ok(self):
        sel = self.parentApp.project_selected
        self.parentApp.switchForm(None)
        print("\nSelected: " + sel)

    def on_cancel(self):
        self.parentApp.switchForm(None)
