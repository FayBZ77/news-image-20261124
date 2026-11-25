// News-image entry for 24 November 2026 (Node 22, standard library only).
//
// The entry image is the entry.png shipped beside this file: a broadsheet front
// page drawn from Tuesday's reporting (Hormuz tankers, Riyadh, Zaporizhzhia,
// Shenzhou-24, the US House, Huawei). This program places those exact bytes at
// /output/entry.png. The gate sees only the file's bytes, so the program
// verifies the copy byte for byte before it exits.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const sourcePath = join(here, 'entry.png');
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const targetPath = join(outputDir, 'entry.png');

const image = readFileSync(sourcePath);
if (image.subarray(1, 4).toString('latin1') !== 'PNG') {
  throw new Error(`entry.png beside main.ts is not a PNG (saw ${image.subarray(0, 8).toString('hex')})`);
}

mkdirSync(outputDir, { recursive: true });
writeFileSync(targetPath, image);

const written = readFileSync(targetPath);
if (!written.equals(image)) {
  throw new Error('entry.png copy failed verification: bytes differ after write');
}
console.log(`wrote ${targetPath} (${written.length} bytes, verified)`);
