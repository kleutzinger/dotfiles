return {
  "sbdchd/neoformat",
  config = function()
    -- Set ruff as the formatter for python
    vim.g.neoformat_enabled_python = { "ruff" }
  end
}
