return {
  "nvim-treesitter/nvim-treesitter-textobjects",
  branch = "main",
  event = { "BufReadPost", "BufNewFile" },
  dependencies = {
    "nvim-treesitter/nvim-treesitter",
  },
  -- main branch dropped `nvim-treesitter.configs`: select/swap keymaps are
  -- bound by hand to the textobjects submodules instead of a keymaps table
  config = function()
    require("nvim-treesitter-textobjects").setup({
      select = {
        -- Automatically jump forward to textobj, similar to targets.vim
        lookahead = true,
        include_surrounding_whitespace = true,
      },
    })

    local select = require("nvim-treesitter-textobjects.select")

    local function select_textobject(query)
      return function()
        select.select_textobject(query, "textobjects")
      end
    end

    -- You can use the capture groups defined in textobjects.scm
    vim.keymap.set({ "x", "o" }, "a=", select_textobject("@assignment.outer"), { desc = "Select outer part of an assignment region" })
    vim.keymap.set({ "x", "o" }, "i=", select_textobject("@assignment.inner"), { desc = "Select inner part of an assignment region" })

    vim.keymap.set({ "x", "o" }, "a:", select_textobject("@parameter.outer"), { desc = "Select outer part of a parameter/field region" })
    vim.keymap.set({ "x", "o" }, "i:", select_textobject("@parameter.inner"), { desc = "Select inner part of a parameter/field region" })

    vim.keymap.set({ "x", "o" }, "ai", select_textobject("@conditional.outer"), { desc = "Select outer part of a conditional region" })
    vim.keymap.set({ "x", "o" }, "ii", select_textobject("@conditional.inner"), { desc = "Select inner part of a conditional region" })

    vim.keymap.set({ "x", "o" }, "al", select_textobject("@loop.outer"), { desc = "Select outer part of a loop region" })
    vim.keymap.set({ "x", "o" }, "il", select_textobject("@loop.inner"), { desc = "Select inner part of a loop region" })

    -- overrides default text object block of parenthesis to parenthesis
    vim.keymap.set({ "x", "o" }, "ab", select_textobject("@block.outer"), { desc = "Select outer part of a block region" })
    vim.keymap.set({ "x", "o" }, "ib", select_textobject("@block.inner"), { desc = "Select inner part of a block region" })

    vim.keymap.set({ "x", "o" }, "af", select_textobject("@function.outer"), { desc = "Select outer part of a function region" })
    vim.keymap.set({ "x", "o" }, "if", select_textobject("@function.inner"), { desc = "Select inner part of a function region" })

    vim.keymap.set({ "x", "o" }, "ac", select_textobject("@class.outer"), { desc = "Select outer part of a class region" })
    vim.keymap.set({ "x", "o" }, "ic", select_textobject("@class.inner"), { desc = "Select inner part of a class region" })

    local swap = require("nvim-treesitter-textobjects.swap")

    -- swap object under cursor with next
    vim.keymap.set("n", "<leader>on", function()
      swap.swap_next("@parameter.inner")
    end, { desc = "Swap parameter with next" })

    -- swap object under cursor with previous
    vim.keymap.set("n", "<leader>op", function()
      swap.swap_previous("@parameter.inner")
    end, { desc = "Swap parameter with previous" })
  end,
}
