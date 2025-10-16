

# GOAL: 
install this MCP and configure it for the right agents

frontend-code-reviewer
frontend-engineer
quality-guardian 

all need it for sure.

# Chrome DevTools MCP Server — Full Guide for Claude Code

## 🔍 What It Is (and Why You Care)

**Chrome DevTools MCP** is an open-source **Model Context Protocol (MCP) server** that bridges your AI coding agent (like **Claude Code**) with the **Chrome DevTools Protocol (CDP)**.  
Think of it as giving your AI **superpowers to inspect, control, and analyze real browser sessions** — all via structured MCP tool calls.

Under the hood:
- Uses **CDP** (the same protocol Chrome DevTools uses)
- Optionally leverages **Puppeteer** for reliability
- Exposes browser actions (open, click, trace, log, etc.) as **MCP tools**

### 🧠 Why It's Useful
- Debug flaky web apps (“why did this button not respond?”)
- Capture and summarize **performance traces**
- Inspect console/network logs automatically
- Simulate CPU throttling or slow network for perf testing
- Automate UI steps or record Lighthouse-style insights

---

## ⚙️ How It Works

1. Claude Code (client) connects to the **MCP server**.
2. The server launches or connects to a running Chrome instance.
3. It exposes structured **tools** such as:
   - `navigate_page`
   - `click`
   - `performance_start_trace`
   - `emulate_network`
   - `list_pages`
   - and more.
4. Claude agents invoke those tools directly in their reasoning chain.

All results come back as structured JSON — no raw console junk — so Claude can reason over the data, not just “read logs”.

---

## 🧯 Safety Note

This thing can literally drive your browser.  
If you connect it to your daily profile, it can read cookies, session storage, etc. **Don’t do that.**

👉 Always run it:
- In a **separate user-data directory**
- Or in **isolated mode**
- Avoid mixing your personal Chrome profile

---

## 🧩 Install & Wire It Into Claude Code

### Prerequisites
- **Node.js ≥ 20.19**
- **Chrome (Stable or Canary)** installed

### Option 1 — Quick CLI Install

```bash
claude mcp add chrome-devtools npx chrome-devtools-mcp@latest
```

This adds the MCP server globally for your current Claude Code environment.

### Option 2 — Manual Config

Edit your `.claude/mcp.json` or project-level config:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

This is identical to the CLI command, just explicit and version-pinnable.

---

## 🧠 Optional: Use an Existing Chrome Instance

If you prefer to connect to your own Chrome session instead of letting the MCP server launch one:

1. Launch Chrome manually:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-profile-stable
```

2. Point the MCP config at that Chrome:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "chrome-devtools-mcp@latest",
        "--browser-url=http://127.0.0.1:9222"
      ]
    }
  }
}
```

---

## 🧰 Useful Runtime Flags

Add these as arguments to tune your Chrome runs:

- `--headless=true` → run without UI  
- `--isolated=true` → temp Chrome profile auto-cleaned on exit  
- `--executablePath=/path/to/chrome` → use a custom Chrome binary  
- `--acceptInsecureCerts` → for internal/staging environments  
- `--chromeArg=--disable-gpu` → forward arbitrary Chrome args

---

## 🤖 Using It Inside an Agent (Claude Code)

Once installed, **any agent** can invoke the DevTools MCP.  
You don’t have to modify Claude itself — just create an agent prompt that *knows when to call it*.

### Example Agent (`.claude/agents/web-perf.md`)

```
You are a Web Performance Investigator.

When analyzing a page:
1. Use the Chrome DevTools MCP tools.
2. Open the page.
3. Run performance_start_trace for ~10 seconds.
4. Report long tasks, blocking scripts, and layout shifts.
5. Recommend optimizations.
```

Now ask Claude:

```
/agent web-perf Analyze https://example.com/checkout for bottlenecks.
```

Claude automatically uses the `chrome-devtools` MCP server.

---

## 🧪 Common Commands & Tools

| Tool Name | What It Does |
|------------|---------------|
| `navigate_page` | Opens a given URL |
| `click`, `fill`, `hover` | Interact with the DOM |
| `wait_for` | Wait for selector or event |
| `emulate_network`, `emulate_cpu` | Simulate slow envs |
| `performance_start_trace` / `performance_get_last_trace` | Record & summarize perf |
| `list_pages` | Show all tabs |
| `console_logs` | Collect browser console output |

---

## 🧭 Example Workflow

1. Claude agent runs:
   ```
   Check performance of https://developers.chrome.com
   ```
2. MCP spins up Chrome
3. Navigates, records trace, collects CPU/JS data
4. Claude gets a summary JSON
5. Agent replies with “Your LCP is 2.4s due to blocking script: analytics.js”

That’s your AI-driven Chrome audit, no Lighthouse UI required.

---

## 🧨 Troubleshooting

- **No browser opens** → That’s normal; headless by default until a tool is called.  
- **Permission denied / sandbox error** → Start Chrome manually and use `--browser-url`.  
- **Can’t connect** → Port conflict; make sure `--remote-debugging-port=9222` is free.  
- **Nothing happens** → Verify the agent actually called a tool (like `navigate_page`).

---

## 🧠 Why This Rocks in Claude Code

- Seamless **local execution** — no cloud dependency.  
- Multiple agents can reuse the same browser context.  
- You can combine it with other MCP servers (GitHub, Playwright, etc.) for full-stack automated debugging.  
- Claude can act like a one-person QA team with Chrome access.

---

## 🧾 Quick Copy-Paste Setup Recap

```bash
# 1) Add the MCP server to Claude Code
claude mcp add chrome-devtools npx chrome-devtools-mcp@latest

# 2) (Optional) Launch Chrome manually
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-profile-stable

# 3) (Optional) Connect the MCP server to your Chrome
# (edit .claude/mcp.json)
# {
#   "mcpServers": {
#     "chrome-devtools": {
#       "command": "npx",
#       "args": ["chrome-devtools-mcp@latest", "--browser-url=http://127.0.0.1:9222"]
#     }
#   }
# }

# 4) Test
# Ask Claude:
# "Check the performance of https://developers.chrome.com"
```

---

## 🧱 References (Validated)

- Official Chrome DevTools MCP repository (source & install instructions)  
  → https://github.com/modelcontextprotocol/servers/tree/main/src/chrome-devtools  
- Add MCP servers in Claude Code docs  
  → https://docs.anthropic.com/en/claude-code/mcp  
- Chrome DevTools Protocol docs (for what’s under the hood)  
  → https://chromedevtools.github.io/devtools-protocol/  
- Puppeteer (used by the MCP server)  
  → https://pptr.dev/  
- DebugBear: How DevTools Protocol powers performance audits  
  → https://www.debugbear.com/blog/chrome-devtools-protocol
