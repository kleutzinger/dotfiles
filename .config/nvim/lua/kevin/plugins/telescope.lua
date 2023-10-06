return {
  "nvim-telescope/telescope.nvim",
  branch = "0.1.x",
  dependencies = {
    "nvim-lua/plenary.nvim",
    { "nvim-telescope/telescope-fzf-native.nvim", build = "make" },
    "nvim-tree/nvim-web-devicons",
  },
  config = function()
    local telescope = require("telescope")
    local actions = require("telescope.actions")

    telescope.setup({
      defaults = {
        path_display = { "truncate " },
        mappings = {
          i = {
            ["<C-h>"] = actions.move_selection_previous, -- move to prev result
            ["<C-k>"] = actions.move_selection_next, -- move to next result
            ["<C-q>"] = actions.send_selected_to_qflist + actions.open_qflist,
          },
        },
      },
    })

    telescope.load_extension("fzf")

    -- set keymaps
    local keymap = vim.keymap -- for conciseness

    keymap.set("n", "<leader><leader><leader>", "<cmd>Telescope<cr>", { desc = "Open Telescope" })
    keymap.set("n", "<leader><leader>f", "<cmd>Telescope find_files<cr>", { desc = "files in cwd" })
    keymap.set("n", "<leader>ff", "<cmd>echo ',,f THIS KEYMAP HAS CHANED'<cr>", { desc = "keymap changed" })
    keymap.set("n", "<leader><leader>r", "<cmd>Telescope oldfiles<cr>", { desc = "recent files" })
    keymap.set("n", "<leader><leader>s", "<cmd>Telescope live_grep<cr>", { desc = "string in cwd" })
    keymap.set("n", "<leader><leader>c", "<cmd>Telescope grep_string<cr>", { desc = "string under cursor in cwd" })
    keymap.set("n", "<leader><leader>b", "<cmd>Telescope buffers<cr>", { desc = "buffers" })
    keymap.set("n", "<leader><leader>m", "<cmd>Telescope marks<cr>", { desc = "marks" })
    keymap.set("n", "<leader><leader>y", "<cmd>Telescope registers<cr>", { desc = "registers" })
  end,
}
