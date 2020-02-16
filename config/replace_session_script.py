#!/usr/bin/env python3

import os
import sys

def replace_source(data, socket_name):
    return "\n".join(
        [line.split(" ")[0].replace("tmux", "tmux -L " + socket_name) + " " + " ".join(line.split(" ")[1:])
        for line in data.split("\n")])

dest = sys.argv[1]
source = sys.argv[2]

with open(dest, "r") as fichier:
    datadest = fichier.read()

with open(source, "r") as fichier:
    datasource = fichier.read()

tmux_socket_name = datadest.split("#TMUXSOCKETNAME:")[1].split(":SOCKETEND")[0]

head = datadest.split("#TMUXSESSION:START")[0]
tail = datadest.split("#TMUXSESSION:END")[1]

forbidden = ["new-session", "#!", "has-session"]
datasource = "\n".join([l for l in datasource.split("\n")
    if all([el not in l for el in forbidden])])

result = head + "#TMUXSESSION:START\n" + replace_source(datasource, tmux_socket_name) + "#TMUXSESSION:END\n" + tail
result = "\n".join([el for el in result.split("\n") if el != ""])
os.remove(source)
with open(dest, "w") as fichier:
    fichier.write(result)
