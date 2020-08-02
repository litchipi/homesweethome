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
        path_prompt = FilepathForm(prompt, info, os.path.curdir, isfile, choose_existing, True)
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
        self.prompt = self.add(nps.PasswordEntry)

    def get_result(self):
        return self.prompt.value

class FSDescriptor(nps.MultiLineAction):
    def __init__(self, *args, **kwargs):
        nps.MultiLine.__init__(self, *args, **kwargs)

        self.select_this_dir_msg = "<Select his dir>"
        self.create_new_dir_msg = "<New dir here>"
        self.create_new_file_msg = "<New file here>"

        self.allow_file_replace = kwargs["allow_replace"]
        self.seek_exist = kwargs["exist"]
        self.seek_dir = not kwargs["isfile"]
        
        self.result = None

        self.change_tree(os.path.abspath(kwargs["startdir"]))
        self.act_values()

    def get_entry_info(self, entry):
        fname = os.path.join(self.fs_dir_curr, entry)
        dex = os.path.isdir(fname); fex = os.path.isfile(fname)
        if dex and fex:
            dex = ("/" in entry)
            fex = (not dex)
        return fname, dex, fex

    def actionHighlighted(self, el, key):
        fname, dex, fex = self.get_entry_info(el)

        if (not self.seek_exist):
            if self.seek_dir and (el == self.create_new_dir_msg):
                pass                                # Create new dir
            elif not self.seek_dir:
                    if (el == self.create_new_file_msg):
                        pass                        # Create new file
                    elif fex and self.allow_file_replace:
                        pass                        # Ask replace file
        else:
            if not self.seek_dir and fex:
                pass                                # Select this file

        if dex:
            self.change_tree(fname)
            self.act_values()


    def change_tree(self, d):
        self.raw_values = self.fs_list(d)
        self.values = list(self.raw_values)
        self.fs_dir_curr = d
        self.parent.prompt.value = d + "/"
        self.totinp = ""

    def fs_list(self, d):
        ldir = list()
        for root, dirs, files in os.walk(d):
            for d in dirs:
                ldir.append(d+"/")
            if not self.seek_dir:
                for f in files:
                    ldir.append(f)
            break
        return ldir

    def new_inp(self, inp):
        self.totinp += inp
        self.act_values()

    def deletechar(self):
        self.totinp = str(self.totinp[:-1])
        self.act_values()
    
    def act_values(self):
        self.values = list()
        if self.seek_dir:
            if self.seek_exist:
                self.values.append(self.select_this_dir_msg)
            else:
                self.values.append(self.create_new_dir_msg)
                if self.allow_file_replace:
                    self.values.append(self.select_this_dir_msg)
        else:
            self.values.append(self.create_new_file_msg)
        self.values.append("../")
        self.values +=[el for el in self.raw_values if el.startswith(self.totinp)]
        self.values +=[el for el in self.raw_values if (el not in self.values) and (self.totinp in el)]
        self.display()

class FilepathPrompt(nps.Textfield):
    def __init__(self, *args, startdir="/", **kwargs):
        nps.Textfield.__init__(self, *args, **kwargs)

    def h_delete_left(self, inp):
        super().h_delete_left(inp)
        self.parent.fs_descr.deletechar()

    def h_addch(self, inp):
        super().h_addch(inp)
        #self.parent.fs_descr.set_relyx(1+len(self.value), 1+len(self.value))
        self.parent.fs_descr.new_inp(chr(inp))


class FilepathForm(nps.ActionForm):
    def __init__(self, msg, info, startdir, isfile, exist, allow_replace, *args, **kwargs):
        nps.Form.__init__(self, *args, **kwargs)
        self.text = self.add(nps.FixedText, editable=False)
        self.text.value = msg
        self.text.set_editable(False)
        self.text.display()

        self.prompt = self.add(FilepathPrompt, startdir=startdir)
        self.fs_descr = self.add(FSDescriptor, startdir=startdir, exist=exist, isfile=isfile, allow_replace=allow_replace, scroll_exit=True)

    def update_display(self):
        self.curr_root.display()
        self.prompt.set_relyx(0, len(self.fs_dir_curr))

    def get_result(self):
        return self.prompt.get_result()

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
