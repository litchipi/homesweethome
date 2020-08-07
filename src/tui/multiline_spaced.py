#!/usr/bin/env python3
#-*-encoding:utf-8*-

import npyscreen as nps

class SepMultiLineAction(nps.MultiLineAction):
    def __init__(self, *args, **kwargs):
        nps.MultiLineAction.__init__(self, *args, **kwargs)
        self.sanitize_values()

    def sanitize_values(self):
        for n, val in enumerate(self.values):   #Eliminate head None
            if val is None:
                continue
            break
        self.values = self.values[n:]

        for i in range(len(self.values)):       #Eliminate tail None
            n = len(self.values)-(1+i)
            val = self.values[n]
            if val is None:
                continue
            break
        self.values = self.values[:n+1]
        self.height = len(self.values) + 1
        self.max_height = self.height

    def h_cursor_line_down(self, inp):
        while (self.values[(self.cursor_line+1)%len(self.values)] == None):
            super().h_cursor_line_down(inp)
        super().h_cursor_line_down(inp)

    def h_cursor_line_up(self, inp):
        while (self.values[self.cursor_line-1] == None):
            super().h_cursor_line_up(inp)
        super().h_cursor_line_up(inp)

    def display_value(self, obj):
        if (obj == None):
            return ""
        else:
            return super().display_value(obj)

class SepMultiLine(nps.MultiLine):
    def __init__(self, *args, **kwargs):
        nps.MultiLine.__init__(self, *args, **kwargs)
        self.sanitize_values()

    def sanitize_values(self):
        for n, val in enumerate(self.values):   #Eliminate head None
            if val is None:
                continue
            break
        self.values = self.values[n:]

        for i in range(len(self.values)):       #Eliminate tail None
            n = len(self.values)-(1+i)
            val = self.values[n]
            if val is None:
                continue
            break
        self.values = self.values[:n+1]
        self.height = len(self.values) + 1
        self.max_height = self.height

    def h_cursor_line_down(self, inp):
        while (self.values[(self.cursor_line+1)%len(self.values)] == None):
            super().h_cursor_line_down(inp)
        super().h_cursor_line_down(inp)

    def h_cursor_line_up(self, inp):
        while (self.values[self.cursor_line-1] == None):
            super().h_cursor_line_up(inp)
        super().h_cursor_line_up(inp)

    def display_value(self, obj):
        if (obj == None):
            return ""
        else:
            return super().display_value(obj)
