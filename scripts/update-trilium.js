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
  const index = parseInt(prompt("choose index:") || 0);
  return arr[index];
}

// use json api to get all releases
const response = await fetch(
  `https://api.github.com/repos/TriliumNext/Notes/releases`
);

const data = (await response.json()).slice(0, 5);
const release = iterPicker(data, (r) => `${r.tag_name} \t\t ${r.published_at}`);
const tagName = release.tag_name;
console.dir(release.name);

let installDir;
let asset;
if (currentOS.isOSX) {
  const assetName = `TriliumNextNotes-${tagName}-macos-arm64.dmg`;
  asset = release.assets.find((a) => {
    return a.name === assetName;
  });
  if (!asset) {
    console.error("no asset found " + assetName);
    process.exit(1);
  }
  const DL_URL = asset.browser_download_url;
  await Bun.spawnSync({
    cmd: ["curl", "-L", "-o", assetName, DL_URL],
    cwd: os.homedir() + "/Desktop",
  });
  const outputPath = os.homedir() + "/Desktop/" + assetName;
  await Bun.spawnSync({
    cmd: ["open", outputPath],
    cwd: os.homedir() + "/Desktop",
  });
}

if (currentOS.isWindows) {
  // download the latest windows release to Desktop
  /*
  cd C:\Users\kevin\Documents\GitHub\dotfiles\ ; git pull ; bun run scripts\update-trilium.js
  */
  const assetName = `TriliumNextNotes-${tagName}-windows-x64.exe`;
  asset = release.assets.find((a) => {
    return a.name === assetName;
  });
  const DL_URL = asset.browser_download_url;
  Bun.spawnSync({
    cmd: ["curl", "-L", "-o", assetName, DL_URL],
    cwd: os.homedir() + "/Desktop",
  });
  // open the new executable
  // Bun.spawnSync({ cmd: ["./" + assetName], cwd: os.homedir() + "/Desktop" });
  console.log("done! please double click the file on your desktop to install.");
}
if (currentOS.isLinux) {
  // get asset with name of form TriliumNextNotes-v0.92.7-linux-x64.zip
  const assetName = `TriliumNextNotes-${tagName}-linux-x64.zip`;
  asset = release.assets.find((a) => {
    return a.name === assetName;
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
  Bun.spawnSync({ cmd: ["rm", "*.zip"], cwd: tmpobj.name });
  await $`rm -rf ${installDir}`;
  Bun.spawnSync({ cmd: ["mv", "*", installDir], cwd: tmpobj.name }); // this is broken
  console.log("done");
}
