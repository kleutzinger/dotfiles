return {
  "windwp/nvim-ts-autotag",
  event = { "BufReadPre", "BufNewFile" },
  dependencies = {
    "nvim-treesitter/nvim-treesitter",
  },
  -- setting this up via nvim-treesitter.configs is deprecated; it now needs
  -- its own standalone setup call
  config = function()
    require("nvim-ts-autotag").setup()
  end,
}
