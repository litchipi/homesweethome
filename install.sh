#!/bin/sh

sudo apt install python3-pip direnv tmux
pip3 install base58 termenu

sudo cp -r ./copydirs/tmux/ ~/.tmux
echo "############# HOME SWEET HOME #################" >> ~/.bashrc
echo "eval '$(direnv hook bash)'">>~/.bashrc
echo "################## END ########################" >> ~/.bashrc
