#!/bin/sh

sudo apt install python3-pip direnv tmux
pip3 install base58 termenu

cd ./copydirs/
    cd ./tmux/
        mkdir -p plugins && cd ./plugins
        git clone https://github.com/jimeh/tmux-themepack
        cp ../custom.tmuxtheme ./tmux-themepack
    cd .. && mv ./plugins/ ~/.tmux/
cd ..

echo "############# HOME SWEET HOME #################" >> ~/.bashrc
echo "eval '$(direnv hook bash)'">>~/.bashrc
echo "################## END ########################" >> ~/.bashrc
