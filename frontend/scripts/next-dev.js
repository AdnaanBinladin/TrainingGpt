const { spawn } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");

const canonicalCwd = fs.realpathSync.native(process.cwd());
process.chdir(canonicalCwd);

const nextBin = path.join(
  canonicalCwd,
  "node_modules",
  "next",
  "dist",
  "bin",
  "next"
);

const port = process.env.PORT || "3101";

const child = spawn(process.execPath, [nextBin, "dev", "-H", "0.0.0.0", "-p", port, "--webpack"], {
  cwd: canonicalCwd,
  env: {
    ...process.env,
    INIT_CWD: canonicalCwd,
    PWD: canonicalCwd,
  },
  stdio: "inherit",
});

child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }

  process.exit(code || 0);
});
