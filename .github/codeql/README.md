# CodeQL Configuration

This directory contains configuration files for GitHub's CodeQL security scanning tool.

## Files

- `codeql-config.yml`: Configuration file for CodeQL scanning, specifying languages, paths to scan/ignore, and queries to run.

## Enabling Code Scanning

To enable CodeQL scanning for this repository, follow these steps:

1. Go to the repository on GitHub
2. Navigate to "Settings" > "Security & analysis"
3. Find "Code scanning" in the list
4. Click "Set up" next to "GitHub Actions"
5. Select "CodeQL Analysis" from the list of available workflows
6. Click "Enable CodeQL"

Once enabled, CodeQL will run automatically on every push to the main branch and on pull requests, according to the configurations in:
- `.github/workflows/codeql-analysis.yml` (dedicated CodeQL workflow)
- `.github/workflows/security-scanning.yml` (includes CodeQL as part of security scanning)

## Workflow Files

This repository includes two workflow files that use CodeQL:

1. **codeql-analysis.yml**: A dedicated workflow for CodeQL analysis that:
   - Runs separately for Python and JavaScript
   - Uses the configuration in this directory
   - Categorizes results by language

2. **security-scanning.yml**: A comprehensive security scanning workflow that:
   - Includes Bandit and Safety for Python dependency scanning
   - Runs CodeQL analysis for both Python and JavaScript together
   - Uses the same configuration as the dedicated workflow

## Configuration Details

The current configuration:
- Scans Python and JavaScript/TypeScript code
- Ignores test files, node_modules, and other non-production code
- Runs security and quality queries

## Troubleshooting

If you see the error "Code scanning is not enabled for this repository", you need to follow the steps above to enable it in the repository settings. This is a GitHub-specific setting that cannot be enabled through code alone.

The workflow files have been configured with `continue-on-error: true` for the CodeQL analysis steps, which means that the workflows will not fail completely when code scanning is not enabled. This allows other security scanning steps to complete successfully even if CodeQL scanning is not enabled.

For more information about CodeQL, see the [GitHub documentation](https://docs.github.com/en/code-security/code-scanning/automatically-scanning-your-code-for-vulnerabilities-and-errors/about-code-scanning-with-codeql).
