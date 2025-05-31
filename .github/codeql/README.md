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

Once enabled, CodeQL will run automatically on every push to the main branch and on pull requests, according to the configuration in `.github/workflows/security-scanning.yml`.

## Configuration Details

The current configuration:
- Scans Python and JavaScript/TypeScript code
- Ignores test files, node_modules, and other non-production code
- Runs security and quality queries

For more information about CodeQL, see the [GitHub documentation](https://docs.github.com/en/code-security/code-scanning/automatically-scanning-your-code-for-vulnerabilities-and-errors/about-code-scanning-with-codeql).