inoremap <silent><expr> <TAB>
                  \ pumvisible() ? "\<C-n>" :
                  \ <SID>check_back_space() ? "\<TAB>" :
                  \ coc#refresh()
inoremap <expr><S-TAB> pumvisible() ? "\<C-p>" : "\<C-h>"
"inoremap <silent><expr> <cr> pumvisible() ? coc#_select_confirm()
"                              \: "\<C-g>u\<CR>\<c-r>=coc#on_enter()\<CR>"

nmap <leader>rn <Plug>(coc-rename)
autocmd CursorHold * silent call CocActionAsync('highlight')

"let g:my_coc_file_types = ['c', 'cpp', 'h', 'asm', 'hpp', 'vim', 'sh', 'py']
let g:my_coc_file_types = ['py', 'js', 'vim']

function! s:disable_coc_for_type()
      if index(g:my_coc_file_types, &filetype) == -1
            let b:coc_enabled = 0
      endif
endfunction

augroup CocGroup
      autocmd!
      autocmd BufNew,BufEnter * call s:disable_coc_for_type()
augroup end
