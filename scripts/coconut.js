#!/usr/bin/env bun
import { $ } from "bun";
import PocketBase from "pocketbase";

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
    sort: "-created",
  });
  // add imageUrl to each record
  for (const record of records) {
    record.imageUrl = pb.files.getUrl(record, record.image);
  }
  console.log(JSON.stringify(records, null, 2));
  process.exit(0);
}

const hostname = (await $`hostname`.text()).trim();
const { uri, sec, path } = JSON.parse(
  await $`fish -c 'recent_played_vlc.py --json'`.text(),
);

const seekTo = sec > 0 ? `00:00:${sec}` : "30%";

// create thumbnail file
const thumbnailPath = `/tmp/${crypto.randomUUID()}.jpg`;
await $`ffmpegthumbnailer -t${seekTo} -s256 -i ${path} -o ${thumbnailPath}`;
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
