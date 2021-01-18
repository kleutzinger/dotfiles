"Kevin's vimrc

call plug#begin()
Plug 'justinmk/vim-sneak'
Plug 'tpope/vim-surround'
Plug 'easymotion/vim-easymotion'
Plug 'embark-theme/vim', { 'as': 'embark' }
Plug 'liuchengxu/vim-which-key'
Plug 'vim-airline/vim-airline'
Plug 'vim-airline/vim-airline-themes'
Plug 'gioele/vim-autoswap'
Plug 'dag/vim-fish'
" https://github.com/preservim/nerdtree
Plug 'preservim/nerdtree'
Plug 'godlygeek/tabular'
Plug 'plasticboy/vim-markdown'
call plug#end()

" vim-markdown has weird folding
let g:vim_markdown_folding_disabled = 1

" Exit Vim if NERDTree is the only window left.
autocmd BufEnter * if tabpagenr('$') == 1 && winnr('$') == 1 && exists('b:NERDTree') && b:NERDTree.isTabTree() |
    \ quit | endif

nnoremap <silent> <expr> <leader>f  g:NERDTree.IsOpen() ? "\:NERDTreeClose<CR>" : bufexists(expand('%')) ? "\:NERDTreeCWD<CR>" : "\:NERDTreeCWD<CR>"
let NERDTreeShowHidden=0

"show spaces
set list
set lcs+=space:·

colorscheme embark
let g:embark_terminal_italics = 1
map <leader><leader>w <Plug>(easymotion-bd-w)
set termguicolors
" allow quit via single keypress (Q)
map Q :qa<CR>

"turn sneak into easymotion-style
"let g:sneak#label = 1
map f <Plug>Sneak_f
map F <Plug>Sneak_F
map t <Plug>Sneak_t
map T <Plug>Sneak_T
let g:sneak#use_ic_scs = 1

set incsearch
" Use <C-L> to clear the highlighting of :set hlsearch.
if maparg('<C-L>', 'n') ==# ''
  nnoremap <silent> <C-L> :nohlsearch<C-R>=has('diff')?'<Bar>diffupdate':''<CR><CR><C-L>
endif

" Run current file
nnoremap <F9> :!clear && %:p<Enter>

inoremap <C-w> <C-\><C-o>dB
inoremap <C-BS> <C-\><C-o>db

" https://www.youtube.com/watch?v=XA2WjJbmmoM
filetype plugin on
set path+=**
set wildmenu
set showcmd
"Disable arrow keys (temporary)
noremap <up> <C-w><up>
noremap <down> <C-w><down>
noremap <left> <C-w><left>
noremap <right> <C-w><right> 
set tabstop=4 softtabstop=0 expandtab shiftwidth=4 smarttab
set mouse=a
set wrapscan
" Ctrl + Y to redo (u to undo)
"nnoremap <C-Y> <C-R>
" TIPS:
" in insert mode press ctrl + o to do a single 

set ignorecase
set smartcase
set number relativenumber
" O
" u
" change numbers look in insert mode
:augroup numbertoggle
:  autocmd!
:  autocmd BufEnter,FocusGained,InsertLeave * set relativenumber
:  autocmd BufLeave,FocusLost,InsertEnter   * set norelativenumber
:augroup END

" exit insert mode with `hk`, but you only have 1 second
" https://forum.colemak.com/topic/1477-i-need-a-rarely-used-twokey-combination-of-home-row-keys-for-vim-esc/#p10747
inoremap hk <ESC>

" select last paste in visual mode
nnoremap <expr> gb '`[' . strpart(getregtype(), 0, 1) . '`]'

" https://forum.colemak.com/topic/50-colemak-vim/#p184
" COLEMAK BINDINGS
noremap K J
noremap J K
inoremap jj <ESC>
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

highlight LineNr term=bold cterm=NONE ctermfg=DarkGrey ctermbg=NONE gui=NONE guifg=DarkGrey guibg=NONE
