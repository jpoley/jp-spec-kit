# Claude Code Permissions

JP Spec Kit uses Claude Code's `permissions.deny` feature to prevent accidental exposure of sensitive files and protect critical configuration.

## Denied Operations

The following operations are blocked by `.claude/settings.json`:

### Read Protection (Sensitive Data)

| Pattern | Protects |
|---------|----------|
| `Read(./.env)` | Root environment file |
| `Read(./.env.*)` | All env variants (.env.local, .env.production) |
| `Read(./secrets/**)` | Secrets directory |
| `Read(./**/.env)` | Nested .env files |
| `Read(./**/.env.*)` | Nested env variants |

### Write Protection (Critical Files)

| Pattern | Protects |
|---------|----------|
| `Write(./CLAUDE.md)` | Project Claude configuration |
| `Write(./memory/constitution.md)` | Constitutional principles |
| `Write(./uv.lock)` | Python dependency lock |
| `Write(./package-lock.json)` | NPM dependency lock |
| `Write(./yarn.lock)` | Yarn dependency lock |

### Bash Protection (Dangerous Commands)

| Pattern | Blocks |
|---------|--------|
| `Bash(sudo:*)` | All sudo commands |
| `Bash(rm:-rf:*)` | Recursive force delete |
| `Bash(rm:-fr:*)` | Force recursive delete |
| `Bash(chmod:777:*)` | World-writable permissions |
| `Bash(curl:*:|:*)` | Piped curl commands |
| `Bash(wget:*:|:*)` | Piped wget commands |

## Why These Rules?

### Sensitive Data Protection
- `.env` files often contain API keys, database credentials, and secrets
- The `secrets/` directory may contain certificates, keys, or tokens
- Accidental reading could expose these in Claude's context or logs

### Critical File Protection
- `CLAUDE.md` controls Claude's behavior - modification could alter project configuration
- `constitution.md` contains project principles that should be changed deliberately
- Lock files maintain dependency integrity and should be managed by package managers

### Dangerous Command Protection
- `sudo` can bypass security controls
- `rm -rf` can delete entire directories irreversibly
- `chmod 777` creates security vulnerabilities
- Piped `curl`/`wget` can execute untrusted code

## Bypassing Permissions

If you need to perform a denied operation:

1. **For reads**: Use the file viewer in your IDE or `cat` in a separate terminal
2. **For writes**: Manually edit the file outside Claude Code
3. **For bash**: Run the command directly in your terminal

## Customizing Permissions

Edit `.claude/settings.json` to modify rules:

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Write(./CLAUDE.md)"
    ]
  }
}
```

### Pattern Syntax

- `Tool(pattern)`: Deny specific tool with glob pattern
- `*` matches any characters
- `**` matches nested directories
- Patterns are relative to project root

## Security Best Practices

1. **Never commit secrets**: Use `.gitignore` for `.env` files
2. **Review permission changes**: Any modification to deny rules should be reviewed
3. **Fail-safe defaults**: Err on the side of denying access
4. **Audit regularly**: Review what operations are being denied
