#!/usr/bin/env bun
import { $ } from "bun";
import PocketBase from "pocketbase";
import PQueue from "p-queue";

var Cache = require("sync-disk-cache");
var cache = new Cache("my-cache");
const os = require("os");
const fs = require("fs");

const POCKETBASE_URL = process.env.POCKETBASE_URL;
const POCKETBASE_USERNAME = process.env.POCKETBASE_USERNAME;
const POCKETBASE_PASSWORD = process.env.POCKETBASE_PASSWORD;

const pb = new PocketBase(POCKETBASE_URL);

await pb
  .collection("users")
  .authWithPassword(POCKETBASE_USERNAME, POCKETBASE_PASSWORD);

function relativeTime(date) {
  // e.g. 1 year, 2 months, 3 days, 4 hours ago
  const now = new Date();
  const elapsed = now - date;

  const units = [
    { label: "year", milliseconds: 1000 * 60 * 60 * 24 * 365 },
    { label: "month", milliseconds: 1000 * 60 * 60 * 24 * 30 },
    { label: "day", milliseconds: 1000 * 60 * 60 * 24 },
    { label: "hour", milliseconds: 1000 * 60 * 60 },
  ];

  const result = [];

  let remainingTime = elapsed;

  for (let i = 0; i < units.length; i++) {
    const unitTime = Math.floor(remainingTime / units[i].milliseconds);
    if (unitTime > 0) {
      result.push(`${unitTime} ${units[i].label}${unitTime > 1 ? "s" : ""}`);
      remainingTime -= unitTime * units[i].milliseconds;
    }
  }

  if (result.length === 0) {
    return "0 hours ago";
  }

  return result.join(", ") + " ago";
}

function hoursAgo(date) {
  const now = new Date();
  const elapsed = now - date; // difference in milliseconds
  const hours = Math.floor(elapsed / (1000 * 60 * 60)); // convert milliseconds to hours
  return `${hours}hr`;
}

// these are the paths that have the  the same stuff on my machines
const EQUIV_PATH_ARR = [
  os.homedir(),
  "/home/kevin",
  "/run/media/kevin/orico",
  "/run/media/kevin/tosh",
].filter(fs.existsSync); // only keep the directories that exist

// check if list in argv
if (process.argv.includes("list") || process.argv.includes("--list")) {
  const records = await pb.collection("coconuts").getFullList({
    sort: "created",
  });
  // add imageUrl to each record
  for (let record of records) {
    const { updated, id } = record;
    const key = `${id}-${updated}-imageUrl`;
    if (cache.has(key)) {
      record.imageUrl = cache.get(key).value;
    } else {
      record.imageUrl = pb.files.getURL(record, record.image);
      cache.set(key, record.imageUrl);
    }
    const createdDateTime = new Date(record.created);
    record.timeAgo = `(${hoursAgo(createdDateTime)}) ${relativeTime(createdDateTime)}`;
  }
  const resolved_records = await concurrentPathFinder(records);

  console.log(JSON.stringify(resolved_records, null, 2));
  process.exit(0);
}

async function concurrentPathFinder(records) {
  const queue = new PQueue({ concurrency: 20 }); // Adjust concurrency as needed
  const pathMap = new Map(); // Map to store resolved paths
  const uniquePaths = new Set(records.map((record) => record.path)); // Deduplicate paths

  // Helper function to resolve a path
  async function resolvePath(originalPath) {
    if (pathMap.has(originalPath)) {
      return pathMap.get(originalPath);
    }

    if (fs.existsSync(originalPath)) {
      pathMap.set(originalPath, { path: originalPath, exists: true });
      return pathMap.get(originalPath);
    }

    const presentPrefix = EQUIV_PATH_ARR.find((x) =>
      originalPath.startsWith(x),
    );
    if (presentPrefix) {
      for (const equivalentPath of EQUIV_PATH_ARR) {
        const newPath = originalPath.replace(presentPrefix, equivalentPath);
        if (fs.existsSync(newPath)) {
          pathMap.set(originalPath, { path: newPath, exists: true });
          return pathMap.get(originalPath);
        }
      }
    }

    pathMap.set(originalPath, { path: originalPath, exists: false });
    return pathMap.get(originalPath);
  }

  // Queue tasks for resolving paths
  await Promise.all(
    Array.from(uniquePaths).map((path) => queue.add(() => resolvePath(path))),
  );

  // Update records with resolved paths
  return records.map((record) => {
    const resolved = pathMap.get(record.path);
    return { ...record, ...resolved };
  });
}

function hhmmssToSec(str) {
  // string can be in format hh:mm:ss or mm:ss or ss
  // replace . with :
  str = str.replace(".", ":");
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
