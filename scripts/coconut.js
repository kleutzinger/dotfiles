#!/usr/bin/env bun
import { $ } from "bun";
import PocketBase from "pocketbase";

import TimeAgo from "javascript-time-ago";
// English.
import en from "javascript-time-ago/locale/en";
TimeAgo.addDefaultLocale(en);
// Create formatter (English).
const timeAgo = new TimeAgo("en-US");

var Cache = require("sync-disk-cache");
var cache = new Cache("my-cache");

const POCKETBASE_URL = process.env.POCKETBASE_URL;
const POCKETBASE_USERNAME = process.env.POCKETBASE_USERNAME;
const POCKETBASE_PASSWORD = process.env.POCKETBASE_PASSWORD;

const pb = new PocketBase(POCKETBASE_URL);

await pb
  .collection("users")
  .authWithPassword(POCKETBASE_USERNAME, POCKETBASE_PASSWORD);

// check if list in argv
if (process.argv.includes("list") || process.argv.includes("--list")) {
  const records = await pb.collection("coconuts").getFullList({
    sort: "created",
  });
  // add imageUrl to each record
  for (const record of records) {
    const { updated, id } = record;
    const key = `${id}-${updated}-imageUrl`;
    if (cache.has(key)) {
      record.imageUrl = cache.get(key).value;
    } else {
      record.imageUrl = pb.files.getUrl(record, record.image);
      cache.set(key, record.imageUrl);
    }
    record.timeAgo = timeAgo.format(new Date(record.created), "twitter");
  }

  console.log(JSON.stringify(records, null, 2));
  process.exit(0);
}

function hhmmssToSec(str) {
  // string can be in format hh:mm:ss or mm:ss or ss
  const parts = str.split(":").map((x) => parseInt(x));
  return parts.reduce((acc, x) => acc * 60 + x);
}

const hostname = (await $`hostname`.text()).trim();
let { uri, sec, path } = JSON.parse(
  await $`fish -c 'recent_played_vlc.py --json'`.text(),
);

const secIndex = process.argv.indexOf("--sec");

if (secIndex > -1) {
  sec = hhmmssToSec(process.argv[secIndex + 1]);
}

if (sec <= 0 && !secIndex) {
  const prompt = "What sec?\n";
  console.log(uri);
  process.stdout.write(prompt);
  for await (const line of console) {
    sec = hhmmssToSec(line.trim());
    break;
  }
}

const seekTo = sec > 0 ? `00:00:${sec}` : "30%";

// create thumbnail file
const thumbnailPath = `/tmp/${crypto.randomUUID()}.jpg`;
await $`ffmpegthumbnailer -t${seekTo} -s512 -i ${path} -o ${thumbnailPath}`;
try {
  await $`kitten icat --align left --scale-up ${thumbnailPath}`;
} catch (e) {
  console.error(e);
}

`
yt-dlp --write-thumbnail -P thumbnail:/tmp/thumb --skip-download 'https://www.youtube.com/watch?v=9DUfx2g_R8U'
writes thumbnail to /tmp/thumb

`;

const toUpload = {
  path,
  hostname,
  sec: sec,
  image: Bun.file(thumbnailPath, { type: "image/jpeg" }),
};

// check if path ends with jpg, jpeg, png, gif
// if it's an image, just upload the image directly
let ext = path.split(".").pop();
if (ext == "jpg") ext = "jpeg";
if (["jpg", "jpeg", "png", "gif"].includes(ext)) {
  toUpload.image = Bun.file(path, { type: `image/${ext}` });
}

console.log(toUpload);
console.log("upload? ctrl+c to cancel");
// count down form 5 4 3 2 1 seconds all on same line
for (let i = 5; i > 0; i--) {
  process.stdout.write(`${i} `);
  await new Promise((r) => setTimeout(r, 1000));
}

await $`clear`;
console.log("uploading...");

const out = await pb.collection("coconuts").create(toUpload);
console.log(out);
