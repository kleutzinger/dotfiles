#!/usr/bin/env bun

// this file only kind of sort of works on linux, don't use

var currentOS = require("current-os");
const os = require("os");
const tmp = require("tmp");
import { $ } from "bun";
const mvdir = require("mvdir");

function iterPicker(iterable, displayFunc) {
  // print all elements in the iterable, have user provide index, and return the
  // element at that index
  const arr = [...iterable];
  if (!displayFunc) {
    displayFunc = (item) => item;
  }
  for (let i = 0; i < arr.length; i++) {
    console.log(i, displayFunc(arr[i]));
  }
  const index = parseInt(prompt("choose index: "));
  return arr[index];
}

// use json api to get all releases
const response = await fetch(
  `https://api.github.com/repos/TriliumNext/Notes/releases`,
);

const data = (await response.json()).slice(0, 10);
const release = iterPicker(data, (r) => `${r.tag_name} \t\t ${r.published_at}`);
const tagName = release.tag_name;
console.dir(release.name);

let installDir;
let asset;
if (currentOS.isLinux) {
  `
  cd $(mktemp --directory --suffix=trilium-update)
  wget --verbose $DL_URL
  unzip *.zip
  rm *.zip
  rm -rf ~/$INSTALL_DIR
  mv * ~/trilium-next
  # ensure symlink to ~/.local/bin/trilium
  rm -f ~/.local/bin/trilium
  ln -sf ~/$INSTALL_DIR/trilium ~/.local/bin/trilium
  `;

  // get asset with name of form TriliumNextNotes-v0.92.7-linux-x64.zip
  const zipname = `TriliumNextNotes-${tagName}-linux-x64.zip`;
  asset = release.assets.find((a) => {
    return a.name === zipname;
  });

  installDir = os.homedir() + "/trilium-next";
  const tmpobj = tmp.dirSync();
  console.log("Dir: ", tmpobj.name);
  // Manual cleanup
  const DL_URL = asset.browser_download_url;
  const DL_FILE = DL_URL.split("/").pop();
  const path = tmpobj.name + "/" + DL_FILE;
  Bun.spawnSync({ cmd: ["wget", "--verbose", DL_URL], cwd: tmpobj.name });
  Bun.spawnSync({ cmd: ["unzip", path], cwd: tmpobj.name });
  Bun.spawnSync({ cmd: ['rm', '*.zip'], cwd: tmpobj.name });
  await $`rm -rf ${installDir}`;
  Bun.spawnSync({ cmd: ["mv", "*", installDir], cwd: tmpobj.name });
  console.log("done");
}
