import path from "node:path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Pin the workspace root to this repository's own root. Without this,
  // when the repo sits nested inside another repo that also has a
  // lockfile (e.g. as a git worktree subfolder), Next.js walks up,
  // finds both lockfiles, and can infer the outer repo as the root.
  turbopack: {
    root: path.join(__dirname, "../.."),
  },
};

export default nextConfig;
