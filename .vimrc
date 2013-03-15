syntax enable
colorscheme solarized
set background=dark
set guifont=Menlo:h15
let g:solarized_hitrail=1
"set columns=90
"set lines=60

set laststatus=2
set showmode
set showcmd
set ruler
set number
set numberwidth=3

set encoding=utf-8

set wrap
set tabstop=2
set shiftwidth=2
set softtabstop=2
set expandtab
set smartindent
set list listchars=tab:\ \ ,trail:·

" Tab Completion
set wildmenu
set wildignore+=.git,*.pyc,.sass-cache/,.DS_Store,*.mo
set wildmode=list:longest,list:full

" Search
set hlsearch
set incsearch
set ignorecase
set smartcase

" Command-T
let g:CommandTMaxHeight=20

au BufRead,BufNewFile {Gemfile,Vagrantfile} set ft=ruby

nnoremap <silent> <F6> :let _s=@/<Bar>:%s/\s\+$//e<Bar>:let @/=_s<Bar>:nohl<CR>

let g:GPGExecutable="/usr/local/bin/gpg"
let g:GPGPreferSign=1
let g:GPGDefaultRecipients=["3082B5A3"]
let g:GPGUseAgent=0
