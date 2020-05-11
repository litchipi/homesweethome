#!/usr/bin/env python3

from base58 import b58encode_check
from hashlib import sha512

import argparse
import json
import zipfile
import shutil
import sys
import re
import glob
import os
import time
import configparser
from termenu import show_menu, Minimenu, OptionGroup
import getpass

SPECIAL_CONFIGS = {
        "nvim":"-u"
        }

global DIRECTORY_PROJECTS
DIRECTORY_PROJECTS = os.getenv("HOME") + "/"

global CHOICE_ONLY
CHOICE_ONLY = False

global EXCLUDE_PROJECTS
EXCLUDE_PROJECTS = list()

def create_dir(path):
    name = input("Entrez le nom du dossier: ")
    os.mkdir(path + "/" + name)

def choose_directory():
    startdir = DIRECTORY_PROJECTS
    currdir = os.path.abspath(startdir)
    cmds = ["<New dir>", "[Select this dir]"]
    while True:
        gen = os.walk(currdir)
        root, dirs, files = next(gen)
        el = create_menu({currdir:(0, cmds + [".."] + list(dirs))}).replace("\t", "")
        print(currdir)
        print(el)
        if el in cmds:
            n = cmds.index(el)
            if n == 0: 
                create_dir(currdir)
                continue
            elif n == 1:
                return root
        currdir = os.path.abspath(currdir + "/" + el)

def yes_no_prompt(msg):
    os.system("clear")
    print(msg)
    return (Minimenu(["Yes", "No"]).show() == "Yes")

def create_menu(options):
    # fixed extra spaces in items
    options = {re.sub("\s+", " ", k.strip()):val for k, val in options.items()}

    seen = set()
    options = {k:x for k, x in options.items() if k not in seen and not seen.add(k)}

    menuopt = [OptionGroup(k, ["\t" + el for el in v[1]]) for k, v in sorted(options.items(),
                    key = lambda x: x[1][0])]

    os.system("clear")
    return show_menu("", menuopt, height=100)

def sanitize_name(name):
    accepted = "".join([str(i) for i in range(10)] +
                       [chr(el) for el in range(ord("A"), ord("Z")+1)] +
                       [chr(el) for el in range(ord("a"), ord("z")+1)])
    res = str()
    for n, c in enumerate(name):
        if c in accepted:
            res += c
        elif (n != 0) and (res[n-1] != "_"): 
            res += "_"
    return res

def encrypt_backup_file(fname, pwd):
    shutil.move(fname, fname.replace(".zip", ""))

def decrypt_backup_file(fname, pwd):
    shutil.move(fname, fname + ".zip")

def exec_command(cmd, cfg, projects):
    get_pwd = lambda i: b58encode_check(sha512(i.encode()).digest())

    if cmd == "New":
        while True:
            name = input("Enter project name: ")
            n = sanitize_name(name)
            try:
                cfg.add_section(n)
                break
            except configparser.DuplicateSectionError:
                print("Name already exists, please enter a new name")
        cfg[n]["display_name"] = name
        cfg[n]["last_used"] = str(int(time.time()))
#        d = input("Enter parent directory in which project directory will be created:\n\t")
        d = choose_directory()
        cfg[n]["env_directory"] = os.path.abspath(d)
        cfg[n]["load_script"] = "load.sh"
#        "save":tmux_save + " " + session_name + " " + replace_script + " " + fname,

        return cfg, True

    elif cmd == "Load":
        d = choose_directory()
#        d = os.path.abspath(input("Enter project directory: "))
        name = input("Enter name for this project (default: {}): ".format(d.split("/")[-1]))
        if name == "": name = d.split("/")[-1]
        n = sanitize_name(name)
        try:
            cfg.add_section(n)
        except configparser.DuplicateSectionError:
            sure = yes_no_prompt(
                        "This project already exists, are you sure you want to override it ?")
            if not sure: return None, True
        cfg[n]["display_name"] = name
        cfg[n]["env_directory"] = d
        cfg[n]["load_script"] = "load.sh"
        cfg[n]["last_used"] = str(int(time.time()))
        return cfg, True

    elif cmd == "Delete":
        proj_link = {data["display_name"]:name for name, data in projects.items()}
        name = show_menu("Select project to delete", list(proj_link.keys()))

        project = proj_link[name]
        if os.path.isdir(cfg[name]["env_directory"]):
            deldata = yes_no_prompt("Delete project data directory ?\n\t" + cfg[name]["env_directory"])
            if deldata:
                shutil.rmtree(cfg[name]["env_directory"])
        del cfg[project]
        return cfg, True

    elif cmd == "Backup":
        proj_link = {data["display_name"]:name for name, data in projects.items()}
        if len(proj_link.keys()) == 0: return None, True
        name = show_menu("Select project to backup", list(proj_link.keys()))

        p = getpass.getpass("Enter a password to encrypt backup (unencrypted if none): ")
        if p != "":
            check = ""
            pwd = get_pwd(p)
            while pwd != check:
                check = get_pwd(getpass.getpass("Verify password: "))
        else:   pwd = None

        include_git = yes_no_prompt("Include git repository to backup ?")

        forbidden = []
        if not include_git: forbidden += [".git", ".gitignore"]
        zf = zipfile.ZipFile(os.path.abspath("./backup/" + name + ".zip"), mode='w', 
                                                           compression=zipfile.ZIP_DEFLATED)
        zf.writestr("project_cfg", json.dumps(dict(cfg[name])))
        cdir = os.curdir
        os.chdir(cfg[name]["env_directory"] + "/..")
        for root, d, files in os.walk(os.path.relpath(cfg[name]["env_directory"])):
            if not all([el not in root for el in forbidden]): continue
            for f in files:
                if all([el not in f for el in forbidden]):
                    zf.write(os.path.join(root, f))
        zf.close()
        os.chdir(cdir)
        if pwd is not None:
            encrypt_backup_file(os.path.abspath("./backup/" + name + ".zip"), pwd)
        return cfg, True

    elif cmd == "Restore":
        pwd=None
        poss = list(glob.glob("./backup/*"))
        if len(poss) == 0: return None, True
        fname = show_menu("Select project to restore", poss)
        fpath = ""
        while fpath == "" or not os.path.isdir(fpath):
            fpath = os.path.abspath(input("Enter path where to extract it: "))

        try:
            zf = zipfile.ZipFile(fname, mode='r', compression=zipfile.ZIP_DEFLATED)
        except:
            decrypt_backup_file(fname, get_pwd(getpass.getpass("Enter the password")))
            zf = zipfile.ZipFile(fname, mode='r', compression=zipfile.ZIP_DEFLATED)

        project_config = json.loads(zf.read("project_cfg", pwd=pwd).decode())
        zf.extractall(path=fpath, pwd=pwd)
        zf.close()
        projname = sanitize_name(project_config["display_name"])
        os.system("chmod +x {}/{}/.load.sh".format(fpath, projname))

        cfg[projname] = project_config
        os.remove(fpath + "/project_cfg")
        return cfg, True
    return None, False

def save_cfg(cfg, cfgfile):
    if cfg is not None:
        with open(cfgfile, "w") as fichier:
            cfg.write(fichier)


def main(datapath, rerun=False, cfg_fname="projects.ini"):
    cfgfile = os.path.abspath(datapath + cfg_fname)
    cfg = configparser.ConfigParser()
    cfg.read(cfgfile)

    projects = dict()
    projectlist = cfg.sections()
    for project in projectlist:
        projects[project] = {k:v for k, v in cfg[project].items()}
        if not rerun and not os.path.isdir(projects[project]["env_directory"]):
            del projects[project]
            del cfg[project]
    projects_menu_link = {data["display_name"]:(name, data["last_used"])
                                                        for name, data in projects.items()}
    projects_menu = [el[0] for el in sorted(projects_menu_link.items(),
                    key=lambda x: int(x[1][1]), reverse=True) if el[0] not in EXCLUDE_PROJECTS]

    commands = ["Quit"]
    if not CHOICE_ONLY:
        commands = ["New", "Load", "Delete", "Backup", "Restore"] + commands
    usr = create_menu({"Projects":(0, projects_menu), "Commands":(1, commands)}).replace("\t", "")
    if usr in commands: 
        cfg, re_run = exec_command(usr, cfg, projects)
        save_cfg(cfg, cfgfile)
        if re_run:
            return main(datapath, cfg_fname=cfg_fname, rerun=True)
        else:
            return '^-$?quit_script?$-^'
    elif usr != "":
        pk = projects_menu_link[usr][0]
        cfg[pk]["last_used"] = str(int(time.time()))
        save_cfg(cfg, cfgfile)
        return projects[pk]["env_directory"] + "/." + projects[pk]["load_script"]
    else:
        return None

def choose_conf(confdir):
    choices = list([os.path.basename(f) for f in glob.glob(confdir + "/*")])
    choices.append("System configuration")
    choice = show_menu("Select config file to choose for {}".format(confdir), choices)
    if choice == "System configuration": choice = ""
    else:
        choice = os.path.abspath(confdir + "/" + choice)
    return os.path.basename(choice)

def check_dir_exist(d):
    if not os.path.isdir(d):
        os.mkdir(d)

def init_gitrepo(d):
    os.chdir(d)
    os.system("git init")
    os.system("touch README")
    os.system("git add *")
    os.system("git commit -m 'Project initialisation'")

    os.system("echo \".gitignore\n.alias/*\n.load.sh\n.envrc\n.*.swp\n.*.swo\n.*_ses\" > .gitignore")
    os.chdir("..")
    os.system("clear")

def create_home_symlink(name, script, is_dir=True):
    os.symlink(os.getenv("HOME") + "/" + name + ("/"*is_dir), os.path.dirname(script) + "/" + name)


def check_init_filesystem(script, rootdir):
    cfgdir = rootdir + "/config"
    bckdir = rootdir + "/backup"
    check_dir_exist(os.path.dirname(script))
    check_dir_exist(cfgdir)
    check_dir_exist(bckdir)

    if not os.path.isfile(script):
        config_files = dict()
        for conf_type in ["tmux"] + list(SPECIAL_CONFIGS.keys()):
            check_dir_exist(cfgdir + "/" + conf_type)
            config_files[conf_type] = choose_conf(cfgdir + "/" + conf_type)
        create_script(script, config_files, cfgdir)
        create_home_symlink(".bashrc", script, False)
        create_home_symlink(".tmux", script)
        create_home_symlink(".local", script)
        create_home_symlink(".config", script)

    if not os.path.isdir(os.path.dirname(script) + "/.git"):
        init_gitrepo(os.path.dirname(script))

def create_script(fname, cfg, config_dir, envrc_vars={}):
    bckdir = config_dir + "/../backup"
    session_name = fname.split("/")[-2]
    session_dir_path = os.path.dirname(fname)

    tmux_save = config_dir + "/aliases/save_tmux_session.sh"
    tmux_switch = config_dir + "/aliases/switch_tmux_session.sh"
    tmux_quit = config_dir + "/aliases/quit_tmux_session.sh"

    envrc_vars["project_manager_script_path"] = os.path.abspath(config_dir + "/..")
    envrc_vars["HOME"] = os.path.abspath(session_dir_path)

    replace_script = config_dir + "/replace_session_script.py"

    create_alias = lambda d, a, c: "echo -e '#!/bin/bash\n" + c + "' > " + d + "/" + a
    all_aliases = {
        "save":tmux_save + " " + session_name + " " + replace_script + " " + fname,
        "switch":tmux_switch + " " + session_name +"_socket",
        "quit":tmux_quit + " " + session_name + "_socket",
        }

    script = ["#!/bin/bash"]
    script.append("")
    script.append("USER_HOME=$(cat /etc/passwd|grep $(whoami)|cut -d ':' -f 6)")
    script.append("PROJECT_ABSPATH="+session_dir_path)
    session_dir="$PROJECT_ABSPATH"
    script.append("if [ $# -eq 1 ]; then")
    script.append("tmux_socket_name=$1")
    script.append("else")
    script.append("tmux_socket_name=\"" + session_name + "_socket\"")
    script.append("fi")
    script.append("tmux_cmd=\"tmux -L $tmux_socket_name\"")

    script.append("mkdir -p " + session_dir + "/.log")
    script.append(config_dir + "/backup_log_files.py " + session_dir + "/.log/ " + bckdir)
    script.append("mkdir -p " + session_dir + "/.alias")

    for alias, cmd in all_aliases.items():
        script.append(create_alias(session_dir + "/.alias", alias, cmd))
        script.append("chmod +x " + session_dir + "/.alias/" + alias)
        script.append("")

    for name, opt in SPECIAL_CONFIGS.items():
        if cfg[name] != "":
            script.append(name + "_cmd=$(whereis " + name + "|cut -d ' ' -f 2)")
            script.append("if [ ! -z \"${}\" ]".format(name + "_cmd"))
            script.append("then")
            script.append(create_alias(session_dir + "/.alias", name,
                "'$" + name + "_cmd '" + opt + " " + config_dir + "/" + name + "/" + cfg[name]
                + " $@"))
            script.append("chmod +x " + session_dir + "/.alias/" + name)
            script.append("fi")
            script.append("")


    script.append("#TMUXSOCKETNAME:" + session_name + "_socket:SOCKETEND")
    script.append("echo \"PATH_add .alias\n" +
            "\n".join(["export " + key.upper() + "=" + val for key, val in envrc_vars.items()]) + 
            "\" > " + session_dir + "/.envrc")
    script.append("direnv allow " + session_dir + "/")
    script.append("")

    start_log_cmd = "/bin/bash " + config_dir + "/../scripts/toggle_logging.sh"
    script.append("echo -e '. '$USER_HOME'/.bashrc\n{}' > $PROJECT_ABSPATH/.bash_profile".format(start_log_cmd))

    script.append("$tmux_cmd -f " + config_dir + "/tmux/" + cfg['tmux'] + " new-session -d -s " + session_name + " -c " + session_dir)

    #script.append("$tmux_cmd set -g default-command ")
    script.append("sleep 0.2")

    script.append("#TMUXSESSION:START")
    welcome_message = "Session " + session_name + " initialized" + \
            "\nTo enable logging, please enter command \'save\' and \'quit\', then restart the session"
    script.append("""$tmux_cmd send-keys -t {}:0.0 'clear && echo "{}"' Enter""".format(session_name, welcome_message))
    script.append("$tmux_cmd select-window -t {}:0.0".format(session_name))
    script.append("$tmux_cmd attach-session -t {}".format(session_name))

    script.append("#TMUXSESSION:END")

    with open(fname, "w") as fichier:
        fichier.write("\n".join(script) + "\n")
    os.system("chmod +x {}".format(fname))

def launch(workdir):
    script = None
    while script is None:
        script = main(workdir)
        if script == '^-$?quit_script?$-^': script = False
    if script == False:
        os.system("clear")
        sys.exit(0)
    check_init_filesystem(script, os.path.abspath("."))
    e = yes_no_prompt("Do you want to execute script:\n\t{} ?".format(script))

    with open("/tmp/hsh_path", "w") as f:
        f.write(script)
    sys.exit(0)
    #cmd = "eval '$(direnv export bash)' && " + script
    #os.system(cmd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--choice-to-file", type=str,
            help="choose a project from the list, and output its name to stdin")
    parser.add_argument("-x", "--exclude", type=str, nargs='*',
            help="do not include this project in the list, can pass multiple projects with syntax: \"-x proj1,proj2,proj3\"")
    parser.add_argument("-d", "--projects-dir", type=str,
            help="directory from which walk starts")
    args = parser.parse_args()

    if args.projects_dir:
        DIRECTORY_PROJECTS = args.projects_dir

    workdir = os.path.abspath(os.path.dirname(sys.argv[0])) + "/"
    os.chdir(workdir)

    if args.exclude and args.exclude != "":
        EXCLUDE_PROJECTS = args.exclude

    if args.choice_to_file:
        CHOICE_ONLY = True
        script = main(workdir)
        if (script is not None) and (script != '^-$?quit_script?$-^'):
            with open(args.choice_to_file, 'w') as fichier:
                fichier.write(script)
    else:
        while True:
            launch(workdir)
            break
