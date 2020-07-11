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
        nps.NPSAppManaged.__init__(self)

    def onStart(self):
        self.addForm("select_project", MenuForm, name="Home Sweet Home")
        self.addForm("start_project", StartProj, name="Start project")

# https://npyscreen.readthedocs.io/form-objects.html
class MenuForm(nps.Form):
    def __init__(self, *args, **kwargs):
        self.ml_values = ["A", "B", "C"]
        self.curr_project = None

        nps.Form.__init__(self, *args, **kwargs)

    def create(self):
        self.project_choose = self.add(ProjectSelector, name="selection_project", values=self.ml_values, height=(len(self.ml_values)+1))
        self.text = self.add(nps.Textfield, value="")
        self.projectinfo = self.add(ProjectInfo, name="project_information")

class ProjectInfo(nps.FixedText):
    def create(self):
        self.value = "Not implemented yet"

    def get_info(self, project):
        self.value = "Project: " + project + " -> Not implemented yet"
        self.value += "\n" + self.parent.parentApp.test_var
        self.display()

class ProjectSelector(nps.MultiLineAction):
    def actionHighlighted(self, act_on_this, key_press):
        self.parent.parentApp.project_selected = act_on_this
        self.parent.parentApp.switchForm("start_project")

    def when_cursor_moved(self, *args, **kwargs):
        self.parent.projectinfo.get_info(self.values[self.cursor_line])

class StartProj(nps.ActionForm):
    def create(self):
        self.text = self.add(nps.FixedText, value="tutu", invert_highlight_color=True)
        self.text.set_editable(False)

    def while_editing(self, widg):
        self.text.value="The selected project is: " + str(self.parentApp.project_selected)
 
    def on_ok(self):
        sel = self.parentApp.project_selected
        self.parentApp.switchForm(None)

    def on_cancel(self):
        self.parentApp.switchForm(None)
