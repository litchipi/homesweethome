#!/bin/bash
current_tmux_session=$(tmux display-message -p '#S')

if [${#raw_choices[@]} -le 1]; then
    $PROJECT_MANAGER_SCRIPT_PATH/project_manager.py -c ./.tmp_choice -x $current_tmux_session
    proj_choice=$(cat .tmp_choice)
    rm .tmp_choice
    tmux -L $1 detach
    $proj_choice $1
else
    raw_choices=( $(tmux -L $1 ls | cut -d ':' -f 1) )
    choices=' "Open project", '
    exclude_projs=
    for choice in "${raw_choices[@]}"
    do
        if [[ "$choice" != "$current_tmux_session" ]]; then
            choices+=' "'$choice'",'
        else
            exclude_projs+=$choice','
        fi
    done
    echo -e 'from termenu import show_menu\nchoice = show_menu("Choose a session to switch", ['$choices'])\nwith open("./.tmp_'$1'_session_switch", "w") as fichier: fichier.write(choice)' > .tmp_python_script.py
    python3 .tmp_python_script.py
    rm .tmp_python_script.py
    session_switch=$(cat .tmp_$1_session_switch)
    rm .tmp_$1_session_switch
    if [[ "$session_switch" == "Open project" ]]; then
        echo "Choosing project"
        echo $PROJECT_MANAGER_SCRIPT_PATH/project_manager.py -c ./.tmp_choice -x $exclude_projs
        $PROJECT_MANAGER_SCRIPT_PATH/project_manager.py -c ./.tmp_choice -x $exclude_projs
        proj=$(cat .tmp_choice)
        rm .tmp_choice
        tmux -L $1 detach
        $proj $1
        tmux -L $1 attach
    else
        echo "switching project"
        tmux -L $1 switchc -t $session_switch
    fi
fi
