MCP configuration for Eternia (Junie)

This project ships a ready-to-use MCP configuration for Junie.


Where the files are
- MCP servers config: .junie/mcp/mcp.json
- Environment file: .junie/mcp/.env (not committed; copy from config/mcp/.env.example)

How to enable in Junie
1) Ensure the required MCP CLIs are installed and on your PATH:
   - github-mcp
   - mcp-sqlite
   - server-postgres
   - e2b-mcp
   - s3-mcp-server
2) Copy environment example and fill values:
   cp config/mcp/.env.example .junie/mcp/.env
   Then edit .junie/mcp/.env to set your tokens and database settings.
3) In Junie Settings → MCP Servers, choose "Load from file" and point to .junie/mcp/mcp.json, or paste the content. Click OK.
4) If servers don’t appear after clicking OK, check:
   - JSON is valid (no trailing commas or comments).
   - Each command is installed and resolvable on PATH (try running, e.g., `which github-mcp`).
   - Required env vars are present in .junie/mcp/.env. The config uses env://KEY lookups.
   - For sqlite-dev, make sure artifacts/dev.sqlite3 exists and is readable.
   - For Postgres, SSL mode and credentials match your cluster.

About capabilities
- github includes: read, write:pull_requests, write:issues (requires GitHub token scopes accordingly).
- sqlite-dev: read.
- postgres-readonly: read.
- e2b-sandbox: exec.
- aws-s3-read: read.

Troubleshooting tips
- Run Junie from a shell that has the MCP CLIs on PATH.
- On macOS with Homebrew, binaries often live in /opt/homebrew/bin; ensure PATH includes it.
- If your setup requires absolute paths to binaries, you may replace the `command` fields with absolute paths.
- Logs: Junie’s logs or your project logs/logs/eternia.log may show helpful errors.

Diagnosing GitHub MCP authentication (401 Unauthorized)
- Common causes:
  - Token missing inside the container (Docker env not forwarded) → ensure github.args includes: -e GITHUB_TOKEN and -e GITHUB_PERSONAL_ACCESS_TOKEN, and github.env maps them to env://GITHUB_TOKEN_RO.
  - Token lacks scopes → minimum recommended: repo (read), issues:write, pull_requests:write (match your configured capabilities).
  - Wrong env var name expected by the image → we forward both GITHUB_TOKEN and GITHUB_PERSONAL_ACCESS_TOKEN to be safe.
- Quick checks:
  1) Verify your .junie/mcp/.env has GITHUB_TOKEN_RO set (not empty) and Junie is launched from a shell that can read that file.
  2) Run the verifier:
     python3 scripts/verify_mcp_config.py
     It will validate mcp.json, PATH resolution, presence of token, and (for Docker) env forwarding flags.
  3) Inspect env inside the container:
     docker run --rm -i -e GITHUB_TOKEN -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server env | grep GITHUB_
     You should see both variables populated when Junie launches the container.
- Notes:
  - 401 from GitHub API is unrelated to GHCR image pull auth. If you get denied pulling the image from ghcr.io, see the section below about read:packages and docker login.
  - Fine-grained tokens must have access to the eternakk/eternia repository and the scopes listed above.

Security notes
- Never commit real secrets to the repo. Use .junie/mcp/.env (ignored) and keep tokens scoped minimally.

Testing your setup
- Run the quick verifier to ensure config and environment are ready:
  python3 scripts/verify_mcp_config.py
  You should see: [verify-mcp] OK: mcp.json valid, github server configured, command found, token present.
- If it fails, follow the hints it prints, then try again. Once it passes, start Junie and load .junie/mcp/mcp.json.

Using Docker for github-mcp
If you installed the GitHub MCP server via Docker (no local binary on PATH), you have two easy options:

Option A: Use the provided wrapper script
- Path: scripts/mcp/github-mcp-docker.sh
- Make it executable:
  chmod +x scripts/mcp/github-mcp-docker.sh
- Export your token in the shell that launches Junie:
  export GITHUB_TOKEN=your_pat_here
- Or simply set GITHUB_TOKEN_RO in .junie/mcp/.env; the wrapper auto-loads it and uses it as fallback for GITHUB_TOKEN.
- In Junie Settings → MCP Servers, either:
  - Replace the github server command with the absolute path to the wrapper script, or
  - Ensure the script directory is on your PATH and leave command as github-mcp then symlink:
    ln -s "$(pwd)/scripts/mcp/github-mcp-docker.sh" /usr/local/bin/github-mcp

Option B: Inline docker run (no script)
- In Junie Settings → MCP Servers, replace the github command with an absolute path to your shell and a one-liner, for example:
  /bin/bash -lc 'export GITHUB_TOKEN=env://GITHUB_TOKEN_RO; docker run --rm -i -e GITHUB_TOKEN ghcr.io/modelcontextprotocol/github-mcp:latest'
- Note: Some launchers may not support complex shell commands. The wrapper script is usually more reliable.

Important
- The GitHub token must have scopes that match your configured capabilities (read, write:issues, write:pull_requests).
- When using Docker, the config now forwards both GITHUB_PERSONAL_ACCESS_TOKEN and GITHUB_TOKEN into the container. Either one can be set in .junie/mcp/.env via env://GITHUB_TOKEN_RO.

- If you keep .junie/mcp/mcp.json as-is (command: "github-mcp"), ensure that command resolves either to the native binary or a symlink to the wrapper script.

Using Docker for the other MCP servers
The repo provides wrapper scripts for running additional MCP servers via Docker. Make them executable first:
  chmod +x scripts/mcp/mcp-sqlite-docker.sh \
          scripts/mcp/server-postgres-docker.sh \
          scripts/mcp/e2b-mcp-docker.sh \
          scripts/mcp/s3-mcp-server-docker.sh

sqlite-dev (mcp-sqlite)
- Script: scripts/mcp/mcp-sqlite-docker.sh
- Defaults: --db ./artifacts/dev.sqlite3 --mode ro (matches mcp.json)
- Optional env overrides:
  SQLITE_DB=./artifacts/your.sqlite3
  SQLITE_MODE=ro|rw
  SQLITE_MCP_IMAGE=ghcr.io/modelcontextprotocol/sqlite-mcp:latest
- Point Junie’s sqlite Dev server command to the script or create a symlink:
  ln -s "$(pwd)/scripts/mcp/mcp-sqlite-docker.sh" /usr/local/bin/mcp-sqlite

postgres-readonly (server-postgres)
- Script: scripts/mcp/server-postgres-docker.sh
- Required env vars (typically set in .junie/mcp/.env):
  PGHOST, PGPORT, PGDATABASE, PGUSER_RO, PGPASSWORD_RO
  Optional: PGSSLMODE (defaults to require)
  POSTGRES_MCP_IMAGE=ghcr.io/modelcontextprotocol/postgres-mcp:latest
- Point Junie’s postgres server command to the script or symlink:
  ln -s "$(pwd)/scripts/mcp/server-postgres-docker.sh" /usr/local/bin/server-postgres

E2B sandbox (e2b-mcp)
- Script: scripts/mcp/e2b-mcp-docker.sh
- Required env var: E2B_API_KEY (set in .junie/mcp/.env)
  Optional: E2B_MCP_IMAGE=ghcr.io/e2b-dev/e2b-mcp:latest
- Point Junie’s e2b server command to the script or symlink:
  ln -s "$(pwd)/scripts/mcp/e2b-mcp-docker.sh" /usr/local/bin/e2b-mcp

AWS S3 (s3-mcp-server)
- Script: scripts/mcp/s3-mcp-server-docker.sh
- Required env vars: AWS_REGION, AWS_ACCESS_KEY_ID_RO, AWS_SECRET_ACCESS_KEY_RO (set in .junie/mcp/.env)
  Optional: S3_MCP_IMAGE=ghcr.io/modelcontextprotocol/s3-mcp-server:latest
- Point Junie’s s3 server command to the script or symlink:
  ln -s "$(pwd)/scripts/mcp/s3-mcp-server-docker.sh" /usr/local/bin/s3-mcp-server

Notes
- You can also replace the command field in Junie’s MCP UI with the absolute path to each wrapper script instead of symlinking.
- Ensure the environment variables are exported in the shell that launches Junie so they propagate to the Docker containers.


Troubleshooting: ghcr.io denied when pulling MCP images
If you see an error like:
- Unable to find image 'ghcr.io/modelcontextprotocol/github-mcp:latest' locally
- docker: Error response from daemon: error from registry: denied

Why this happens
- GitHub Container Registry (GHCR) may require authentication to pull images (e.g., due to rate limits, private images, or policy changes). You need a token with read:packages scope to authenticate.

Fix (recommended)
1) Create a GitHub token with read:packages
   - GitHub → Settings → Developer settings → Personal access tokens.
   - Fine-grained or classic PAT is ok; ensure it includes read:packages.
2) Provide credentials via .junie/mcp/.env
   - Add these lines (the wrapper for github-mcp auto-loads this file):
     GHCR_USERNAME=your_github_username
     GHCR_TOKEN=your_pat_with_read_packages
   - Alternatively, if your existing GITHUB_TOKEN has read:packages, you can set only:
     GHCR_USERNAME=your_github_username
     # The wrapper will fall back to GITHUB_TOKEN for registry auth.
3) Re-run Junie or the wrapper
   - scripts/mcp/github-mcp-docker.sh will auto-login to ghcr.io and pull the image before starting.

Manual fallback
- You can also authenticate once in your shell:
  docker login ghcr.io -u your_github_username
  # paste your PAT (with read:packages) when prompted

Notes
- The same approach applies to other MCP images hosted on ghcr.io (sqlite, postgres, s3). If you hit a denied error there, run docker login ghcr.io once or set GHCR_USERNAME/GHCR_TOKEN similarly.
- Never commit secrets. Keep them in .junie/mcp/.env or your OS keychain.



Using the GitHub MCP GraphQL tool
- The configured GitHub MCP server (github-mcp) exposes a graphql tool that accepts a GraphQL query and variables.
- Ask Junie to call it, for example:
  Prompt: Use the GitHub MCP to run this GraphQL and show the first org project’s title and URL for org "eternakk".
  Query:
    query($org:String!){
      organization(login:$org){
        projectsV2(first:1){
          nodes { id number title closed url }
        }
      }
    }
  Variables:
    {"org":"eternakk"}
- Junie will call the github.graphql tool and return fields like title and url from data.organization.projectsV2.nodes[0].
- Requirements:
  - Ensure .junie/mcp/.env contains GITHUB_TOKEN_RO with access to the eternakk org and repos (fine‑grained or classic PAT).
  - If your org enforces SSO, authorize the token for the organization.
- If a 401/403 appears, re-run: python3 scripts/verify_mcp_config.py and check token scopes per the section above.

