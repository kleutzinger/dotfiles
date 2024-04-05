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

const hostname = (await $`hostname`.text()).trim();
const filepath = (await $`fish -c 'recent_played_vlc'`.text()).trim();

// convert file:///path/to/file to /path/to/file and decode URI
const path = decodeURI(filepath.replace("file://", ""));
// const vidFilename = path.split("/").pop();

// create thumbnail file
const thumbnailPath = `/tmp/${crypto.randomUUID()}.jpg`;
await $`ffmpegthumbnailer -s256 -i ${path} -o ${thumbnailPath}`;

`
yt-dlp --write-thumbnail -P thumbnail:/tmp/thumb --skip-download 'https://www.youtube.com/watch?v=9DUfx2g_R8U'
writes thumbnail to /tmp/thumb


const records = await pb.collection("coconuts").getFullList({
  sort: "-created",
});
`;

const toUpload = {
  path,
  hostname,
  image: Bun.file(thumbnailPath, { type: "image/jpeg" }),
};

console.log(toUpload);
console.log("upload? ctrl+c to cancel");
// count down form 5 4 3 2 1 seconds all on same line
for (let i = 5; i > 0; i--) {
  process.stdout.write(`${i} `);
  await new Promise((r) => setTimeout(r, 1000));
}
console.log("uploading...");

const out = await pb.collection("coconuts").create(toUpload);
console.log(out);
