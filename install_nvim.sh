sudo apt install neovim
curl -fLo ~/.local/share/nvim/site/autoload/plug.vim --create-dirs \
    https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
echo "When using any nvim configuration for the first time, please run \":PlugInstall\" in order to install the needed plugins\n"
