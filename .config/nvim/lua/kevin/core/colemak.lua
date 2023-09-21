-- NORMAL MODE --

-- Remap h, j, and k for normal mode
vim.api.nvim_set_keymap("n", "h", "k", { noremap = true })
vim.api.nvim_set_keymap("n", "j", "h", { noremap = true })
vim.api.nvim_set_keymap("n", "k", "j", { noremap = true })

-- Remap gh, gj, and gk for normal mode
vim.api.nvim_set_keymap("n", "gh", "gk", { noremap = true })
vim.api.nvim_set_keymap("n", "gj", "gh", { noremap = true })
vim.api.nvim_set_keymap("n", "gk", "gj", { noremap = true })

-- Remap zh, zj, and zk for normal mode
vim.api.nvim_set_keymap("n", "zh", "zk", { noremap = true })
vim.api.nvim_set_keymap("n", "zj", "zh", { noremap = true })
vim.api.nvim_set_keymap("n", "zk", "zj", { noremap = true })

-- Remap z<Space>, z<S-Space>, and z<BS> for normal mode
vim.api.nvim_set_keymap("n", "z<Space>", "zl", { noremap = true })
vim.api.nvim_set_keymap("n", "z<S-Space>", "zL", { noremap = true })
vim.api.nvim_set_keymap("n", "z<BS>", "zh", { noremap = true })

-- Remap z<S-BS> for normal mode
vim.api.nvim_set_keymap("n", "z<S-BS>", "zH", { noremap = true })

-- Remap <C-w>h, <C-w>H, <C-w>j, <C-w>J, <C-w>k, <C-w>K, <C-w><Space>, <C-w><S-Space>, and <C-w><S-BS> for normal mode
vim.api.nvim_set_keymap("n", "<C-w>h", "<C-w>k", { noremap = true })
vim.api.nvim_set_keymap("n", "<C-w>H", "<C-w>K", { noremap = true })
vim.api.nvim_set_keymap("n", "<C-w>j", "<C-w>h", { noremap = true })
vim.api.nvim_set_keymap("n", "<C-w>J", "<C-w>H", { noremap = true })
vim.api.nvim_set_keymap("n", "<C-w>k", "<C-w>j", { noremap = true })
vim.api.nvim_set_keymap("n", "<C-w>K", "<C-w>J", { noremap = true })
vim.api.nvim_set_keymap("n", "<C-w><Space>", "<C-w>l", { noremap = true })
vim.api.nvim_set_keymap("n", "<C-w><S-Space>", "<C-w>L", { noremap = true })
vim.api.nvim_set_keymap("n", "<C-w><S-BS>", "<C-w>H", { noremap = true })

-- VISUAL MODE --

-- Remap h, j, and k for visual mode
vim.api.nvim_set_keymap("x", "h", "k", { noremap = true })
vim.api.nvim_set_keymap("x", "j", "h", { noremap = true })
vim.api.nvim_set_keymap("x", "k", "j", { noremap = true })

-- Remap gh, gj, and gk for visual mode
vim.api.nvim_set_keymap("x", "gh", "gk", { noremap = true })
vim.api.nvim_set_keymap("x", "gj", "gh", { noremap = true })
vim.api.nvim_set_keymap("x", "gk", "gj", { noremap = true })

-- Remap zh, zj, and zk for visual mode
vim.api.nvim_set_keymap("x", "zh", "zk", { noremap = true })
vim.api.nvim_set_keymap("x", "zj", "zh", { noremap = true })
vim.api.nvim_set_keymap("x", "zk", "zj", { noremap = true })

-- Remap z<Space>, z<S-Space>, and z<BS> for visual mode
vim.api.nvim_set_keymap("x", "z<Space>", "zl", { noremap = true })
vim.api.nvim_set_keymap("x", "z<S-Space>", "zL", { noremap = true })
vim.api.nvim_set_keymap("x", "z<BS>", "zh", { noremap = true })

-- Remap z<S-BS> for visual mode
vim.api.nvim_set_keymap("x", "z<S-BS>", "zH", { noremap = true })

-- Remap <C-w>h, <C-w>H, <C-w>j, <C-w>J, <C-w>k, <C-w>K, <C-w><Space>, <C-w><S-Space>, and <C-w><S-BS> for visual mode
vim.api.nvim_set_keymap("x", "<C-w>h", "<C-w>k", { noremap = true })
vim.api.nvim_set_keymap("x", "<C-w>H", "<C-w>K", { noremap = true })
vim.api.nvim_set_keymap("x", "<C-w>j", "<C-w>h", { noremap = true })
vim.api.nvim_set_keymap("x", "<C-w>J", "<C-w>H", { noremap = true })
vim.api.nvim_set_keymap("x", "<C-w>k", "<C-w>j", { noremap = true })
vim.api.nvim_set_keymap("x", "<C-w>K", "<C-w>J", { noremap = true })
vim.api.nvim_set_keymap("x", "<C-w><Space>", "<C-w>l", { noremap = true })
vim.api.nvim_set_keymap("x", "<C-w><S-Space>", "<C-w>L", { noremap = true })
vim.api.nvim_set_keymap("x", "<C-w><S-BS>", "<C-w>H", { noremap = true })
