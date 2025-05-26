#!/usr/bin/env bun

/*
Forwards all arguments to coconut.py
*/

let command = [ "coconut.py", ...Bun.argv.slice(2) ]

command = command.map(arg => arg === "--list" ? "list" : arg)

const proc = Bun.spawnSync(command, {
  stdout : "inherit",
})
