return {
  "gbrlsnchs/winpick.nvim",
  lazy = true,
  keys = {
    {
      "<leader><leader>w",
      function()
        require("winpick").select()
      end,
      desc = "Pick window",
      mode = { "n" },
    },
  },
  opts = {},
}
