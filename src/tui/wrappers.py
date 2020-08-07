#!/usr/bin/env python3
#-*-encoding:utf-8*-

import os
import npyscreen as nps

from .filesystem_open_create import FilepathForm

def create_button(callback, ident):
    class CustomButton(nps.ButtonPress):
        CUST_BUTTON_ID = ident
        CUST_CUTTON_CALLBACK = callback
        def whenPressed(self):
            self.CUST_CUTTON_CALLBACK(self.CUST_BUTTON_ID)
    return CustomButton

def get_filepath(prompt, info="", isfile=True, choose_existing=True):
    path_prompt = FilepathForm(prompt, info, os.path.curdir, isfile, choose_existing, True)
    path_prompt.edit()
    return path_prompt.get_result()
