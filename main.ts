/**
 * Entry point for the news-image-20261124 make.fun submission.
 *
 * Copies the front-page image drawn by make_image.py (entry.png, sitting
 * next to this file) into the grader's output directory, then reads the
 * copy back and verifies it is byte-for-byte identical to the source.
 * Only the Node standard library is used, and the copy is deterministic:
 * the same input bytes always produce the same output bytes.
 */

import { copyFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

function fail(message: string): never {
  console.error(`error: ${message}`);
  process.exit(1);
}

function main(): void {
  const here = dirname(fileURLToPath(import.meta.url));
  const sourcePath = join(here, "entry.png");

  if (!existsSync(sourcePath)) {
    fail(`entry.png not found next to main.ts (looked in ${here})`);
  }

  const bytes = readFileSync(sourcePath);
  if (bytes.length < PNG_MAGIC.length || !bytes.subarray(0, 8).equals(PNG_MAGIC)) {
    fail("entry.png does not start with the PNG signature");
  }

  const outDir = resolve(process.env.MAKEFUN_OUTPUT_DIR ?? "/output");
  mkdirSync(outDir, { recursive: true });
  const targetPath = join(outDir, "entry.png");

  // Write via an explicit buffer copy so the output is exactly the input.
  writeFileSync(targetPath, bytes);
  copyFileSync(sourcePath, targetPath);

  const roundTrip = readFileSync(targetPath);
  if (!roundTrip.equals(bytes)) {
    fail("verification failed: output bytes differ from entry.png");
  }

  console.log(`entry.png written to ${targetPath} (${bytes.length} bytes, verified)`);
}

main();
