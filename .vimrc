"Kevin's vimrc
let mapleader = ','
so ~/.config/coc/config.vim

call plug#begin()
Plug 'justinmk/vim-sneak'
Plug 'tpope/vim-surround'
Plug 'easymotion/vim-easymotion'
Plug 'embark-theme/vim', { 'as': 'embark' }
Plug 'liuchengxu/vim-which-key'
"Plug 'vim-airline/vim-airline'
"Plug 'vim-airline/vim-airline-themes'
Plug 'itchyny/lightline.vim'
Plug 'gioele/vim-autoswap'
Plug 'dag/vim-fish'
Plug 'preservim/nerdtree'
Plug 'godlygeek/tabular'
Plug 'plasticboy/vim-markdown'
Plug 'preservim/nerdcommenter'
Plug 'glacambre/firenvim', { 'do': { _ -> firenvim#install(0) } }
Plug 'sbdchd/neoformat'
Plug 'Raimondi/delimitMate'
Plug 'tpope/vim-sleuth'
Plug 'posva/vim-vue'
Plug 'tpope/vim-eunuch'
Plug 'tpope/vim-dispatch'
call plug#end()
" General colors


augroup highlight_yank
  autocmd!
  au TextYankPost * silent! lua vim.highlight.on_yank{higroup="IncSearch", timeout=300}
augroup END
let g:lightline = {'colorscheme': 'embark'}

au BufReadPost *.lr set syntax=markdow
" autocmd BufNewFile * if !empty(&filetype) | execute 'silent! 1s/.*/#!\/usr\/bin\/env ' . &filetype . '\r\r'| :startinsert | endif
" vim-markdown has weird folding
let g:vim_markdown_folding_disabled = 1
set omnifunc=syntaxcomplete#Complete

" Exit Vim if NERDTree is the only window left.
autocmd BufEnter * if tabpagenr('$') == 1 && winnr('$') == 1 && exists('b:NERDTree') && b:NERDTree.isTabTree() |
    \ quit | endif

nnoremap <silent> <expr> <leader>f  g:NERDTree.IsOpen() ? "\:NERDTreeClose<CR>" : bufexists(expand('%')) ? "\:NERDTreeCWD<CR>" : "\:NERDTreeCWD<CR>"
let NERDTreeShowHidden=0
nnoremap <leader>nf :Neoformat<Enter>
"set clipboard=unnamedplus

"show spaces
set list
set lcs+=space:·

colorscheme embark
let g:embark_terminal_italics = 1
map <leader><leader>w <Plug>(easymotion-bd-w)
set termguicolors
":hi! Normal ctermbg=NONE guibg=NONE
":hi! CursorLineNr guibg=NONE
":set notermguicolors
":set termguicolors
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
set tabstop=4 softtabstop=0 expandtab shiftwidth=4 smarttab smartindent
set autoindent
set mouse=a
set wrapscan

set lazyredraw
set ignorecase
set smartcase
set number relativenumber
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


let g:firenvim_config = {
    \ 'globalSettings': {
        \ 'alt': 'all',
    \  },
    \ 'localSettings': {
        \ '.*': {
            \ 'cmdline': 'neovim',
            \ 'content': 'text',
            \ 'priority': 0,
            \ 'selector': 'textarea',
            \ 'takeover': 'never',
        \ },
    \ }
\ }
