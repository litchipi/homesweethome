#!/usr/bin/env python3
#-*-encoding:utf-8*-

import os
import npyscreen as nps
from .popups import popup_text_input

class FSDescriptor(nps.MultiLineAction):
    def __init__(self, *args, **kwargs):
        nps.MultiLine.__init__(self, *args, **kwargs)

        self.allow_file_replace = kwargs["allow_replace"]
        self.seek_exist = kwargs["exist"]
        self.seek_dir = not kwargs["isfile"]
        
        self.reset_but()
        self.result = None

        self.change_tree(os.path.abspath(kwargs["startdir"]))
        self.act_values()

    def reset_but(self):
        self.select_this_dir_but = False# = "<Select his dir>"
        self.create_new_dir_but = False#msg = "<New dir here>"
        self.create_new_dir_from_inp_but = False#msg = "<Create this dir>"
        self.create_new_file_but = False#msg = "<New file here>"
        self.create_new_file_from_inp_but = False#msg = "<Create this file>"

    def get_entry_info(self, entry):
        fname = os.path.abspath(os.path.join(self.fs_dir_curr, entry)) + "/"
        dex = os.path.isdir(fname); fex = os.path.isfile(fname)
        if dex and fex:
            dex = ("/" in entry)
            fex = (not dex)
        return fname, dex, fex

    def actionHighlighted(self, el, key):
        fname, dex, fex = self.get_entry_info(el.lstrip())

        if (not self.seek_dir) and fex:
            if (not self.seek_exist):
                pass        # Select this file
            elif self.allow_file_replace:
                pass        # Ask replace file

        if dex:
            self.enter_folder(fname)

    def enter_folder(self, fname):
        self.change_tree(fname)
        self.act_values()
        self.parent.prompt.update_value(fname)

    def exit_folder(self):
        parent, inp = os.path.split(self.fs_dir_curr[:-1])
        self.enter_folder(parent + "/")
        self.parent.prompt.update_value(os.path.join(parent, inp))
        self.totinp = inp

    def change_tree(self, d):
        self.raw_values = self.fs_list(d)
        self.raw_values = ["../"] + self.raw_values
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
        if inp == "/":
            self.enter_folder(os.path.join(self.fs_dir_curr, self.totinp) + "/")
            self.totinp = ""
        else:
            self.totinp += inp
        self.act_values()

    def deletechar(self):
        if self.totinp == "":
            self.exit_folder()
        else:
            self.totinp = str(self.totinp[:-1])
        self.act_values()

    def act_values(self):
        self.values = list()
        prefix = lambda n: " "*(len(self.totinp) + len(self.fs_dir_curr)-2) + ("+"*("/" in n) + "|"*("/" not in n)) + " "

        self.reset_but()
        if self.seek_dir:
            if self.seek_exist and (self.totinp == ""):
                self.values.append(self.select_this_dir_msg)
            else:
                if (self.totinp == ""):
                    self.create_new_dir_but = True
                elif not os.path.isdir(os.path.join(self.fs_dir_curr, self.totinp)):
                    self.create_new_dir_from_inp_but = True
                if self.allow_file_replace and (self.totinp == ""):
                    self.select_this_dir_but = True
        else:
            if (self.totinp == ""):
                self.create_new_file_but = True
            else:
                if not os.path.isdir(os.path.join(self.fs_dir_curr, self.totinp)):
                    self.create_new_dir_from_inp_but = True
                if not os.path.isfile(os.path.join(self.fs_dir_curr, self.totinp)):
                    self.create_new_file_from_inp_but = True

        self.parent.but_grid.update_buttons([
            self.select_this_dir_but,
            self.create_new_dir_but,
            self.create_new_dir_from_inp_but,
            self.create_new_file_but,
            self.create_new_file_from_inp_but])

        self.choices = [el for el in self.raw_values if el.startswith(self.totinp)]
        self.choices +=[el for el in self.raw_values if (el not in self.choices) and (self.totinp in el)]

        self.values += list(self.choices)
        self.values = [prefix(el) + el for el in self.values]
        self.display()

    def autocomplete(self):
        if len(self.choices) == 1 and (self.choices[0] != "../"):
            self.actionHighlighted(self.choices[0], 10)
        return os.path.join(self.fs_dir_curr, self.totinp)

    def create_new_dir(self):
        name = popup_text_input("Enter the name of the directory: ")
        if name is not None:
            self.create_this_dir(inp=name)

    def create_this_dir(self, inp=None):
        if inp is None:
            inp = self.totinp
        os.mkdir(os.path.join(self.fs_dir_curr, inp))
        self.enter_folder(os.path.join(self.fs_dir_curr, inp))

    def create_new_file(self):
        name = popup_text_input("Enter the name of the file: ")
        if name is not None:
            self.create_this_file(inp=name)

    def create_this_file(self, inp=None):
        if inp is None:
            inp = self.totinp
        self.got_final_result(os.path.join(self.fs_dir_curr, inp))

    def select_this_dir(self):
        self.got_final_result(self.fs_dir_curr)

    def got_final_result(self, fname):
        self.parent.result = fname
        self.parent.exit_editing()

class FilepathPrompt(nps.Autocomplete):
    def __init__(self, *args, startdir="/", **kwargs):
        nps.Autocomplete.__init__(self, *args, **kwargs)

    def auto_complete(self, inp):
        n = len(self.value)
        self.value = self.parent.fs_descr.autocomplete()
        self.move_curs_right(n)

    def move_curs_right(self, n):
        for i in range(len(self.value)-n):
            self.h_cursor_right(10)

    def update_value(self, val):
        n = len(self.value)
        self.value = val
        self.move_curs_right(n)
        self.update()

    def h_delete_left(self, inp):
        super().h_delete_left(inp)
        self.parent.fs_descr.deletechar()

    def h_addch(self, inp):
        super().h_addch(inp)
        self.parent.fs_descr.new_inp(chr(inp))

class FSButtonGrid(nps.SimpleGrid):
    def __init__(self, *args, **kwargs):
        nps.SimpleGrid.__init__(self, *args, **kwargs)
        self.values = [[]]
        self.buttons_indexes = ["sd", "cnd", "cndi", "cnf", "cnfi"]
        self.buttons_text = {
                "sd":"Select this dir",
                "cnd":"Create new dir",
                "cndi":"Create this dir",
                "cnf":"Create new file",
                "cnfi":"Create this file"
                }
        self.button_width = max([len(el) for el in self.buttons_text.values()]) + 2

    def setup_cb(self):
        self.buttons_index_callback = {
                "sd": self.parent.fs_descr.select_this_dir,
                "cnd":self.parent.fs_descr.create_new_dir,
                "cndi":self.parent.fs_descr.create_this_dir,
                "cnf":self.parent.fs_descr.create_new_file,
                "cnfi":self.parent.fs_descr.create_this_file
                }

    def update_buttons(self, butts):
        self.values = [[]]
        for n, but in enumerate(butts):
            if but:
                self.values[0].append(self.create_button(self.buttons_indexes[n], len(self.values[0])))
        self.update()

    def create_button(self, butt_index, nbut):
        return (butt_index, self.buttons_text[butt_index])

    def display_value(self, obj):
        return obj[1]

    def handle_input(self, inp):
        if inp == 10:
            self.button_callback(self.selected_row()[self.edit_cell[1]][0])
        super().handle_input(inp)

    def button_callback(self, but_index):
        self.buttons_index_callback[but_index]()

class FilepathForm(nps.ActionForm):
    def __init__(self, msg, info, startdir, isfile, exist, allow_replace, *args, **kwargs):
        nps.Form.__init__(self, *args, **kwargs)
        self.text = self.add(nps.FixedText, editable=False)
        self.text.value = msg
        self.text.set_editable(False)
        self.text.display()

        self.prompt = self.add(FilepathPrompt, startdir=startdir)
        self.but_grid = self.add(FSButtonGrid, height=1, scroll_exit=True)
        self.fs_descr = self.add(FSDescriptor, startdir=startdir, exist=exist, isfile=isfile, allow_replace=allow_replace, scroll_exit=True)
        self.but_grid.setup_cb()

        self.result = None

    def update_display(self):
        self.curr_root.display()
        self.prompt.set_relyx(0, len(self.fs_dir_curr))

    def get_result(self):
        return self.result
