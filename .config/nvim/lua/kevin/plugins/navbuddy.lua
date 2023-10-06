return {
  "neovim/nvim-lspconfig",
  dependencies = {
    {
      "SmiteshP/nvim-navbuddy",
      dependencies = {
        "SmiteshP/nvim-navic",
        "MunifTanjim/nui.nvim",
      },
      opts = {
        -- mappings = {
        --   ["<esc>"] = require("nvim-navbuddy.actions").close(), -- Close and cursor to original location
        --   ["q"] = require("nvim-navbuddy.actions").close(),
        --
        --   ["k"] = require("nvim-navbuddy.actions").next_sibling(), -- down
        --   ["h"] = require("nvim-navbuddy.actions").previous_sibling(), -- up
        --
        --   ["j"] = require("nvim-navbuddy.actions").parent(), -- Move to left panel
        --   --       ["l"] = require("nvim-navbuddy.actions").child
        --   --
        --   --       (), -- Move to right panel
        -- },
        lsp = { auto_attach = true },
      },
    },
  },
  -- your lsp config or other stuff
}
