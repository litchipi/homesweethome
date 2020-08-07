#!/usr/bin/env python3
#-*-encoding:utf-8*-

import npyscreen as nps

def popup_text_input(prompt):
    form = nps.Popup()
    form.add(nps.FixedText, editable=False, value=prompt)
    inp = form.add(nps.Textfield)
    form.edit()
    return inp.value

def popup_information(msg, wide=True):
    if wide:
        form = nps.PopupWide()
    else:
        form = nps.Popup()
    text = form.add(nps.FixedText, value=msg, editable=False)
    text.display()
    form.edit()

def popup_error(msg, add_info=None):
    form = nps.Popup(name="Error")
    text = form.add(nps.FixedText, value=msg, editable=False)
    if (add_info is not None):
        info = form.add(nps.FixedText, value=add_info, editable=False, relx=8)
    form.edit()
