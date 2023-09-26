return {
  "folke/which-key.nvim",
  event = "VeryLazy",
  init = function()
    vim.o.timeout = true
    vim.o.timeoutlen = 500
  end,
  opts = {
    -- your configuration comes here
    -- or leave it empty to use the default settings
    -- refer to the configuration section below
    triggers_blacklist = {
      -- ignore h when in insert mode (i use hk to exit insert mode)
      i = { "h", "k" },
    },
  },
}
