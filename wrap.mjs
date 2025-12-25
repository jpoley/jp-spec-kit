#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import pty from "node-pty";

const LOG_DIR = process.env.LOG_DIR || ".logs";
fs.mkdirSync(LOG_DIR, { recursive: true });

const ts = new Date().toISOString().replace(/[:-]/g, "").replace(/\..+/, "Z");
const stdinLog = path.join(LOG_DIR, `claude-code.${ts}.stdin.log`);
const outLog   = path.join(LOG_DIR, `claude-code.${ts}.stdout.log`);

const stdinStream = fs.createWriteStream(stdinLog, { flags: "a" });
const outStream   = fs.createWriteStream(outLog,   { flags: "a" });

const shell = "claude-code";
const args = process.argv.slice(2);

const term = pty.spawn(shell, args, {
  name: process.env.TERM || "xterm-256color",
  cols: process.stdout.columns || 80,
  rows: process.stdout.rows || 24,
  cwd: process.cwd(),
  env: process.env,
});

// Forward output to your terminal + log it
term.onData((data) => {
  process.stdout.write(data);
  outStream.write(data);
});

// Read *raw* user keystrokes from the terminal and forward to PTY
process.stdin.setRawMode?.(true);
process.stdin.resume();
process.stdin.on("data", (buf) => {
  // Log exactly what user typed (raw bytes)
  stdinStream.write(buf);
  // Forward into claude-code’s PTY
  term.write(buf.toString("utf8"));
});

// Handle resize
process.stdout.on("resize", () => {
  term.resize(process.stdout.columns, process.stdout.rows);
});

// Exit handling
term.onExit(({ exitCode }) => {
  stdinStream.end();
  outStream.end();
  process.exit(exitCode ?? 0);
});
