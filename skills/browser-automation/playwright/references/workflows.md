# Playwright CLI Workflows

Use the wrapper script and snapshot often.
Assume `PWCLI` is set and `pwcli` is an alias for `"$PWCLI"`.
In this repo, run commands from `output/playwright/<label>/` to keep artifacts contained.

> **Note**: Since Playwright v1.62.0, the CLI is built into the main `playwright` package.
> You can also use `npx playwright cli` directly instead of the wrapper script.

## Standard interaction loop

```bash
pwcli open https://example.com
pwcli snapshot
pwcli click e3
pwcli snapshot
```

## Form submission

```bash
pwcli open https://example.com/form --headed
pwcli snapshot
pwcli fill e1 "user@example.com"
pwcli fill e2 "password123"
pwcli click e3
pwcli snapshot
pwcli screenshot
```

## Data extraction

```bash
pwcli open https://example.com
pwcli snapshot
pwcli eval "document.title"
pwcli eval "el => el.textContent" e12
```

## Debugging and inspection

Capture console messages and network activity after reproducing an issue:

```bash
pwcli console warning
pwcli network
```

Record a trace around a suspicious flow:

```bash
pwcli tracing-start
# reproduce the issue
pwcli tracing-stop
pwcli screenshot
```

## Sessions

Use sessions to isolate work across projects:

```bash
pwcli --session marketing open https://example.com
pwcli --session marketing snapshot
pwcli --session checkout open https://example.com/checkout
```

Or set the session once:

```bash
export PLAYWRIGHT_CLI_SESSION=checkout
pwcli open https://example.com/checkout
```

## Configuration file

By default, the CLI reads `playwright-cli.json` from the current directory. Use `--config` to point at a specific file.

Minimal example:

```json
{
  "browser": {
    "launchOptions": {
      "headless": false
    },
    "contextOptions": {
      "viewport": { "width": 1280, "height": 720 }
    }
  }
}
```

## New in Playwright v1.60–v1.62

Key features that may be useful in CLI workflows:

- **AbortSignal support** (v1.62): Most operations accept a `signal` option to cancel long-running actions.
- **WebP screenshots** (v1.62): `screenshot` can now output `.webp` format for smaller file sizes.
- **`scroll` option** (v1.62): Actions accept `scroll: "none"` to opt out of automatic scroll-into-view.
- **`locator.drop()`** (v1.60): Simulate drag-and-drop of files or clipboard data onto an element.
- **Aria snapshots with boxes** (v1.60): `ariaSnapshot()` can append bounding box info as `[box=x,y,width,height]`.
- **WebAuthn passkeys** (v1.61): Virtual authenticator for testing passkey flows without hardware.
- **WebStorage API** (v1.61): Read/write `localStorage` / `sessionStorage` via page methods.

## Troubleshooting

- If an element ref fails, run `pwcli snapshot` again and retry.
- If the page looks wrong, re-open with `--headed` and resize the window.
- If a flow depends on prior state, use a named `--session`.
