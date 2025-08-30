#!/usr/bin/env node
// Vitest runner wrapper that supports a Jest-style --coverageThreshold flag.
// It captures the flag value and exposes it via process.env.COVERAGE_THRESHOLD,
// then invokes Vitest programmatically with remaining args.

import { startVitest } from 'vitest/node';

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
    // Ensure non-watch mode by mimicking `vitest run`
    const args = filtered.includes('run') ? filtered : ['run', ...filtered];
    const ctx = await startVitest('test', args, {});
    // Ensure Vitest cleans up; exit code should be set by Vitest
    await ctx?.close?.();
  } catch (err) {
    console.error('[vitest-runner] Error:', err);
    process.exitCode = 1;
  }
}

main();
