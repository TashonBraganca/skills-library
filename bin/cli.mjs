#!/usr/bin/env node
// tashon-skills - install the skills library into every agent tool on this machine.
//
//   npx tashon-skills            clone or update, then install
//   npx tashon-skills --dry-run  show what would change
//   npx tashon-skills --where    print the library path and exit
//
// Idempotent. Safe to run on a fresh machine or an existing one.

import { execFileSync, spawnSync } from "node:child_process";
import { existsSync, mkdirSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

const REPO = process.env.TASHON_SKILLS_REPO || "https://github.com/tashonbraganca/skills-library.git";
const LIB = process.env.TASHON_SKILLS_HOME || join(homedir(), ".skills-library");
const args = process.argv.slice(2);
const has = (f) => args.includes(f);

const run = (cmd, cmdArgs, opts = {}) =>
  spawnSync(cmd, cmdArgs, { stdio: "inherit", ...opts });

if (has("--where")) {
  console.log(LIB);
  process.exit(0);
}

function haveGit() {
  try {
    execFileSync("git", ["--version"], { stdio: "ignore" });
    return true;
  } catch {
    return false;
  }
}

if (!haveGit()) {
  console.error("git is required and was not found on PATH.");
  process.exit(1);
}

function hasRemote() {
  const r = spawnSync("git", ["-C", LIB, "remote"], { encoding: "utf8" });
  return r.status === 0 && r.stdout.trim().length > 0;
}

if (existsSync(join(LIB, ".git"))) {
  if (hasRemote()) {
    console.log(`updating ${LIB}`);
    const r = run("git", ["-C", LIB, "pull", "--ff-only", "--quiet"]);
    if (r.status !== 0) {
      console.error("git pull failed. Resolve it by hand, then re-run.");
      process.exit(r.status ?? 1);
    }
  } else {
    // local-only checkout: nothing to pull, which is normal before you push it anywhere
    console.log(`using local checkout at ${LIB} (no git remote configured)`);
  }
} else if (existsSync(LIB)) {
  console.log(`${LIB} exists but is not a git checkout. Using it as-is.`);
} else {
  console.log(`cloning into ${LIB}`);
  mkdirSync(LIB, { recursive: true });
  const r = run("git", ["clone", "--quiet", REPO, LIB]);
  if (r.status !== 0) {
    console.error(`clone failed. If the repo is private, set up SSH or a token first.`);
    process.exit(r.status ?? 1);
  }
}

const installer = join(LIB, "install.sh");
if (!existsSync(installer)) {
  console.error(`no install.sh at ${installer}`);
  process.exit(1);
}

// --vendor fetches the third-party skill repos, which are gitignored and so absent on a fresh clone
const passthrough = ["--vendor", ...(has("--dry-run") ? ["--dry-run"] : [])];
const r = run("bash", [installer, ...passthrough], { cwd: LIB });
process.exit(r.status ?? 0);
