return {
  "gbprod/yanky.nvim",
  lazy = false,
  dependencies = {
    { "kkharji/sqlite.lua" },
  },
  opts = {
    highlight = {
      timer = 250,
    },
  },
  keys = {
    { "p", "<Plug>(YankyPutAfter)", mode = { "n", "x" } },
    { "P", "<Plug>(YankyPutBefore)", mode = { "n", "x" } },
    { "<c-n>", "<Plug>(YankyCycleForward)" },
    { "<c-p>", "<Plug>(YankyCycleBackward)" },
    { "<leader>p", "a<space><esc><Plug>(YankyPutAfter)" },
  },
  config = function(_, opts)
    require("yanky").setup(opts)
  end,
}
