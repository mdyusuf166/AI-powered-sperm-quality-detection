const fs = require("fs");

if (global.__SPERM_ANALYSIS_PATCHED_READLINK__) {
  return;
}
global.__SPERM_ANALYSIS_PATCHED_READLINK__ = true;

function normalizeReadlinkError(error) {
  if (error && error.code === "EISDIR" && typeof error.message === "string") {
    error.code = "EINVAL";
    error.message = error.message.replace("EISDIR", "EINVAL");
  }
  return error;
}

function fallbackRealpath(error, targetPath) {
  if (error && error.code === "EISDIR") {
    return targetPath;
  }
  throw normalizeReadlinkError(error);
}

const originalReadlink = fs.readlink;
fs.readlink = function patchedReadlink(...args) {
  const callback = args.pop();
  return originalReadlink.call(fs, ...args, (error, ...rest) => {
    callback(normalizeReadlinkError(error), ...rest);
  });
};

const originalReadlinkSync = fs.readlinkSync;
fs.readlinkSync = function patchedReadlinkSync(...args) {
  try {
    return originalReadlinkSync.call(fs, ...args);
  } catch (error) {
    throw normalizeReadlinkError(error);
  }
};

const originalRealpath = fs.realpath;
fs.realpath = function patchedRealpath(...args) {
  const callback = args.pop();
  const targetPath = args[0];
  return originalRealpath.call(fs, ...args, (error, resolvedPath) => {
    if (error && error.code === "EISDIR") {
      callback(null, targetPath);
      return;
    }
    callback(normalizeReadlinkError(error), resolvedPath);
  });
};

const originalRealpathSync = fs.realpathSync;
fs.realpathSync = function patchedRealpathSync(...args) {
  try {
    return originalRealpathSync.call(fs, ...args);
  } catch (error) {
    return fallbackRealpath(error, args[0]);
  }
};

if (fs.realpath.native) {
  const originalNativeRealpath = fs.realpath.native;
  fs.realpath.native = function patchedNativeRealpath(...args) {
    const callback = args.pop();
    const targetPath = args[0];
    return originalNativeRealpath.call(fs.realpath, ...args, (error, resolvedPath) => {
      if (error && error.code === "EISDIR") {
        callback(null, targetPath);
        return;
      }
      callback(normalizeReadlinkError(error), resolvedPath);
    });
  };
}

if (fs.realpathSync.native) {
  const originalNativeRealpathSync = fs.realpathSync.native;
  fs.realpathSync.native = function patchedNativeRealpathSync(...args) {
    try {
      return originalNativeRealpathSync.call(fs.realpathSync, ...args);
    } catch (error) {
      return fallbackRealpath(error, args[0]);
    }
  };
}

if (fs.promises?.readlink) {
  const originalPromiseReadlink = fs.promises.readlink.bind(fs.promises);
  fs.promises.readlink = async (...args) => {
    try {
      return await originalPromiseReadlink(...args);
    } catch (error) {
      throw normalizeReadlinkError(error);
    }
  };
}

if (fs.promises?.realpath) {
  const originalPromiseRealpath = fs.promises.realpath.bind(fs.promises);
  fs.promises.realpath = async (...args) => {
    try {
      return await originalPromiseRealpath(...args);
    } catch (error) {
      if (error && error.code === "EISDIR") {
        return args[0];
      }
      throw normalizeReadlinkError(error);
    }
  };
}

