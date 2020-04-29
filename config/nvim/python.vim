call plug#begin()
Plug 'davidhalter/jedi-vim'

Plug 'prabirshrestha/async.vim'
Plug 'prabirshrestha/vim-lsp'
Plug 'mattn/vim-lsp-settings'

Plug 'roxma/nvim-yarp'
Plug 'ncm2/ncm2'
Plug 'ncm2/ncm2-vim-lsp'
Plug 'ncm2/ncm2-path'
Plug 'ncm2/ncm2-neoinclude' | Plug 'Shougo/neoinclude.vim'
Plug 'ncm2/ncm2-syntax' | Plug 'Shougo/neco-syntax'

Plug 'vim-airline/vim-airline'
Plug 'vim-airline/vim-airline-themes'
Plug 'scrooloose/nerdtree'
Plug 'sbdchd/neoformat'
Plug 'terryma/vim-multiple-cursors'
Plug 'neomake/neomake'

Plug 'thaerkh/vim-workspace'
Plug 'majutsushi/tagbar'
call plug#end()



" GENERAL OPTIONS
set completeopt=noinsert,menuone,noselect
set undofile
set shortmess+=c
highlight SignColumn guibg=<X>
set noswapfile
if &encoding != 'utf-8'
    set encoding=utf-8              "Necessary to show Unicode glyphs
endif
set autoindent
set smartindent
set shiftwidth=4
set tabstop=4
set smarttab
set expandtab
set number
"set completeopt-=preview
au BufWritePost * if v:this_session != "" | exe "mksession! ".v:this_session




" INTERFACE
highlight Pmenu ctermbg=8 guibg=#606060
highlight PmenuSel ctermbg=1 guifg=#dddd00 guibg=#1f82cd
highlight PmenuSbar ctermbg=0 guibg=#d6d6d6
hi LineNr ctermfg=green
" set number                  " add line numbers
let g:indentLine_setColors = 1
let g:indentLine_color_term = 1
let g:indentLine_char = '┊'
syntax on
if has("termguicolors") && has("nvim") " set true colors on NeoVim
    set termguicolors
endif
set background=dark


" KEYBOARD
let g:mapleader = '$'
nnoremap <leader>d :bnext<CR>
nnoremap <leader>z :enew<CR>
nnoremap <leader>q :bprevious<CR>
nnoremap <leader>s :bd<CR>

nnoremap <leader>e :wincmd w<CR>
nnoremap <leader>r :vsplit<CR>
nnoremap <leader>t :wincmd o<CR>

nnoremap <Tab> :NERDTreeToggle<CR>
nnoremap <Tab> :NERDTreeToggle<CR>
nnoremap <leader>a :TagbarToggle<CR>
nnoremap <leader>" :lnext<CR>
nnoremap <leader>& :lprevious<CR>


" LSP
let g:lsp_fold_enabled = 0
let g:lsp_diagnostics_enabled = 0         " disable diagnostics support



" NCM2
autocmd BufEnter * call ncm2#enable_for_buffer()



" VIM WORKSPACE (SESSION MANAGER)
let g:workspace_autosave_always = 1
let g:workspace_persist_undo_history = 0
let g:workspace_create_new_tabs = 0
let g:workspace_session_name = '.session.vim'



" AIRLINE (STATUS BAR & THEME)
let g:airline_theme='deus'
let g:airline#extensions#tabline#enabled = 1
let g:airline#extensions#tabline#show_splits = 0
let g:airline#extensions#tabline#formatter = 'unique_tail'
let g:airline#extensions#tabline#left_sep = ' '
let g:airline#extensions#branch#enabled = 1
let g:airline#extensions#neomake#enabled = 1
let g:airline#extensions#tabline#enabled = 1
let g:airline#extensions#tabline#buffer_nr_show = 1



" NEOFORMAT (FORMATTING)
let g:neoformat_basic_format_align = 1
let g:neoformat_basic_format_retab = 1
let g:neoformat_basic_format_trim = 1



" NEOMAKE (CODE CHECKING)
let g:neomake_highlight_columns = 0
highlight NeomakeWarningSign guifg=#ff9932
call neomake#configure#automake('w')
" hi NeomakeVirtualtextError ctermbg=234 ctermfg=238 guibg=
hi NeomakeVirtualtextWarning guifg=#512866




" SPECIFIC PYTHON CONFIGURATION

let g:neomake_python_enabled_makers = ['flake8']
let g:jedi#goto_command = "<leader>é"
let g:jedi#goto_stubs_command = ""
let g:jedi#rename_command = ""
let g:jedi#usages_command = ""
let g:jedi#show_call_signatures = 0

autocmd BufWritePre *.py Neoformat
autocmd BufWritePost *.py Neomake
autocmd BufWinEnter *.py Neomake
