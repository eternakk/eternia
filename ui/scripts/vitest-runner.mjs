#!/usr/bin/env node
// Vitest runner wrapper that supports a Jest-style --coverageThreshold flag.
// It captures the flag value and exposes it via process.env.COVERAGE_THRESHOLD,
// then invokes Vitest programmatically with remaining args.

import { fileURLToPath } from 'url';
import path from 'path';
import { spawn } from 'node:child_process';

// Ensure we run from the UI package root regardless of where npm was invoked
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');
try {
  process.chdir(projectRoot);
} catch {
  // If chdir fails, continue; Vitest will still try using cwd
}

function extractCoverageThresholdArg(argv) {
  let threshold;
  const filtered = [];

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];

    // --coverageThreshold=JSON
    if (arg.startsWith('--coverageThreshold=')) {
      threshold = arg.slice('--coverageThreshold='.length);
      continue;
    }
    // --coverage-threshold=JSON (fallback kebab-case)
    if (arg.startsWith('--coverage-threshold=')) {
      threshold = arg.slice('--coverage-threshold='.length);
      continue;
    }

    // --coverageThreshold JSON
    if (arg === '--coverageThreshold') {
      threshold = argv[i + 1];
      i += 1;
      continue;
    }
    // --coverage-threshold JSON (fallback kebab-case)
    if (arg === '--coverage-threshold') {
      threshold = argv[i + 1];
      i += 1;
      continue;
    }

    filtered.push(arg);
  }

  return { threshold, filtered };
}

async function main() {
  const argv = process.argv.slice(2);
  const { threshold, filtered } = extractCoverageThresholdArg(argv);

  if (threshold) {
    process.env.COVERAGE_THRESHOLD = threshold;
  }

  try {
    // Build CLI args for Vitest, ensuring non-watch mode with `run`
    const cleaned = filtered.filter(a => a !== 'run');
    const args = ['run', ...cleaned];

    const vitestBin = path.resolve(projectRoot, 'node_modules', '.bin', process.platform === 'win32' ? 'vitest.cmd' : 'vitest');
    const child = spawn(vitestBin, args, { stdio: 'inherit', env: process.env });

    await new Promise((resolve, reject) => {
      child.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`Vitest exited with code ${code}`));
        } else {
          resolve(null);
        }
      });
      child.on('error', reject);
    });
  } catch (err) {
    console.error('[vitest-runner] Error:', err);
    process.exitCode = 1;
  }
}

main();
