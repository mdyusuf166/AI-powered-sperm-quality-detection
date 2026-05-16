const path = require("path");

const patchPath = path.resolve(__dirname, "patch-fs-readlink.cjs");
require(patchPath);

const preloadFlag = `--require=${patchPath}`;
const existingNodeOptions = process.env.NODE_OPTIONS || "";
if (!existingNodeOptions.includes(preloadFlag)) {
  process.env.NODE_OPTIONS = `${existingNodeOptions} ${preloadFlag}`.trim();
}

require("next/dist/bin/next");

