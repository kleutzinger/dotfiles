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

    local multiopen = function(prompt_bufnr)
      local picker = require('telescope.actions.state').get_current_picker(prompt_bufnr)
      local multi = picker:get_multi_selection()

      if vim.tbl_isempty(multi) then
        require('telescope.actions').select_default(prompt_bufnr)
        return
      end

      require('telescope.actions').close(prompt_bufnr)
      for _, entry in pairs(multi) do
        local filename = entry.filename or entry.value
        local lnum = entry.lnum or 1
        local lcol = entry.col or 1
        if filename then
          vim.cmd(string.format("tabnew +%d %s", lnum, filename))
          vim.cmd(string.format("normal! %dG%d|", lnum, lcol))
        end
      end
    end

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
      pickers = {
        live_grep = {
          mappings = {
            i = {
              ["<CR>"] = multiopen,
            },
            n = {
              ["<CR>"] = multiopen,
            },
          },
        },
      },
    })

    telescope.load_extension("fzf")
    telescope.load_extension("persisted")

    -- set keymaps
    local keymap = vim.keymap -- for conciseness

    keymap.set("n", "<leader><leader><leader>", "<cmd>Telescope<cr>", { desc = "Open Telescope" })
    keymap.set("n", "<leader><leader>f", "<cmd>Telescope find_files<cr>", { desc = "files in cwd" })
    keymap.set("n", "<leader>ff", "<cmd>Telescope find_files<cr>", { desc = "files in cwd" })
    keymap.set("n", "<leader><leader>r", "<cmd>Telescope oldfiles<cr>", { desc = "recent files" })
    keymap.set("n", "<leader><leader>s", "<cmd>Telescope live_grep<cr>", { desc = "string in cwd" })
    keymap.set("n", "<leader><leader>c", "<cmd>Telescope grep_string<cr>", { desc = "string under cursor in cwd" })
    keymap.set("n", "<leader><leader>b", "<cmd>Telescope buffers<cr>", { desc = "buffers" })
    keymap.set("n", "<leader><leader>m", "<cmd>Telescope marks<cr>", { desc = "marks" })
    keymap.set("n", "<leader><leader>y", "<cmd>Telescope registers<cr>", { desc = "registers" })
    keymap.set("n", "<leader><leader>j", "<cmd>Telescope jumplist<cr>", { desc = "jumplist" })
    keymap.set("n", "<leader><leader>p", "<cmd>Telescope persisted<cr>", { desc = "persisted sessions" })
  end,
}
