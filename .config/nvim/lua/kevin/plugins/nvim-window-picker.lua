return {
  "gbrlsnchs/winpick.nvim",
  lazy = true,
  keys = {
    {
      "<leader>ww",
      function()
        require("winpick").select()
      end,
      desc = "Pick window",
      mode = { "n" },
    },
  },
  opts = {},
}
