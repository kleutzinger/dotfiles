return {
  "dundalek/lazy-lsp.nvim",
  dependencies = { "neovim/nvim-lspconfig" },
  config = function()
    require("lazy-lsp").setup {
      excluded_servers = {
        "pylyzer", -- sometimes maxes out CPU?
      },
      use_vim_lsp_config = true,
    }
  end
}
