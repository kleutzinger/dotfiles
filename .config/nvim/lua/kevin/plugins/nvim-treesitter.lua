return {
  {
    "nvim-treesitter/nvim-treesitter",
    branch = "main",
    build = ":TSUpdate",
    event = { "BufReadPre", "BufNewFile" },
    -- main branch dropped `nvim-treesitter.configs`: highlight/indent/install
    -- are wired up by hand here instead of through a `setup({ ... })` table
    init = function()
      local function highlight(bufnr, lang)
        if not vim.treesitter.language.add(lang) then
          return vim.notify(
            string.format("Treesitter cannot load parser for language: %s", lang),
            vim.log.levels.WARN,
            { title = "Treesitter" }
          )
        end
        vim.treesitter.start(bufnr)
      end

      vim.api.nvim_create_autocmd("FileType", {
        callback = function(args)
          local ft = vim.bo[args.buf].filetype
          local bt = vim.bo[args.buf].buftype

          if bt ~= "" then
            return
          end

          local ok, treesitter = pcall(require, "nvim-treesitter")
          if not ok then
            return
          end

          -- folds
          if ft == "javascriptreact" or ft == "typescriptreact" then
            vim.opt_local.foldmethod = "indent"
          else
            vim.opt_local.foldmethod = "expr"
            vim.opt_local.foldexpr = "v:lua.vim.treesitter.foldexpr()"
          end
          vim.schedule(function()
            if vim.fn.mode() ~= "t" then
              vim.cmd("silent! normal! zx")
            end
          end)

          -- indent
          if not vim.tbl_contains({ "python", "html", "yaml", "markdown" }, ft) then
            vim.bo[args.buf].indentexpr = "v:lua.require('nvim-treesitter').indentexpr()"
          end

          -- install + highlight
          if not vim.treesitter.language.get_lang(ft) then
            return
          end

          if vim.list_contains(treesitter.get_installed(), ft) then
            highlight(args.buf, ft)
          elseif vim.list_contains(treesitter.get_available(), ft) then
            treesitter.install(ft):await(function()
              highlight(args.buf, ft)
            end)
          end
        end,
      })
    end,
    opts = {
      -- ensure these language parsers are installed
      install = {
        "json",
        "javascript",
        "typescript",
        "python",
        "tsx",
        "yaml",
        "html",
        "css",
        "prisma",
        "markdown",
        "markdown_inline",
        "svelte",
        "graphql",
        "bash",
        "lua",
        "vim",
        "dockerfile",
        "gitignore",
      },
    },
    config = function(_, opts)
      require("nvim-treesitter").setup()
      require("nvim-treesitter").install(opts.install)
    end,
  },
}
