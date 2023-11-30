return os.getenv("TERM") ~= "xterm-kitty"
    and {
      {
        -- not xterm, meaning it's likely a GUI (aka my notes)
        "robertmeta/nofrils",
        priority = 1000,
        config = function()
          vim.cmd([[colorscheme nofrils-dark]])
        end,
      },
    }
  or {
    {
      -- normal xterm stuff
      "robertmeta/nofrils",
      priority = 1000, -- make sure to load this before all the other start plugins
      config = function()
        -- load the colorscheme here
        vim.cmd([[colorscheme nofrils-dark]])
      end,
    },
  }
