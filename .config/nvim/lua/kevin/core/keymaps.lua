-- set leader key to space
vim.g.mapleader = ","

local keymap = vim.keymap -- for conciseness

---------------------
-- General Keymaps -------------------

-- use backslash to go back when using f/t
vim.api.nvim_set_keymap("n", "\\", ",", { noremap = true })

-- use hk to exit insert mode
keymap.set("i", "hk", "<ESC>", { desc = "Exit insert mode with hk" })

keymap.set("n", "<leader>nh", ":nohl<CR>", { desc = "Clear search highlights" })

keymap.set("n", "<leader>lg", ":LazyGit<CR>", { desc = "Open LazyGit" })

-- delete single character without copying into register
keymap.set("n", "x", '"_x')

-- window management
keymap.set("n", "<leader>sv", "<C-w>v", { desc = "Split window vertically" }) -- split window vertically
keymap.set("n", "<leader>sh", "<C-w>s", { desc = "Split window horizontally" }) -- split window horizontally
keymap.set("n", "<leader>se", "<C-w>=", { desc = "Make splits equal size" }) -- make split windows equal width & height
keymap.set("n", "<leader>sx", "<cmd>close<CR>", { desc = "Close current split" }) -- close current split window

keymap.set("n", "<leader>to", "<cmd>tabnew<CR>", { desc = "Open new tab" }) -- open new tab
keymap.set("n", "<leader>tx", "<cmd>tabclose<CR>", { desc = "Close current tab" }) -- close current tab
keymap.set("n", "<leader>tn", "<cmd>tabn<CR>", { desc = "Go to next tab" }) --  go to next tab
keymap.set("n", "<leader>tp", "<cmd>tabp<CR>", { desc = "Go to previous tab" }) --  go to previous tab
keymap.set("n", "<leader>tf", "<cmd>tabnew %<CR>", { desc = "Open current buffer in new tab" }) --  move current buffer to new tab

-- map f to sneak plugin in all modes
keymap.set("n", "f", "<Plug>Sneak_f", { silent = true })
keymap.set("o", "f", "<Plug>Sneak_f", { silent = true })
keymap.set("x", "f", "<Plug>Sneak_f", { silent = true })

-- same for F and t and T
keymap.set("n", "F", "<Plug>Sneak_F", { silent = true })
keymap.set("o", "F", "<Plug>Sneak_F", { silent = true })
keymap.set("x", "F", "<Plug>Sneak_F", { silent = true })

keymap.set("n", "t", "<Plug>Sneak_t", { silent = true })
keymap.set("o", "t", "<Plug>Sneak_t", { silent = true })
keymap.set("x", "t", "<Plug>Sneak_t", { silent = true })

keymap.set("n", "T", "<Plug>Sneak_T", { silent = true })
keymap.set("o", "T", "<Plug>Sneak_T", { silent = true })
keymap.set("x", "T", "<Plug>Sneak_T", { silent = true })

keymap.set("n", "<esc><esc><esc>", "<cmd>qa<CR>", { desc = "Quit neovim" })

keymap.set("i", "<C-BS>", "<C-W>", { desc = "Delete word backwards in insert mode" })

-- leader w to save file
keymap.set("n", "<leader>w", "<cmd>w<CR>", { desc = "Save file" })

keymap.set("v", "<leader>r", '"hy:%s/<C-r>h//g<left><left>', { desc = "Replace all instances of highlighted words" })

local def_opts = { silent = false, noremap = true }
vim.keymap.set({ "n", "v" }, "<CR>", ":<up>", def_opts)
