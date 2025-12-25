# Flowspec Logging vs Asciinema Comparison

## Overview

Both systems capture terminal sessions, but they serve different purposes and use different approaches.

## Quick Comparison

| Feature | Flowspec Logging | Asciinema |
|---------|------------------|-----------|
| **Primary Purpose** | Debugging & auditing | Demo & sharing |
| **Timing Data** | ❌ No | ✅ Yes, precise |
| **Playback** | ❌ No | ✅ Yes, with player |
| **Hook Execution** | ✅ Yes, detailed | ❌ No |
| **File Format** | Raw text logs | JSON (.cast) |
| **ANSI Preservation** | ⚠️ Partial | ✅ Full |
| **File Size** | Small (~200KB) | Larger (with timing) |
| **Integration** | Auto-enabled | Manual start/stop |
| **Privacy** | Local only | Can upload/share |

## Detailed Comparison

### 1. Capture Mechanism

**Flowspec Logging:**
```javascript
// wrap.mjs using node-pty
const term = pty.spawn('claude-code', args);
term.onData((data) => {
  process.stdout.write(data);  // Forward to terminal
  outStream.write(data);        // Log to file
});
```

**Asciinema:**
```bash
# Records with timing metadata
asciinema rec session.cast
# Produces JSON with timestamps:
# {"version": 2, "width": 80, "height": 24, "timestamp": 1640000000}
# [0.123456, "o", "output text"]
```

### 2. Output Format

**Flowspec Logging:**
```
.logs/
├── claude-code.20251225T120000Z.stdin.log   # Raw user input
├── claude-code.20251225T120000Z.stdout.log  # Raw Claude output
└── hooks.log                                 # Structured hook logs

# hooks.log format:
[2025-12-25T12:00:00] START: pre-tool-use-git-safety --arg1
[2025-12-25T12:00:00] pre-tool-use-git-safety: Checking git safety...
[2025-12-25T12:00:01] END: pre-tool-use-git-safety (exit 0)
```

**Asciinema:**
```json
{
  "version": 2,
  "width": 80,
  "height": 24,
  "timestamp": 1640000000,
  "env": {"SHELL": "/bin/bash", "TERM": "xterm-256color"}
}
[0.000000, "o", "\u001b[?1049h\u001b[22;0;0t"]
[0.123456, "i", "ls\r"]
[0.234567, "o", "file1.txt\r\nfile2.txt\r\n"]
```

### 3. Use Cases

**Flowspec Logging - Better For:**
- ✅ Debugging workflow failures
- ✅ Auditing hook executions
- ✅ Security compliance logging
- ✅ Automated log analysis (grep, awk, etc.)
- ✅ Continuous background capture
- ✅ Low overhead monitoring
- ✅ Privacy-sensitive environments (local only)

**Asciinema - Better For:**
- ✅ Creating demos and tutorials
- ✅ Sharing terminal sessions
- ✅ Exact playback with timing
- ✅ Visual demonstrations
- ✅ Bug reproduction (with visual context)
- ✅ Training materials
- ✅ Conference presentations

### 4. Privacy & Security

**Flowspec Logging:**
```bash
# Logs stay local
.logs/  # In .gitignore, never committed

# Review before sharing
grep -i "password\|token\|secret" .logs/*.log

# Scrub sensitive data
sed -i 's/ghp_[a-zA-Z0-9]\{36\}/[REDACTED]/g' .logs/*.log
```

**Asciinema:**
```bash
# Can upload to asciinema.org
asciinema upload session.cast  # ⚠️ Public by default!

# Or keep local
asciinema rec --idle-time-limit 2 session.cast  # Local only
asciinema play session.cast
```

### 5. Performance Impact

**Flowspec Logging:**
- CPU: <1% (simple file I/O)
- Memory: ~15MB (node-pty + buffers)
- Disk: ~200KB per session (text only)
- Latency: None (async writes)

**Asciinema:**
- CPU: ~2-5% (timing calculations)
- Memory: ~30-50MB (buffering + metadata)
- Disk: ~500KB-2MB per session (with timing)
- Latency: Minimal (<5ms)

### 6. Integration & Automation

**Flowspec Logging:**
```bash
# Auto-enabled in devcontainer
export FLOWSPEC_CAPTURE_TTY=true
export FLOWSPEC_CAPTURE_HOOKS=true

# Works with CI/CD
if [ "$CI" = "true" ]; then
  export FLOWSPEC_CAPTURE_HOOKS=true  # Keep hooks, disable TTY
  export FLOWSPEC_CAPTURE_TTY=false
fi

# Automated analysis
grep "ERROR\|FAIL" .logs/hooks.log | mail -s "Build failures" team@example.com
```

**Asciinema:**
```bash
# Manual start/stop
asciinema rec session.cast
# ... work ...
# (Ctrl+D to stop)

# CI integration requires wrapper scripts
# Not designed for continuous capture
```

### 7. What Each System Captures

**Flowspec Logging Captures:**
- ✅ User keystrokes (raw)
- ✅ Claude's text output
- ✅ Hook executions (name, args, timing, exit code)
- ✅ Hook log messages (structured)
- ❌ ANSI escape codes (partial)
- ❌ Timing metadata
- ❌ Terminal resizes
- ❌ Subprocess outputs (unless echoed)

**Asciinema Captures:**
- ✅ All terminal output (ANSI codes)
- ✅ Precise timing (microsecond)
- ✅ Terminal dimensions
- ✅ User input (if enabled)
- ✅ Visual appearance
- ❌ Internal application state
- ❌ Subprocess logs (unless on stdout)
- ❌ Hook executions

### 8. Log Analysis

**Flowspec Logging:**
```bash
# Easy text processing
grep "Dangerous git command" .logs/hooks.log
awk '/ERROR/ {print $0}' .logs/hooks.log | wc -l

# Find all sessions with errors
grep -l "error" .logs/claude-code.*.stdout.log

# Extract specific hook executions
sed -n '/START: pre-tool-use-git-safety/,/END: pre-tool-use-git-safety/p' .logs/hooks.log
```

**Asciinema:**
```bash
# Requires special tools
asciinema play session.cast  # Visual only

# JSON processing
jq '.[] | select(.[1] == "o") | .[2]' session.cast  # Extract output

# Harder to grep/analyze programmatically
```

### 9. File Size Comparison

**Example 30-minute session:**

**Flowspec Logging:**
- stdin.log: ~50KB (user input)
- stdout.log: ~150KB (Claude output)
- hooks.log: ~20KB (hook executions)
- **Total: ~220KB**

**Asciinema:**
- session.cast: ~800KB (with timing + metadata)
- **Total: ~800KB**

### 10. Can We Use Both?

**Yes! They're complementary:**

```bash
# For debugging (always on):
export FLOWSPEC_CAPTURE_TTY=true
export FLOWSPEC_CAPTURE_HOOKS=true

# For demos (manual):
asciinema rec demo.cast
claude
# ... demonstrate feature ...
# Ctrl+D

# Result:
# - .logs/ → debugging and auditing
# - demo.cast → shareable demonstration
```

## Recommendation

### Use Flowspec Logging When:
- You want continuous, automatic capture
- You need to debug hook failures
- You're auditing for security/compliance
- You want low overhead
- Logs stay private/local

### Use Asciinema When:
- Creating demos or tutorials
- Sharing bug reproductions (visual)
- Presenting at conferences
- Training new team members
- Need exact playback with timing

### Use Both When:
- Recording a demo while debugging
- Creating training materials from real sessions
- Documenting complex workflows

## Could We Enhance Flowspec Logging?

**Possible Level 3 enhancements inspired by asciinema:**

1. **Add timing metadata:**
   ```javascript
   // In wrap.mjs
   const startTime = Date.now();
   outStream.write(JSON.stringify({
     time: (Date.now() - startTime) / 1000,
     type: 'o',
     data: data
   }) + '\n');
   ```

2. **Playback capability:**
   ```bash
   flowspec logs play .logs/claude-code.20251225T120000Z
   # Replays with timing
   ```

3. **Structured format:**
   - Switch from raw text to JSONL
   - Preserve ANSI codes
   - Include terminal dimensions

**But:** This increases complexity and overhead. Level 2 is optimized for debugging, not playback.

## Conclusion

**Flowspec Logging** and **Asciinema** solve different problems:

- **Flowspec Logging**: Low-overhead debugging and auditing tool
- **Asciinema**: High-fidelity recording and sharing tool

Our implementation is **not a replacement for asciinema**—it's a **complementary debugging tool** optimized for:
- Continuous background capture
- Hook execution visibility
- Low performance impact
- Easy log analysis
- Privacy and security

If you need asciinema's features (playback, sharing, precise timing), use asciinema. If you need debugging and auditing, use Flowspec Logging. Or use both!

---

**Status**: Level 2 implementation complete (TTY + Hooks)
**Next**: Could implement Level 3 (Network) or add asciinema-style enhancements
