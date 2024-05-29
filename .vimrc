let mapleader = ','

let &t_ut=''

set nrformats+=alpha
set updatetime=300


au BufReadPost *.lr set syntax=markdown
"run in python
imap <F5> <Esc>:w<CR>:!clear;python %<CR>
nmap <F5> <Esc>:w<CR>:!clear;python %<CR>

nnoremap <leader>nf :Neoformat<Enter>

set clipboard=unnamedplus

let g:neoformat_enabled_markdown = ['prettier']
"whitespace
set list

tnoremap <Esc> <C-\><C-n>:q!<CR>
"wrap around
set whichwrap+=<,>,[,]

set termguicolors
:hi! Normal ctermbg=BLACK guibg=NONE
":hi! CursorLineNr guibg=NONE
:set notermguicolors
":set termguicolors
" allow quit via single keypress (Q)
map Q :qa<CR>

" https://www.youtube.com/watch?v=XA2WjJbmmoM
filetype plugin on
set path+=**
set wildmenu
set showcmd
set tabstop=4 softtabstop=0 expandtab shiftwidth=4 smarttab smartindent
set autoindent
set mouse=a
set wrapscan

set lazyredraw
set ignorecase
set smartcase
inoremap hk <ESC>
vnoremap p pgvy

" https://forum.colemak.com/topic/50-colemak-vim/#p184
" COLEMAK BINDINGS
"noremap K J
"noremap J K
noremap h k
noremap j h
noremap k j

noremap gh gk
noremap gj gh
noremap gk gj

noremap zh zk
"zK does not exist
noremap zj zh
noremap zJ zH
noremap zk zj
"zJ does not exist
noremap z<Space> zl
noremap z<S-Space> zL
noremap z<BS> zh
noremap z<S-BS> zH

noremap <C-w>h <C-w>k
noremap <C-w>H <C-w>K
noremap <C-w>j <C-w>h
noremap <C-w>J <C-w>H
noremap <C-w>k <C-w>j
noremap <C-w>K <C-w>J
noremap <C-w><Space> <C-w>l
noremap <C-w><S-Space> <C-w>L
noremap <C-w><S-BS> <C-w>H

