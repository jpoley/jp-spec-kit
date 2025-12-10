# Rust CLI Project Constitution Example

This example shows a customized constitution for a Rust command-line application.

## Before: Template

```markdown
## Technology Stack
<!-- SECTION:TECH_STACK:BEGIN -->
<!-- NEEDS_VALIDATION: Populate with detected languages/frameworks -->
[LANGUAGES_AND_FRAMEWORKS]
<!-- SECTION:TECH_STACK:END -->
```

## After: Customized

```markdown
## Technology Stack
<!-- SECTION:TECH_STACK:BEGIN -->
- **Primary Language**: Rust 1.75+ (2021 edition)
- **CLI Framework**: clap v4 (derive API)
- **Error Handling**: anyhow + thiserror
- **Async Runtime**: tokio (if needed)
- **Build Tool**: Cargo
- **Distribution**: cargo-dist
<!-- SECTION:TECH_STACK:END -->

## Quality Standards
<!-- SECTION:QUALITY:BEGIN -->
- Test coverage minimum: 80%
- All public items must have documentation
- No unsafe code without justification
- Zero warnings on stable + clippy
- MSRV (Minimum Supported Rust Version) documented
<!-- SECTION:QUALITY:END -->

## Testing
<!-- SECTION:TESTING:BEGIN -->
- Framework: cargo test (built-in)
- Integration tests in tests/ directory
- Documentation tests in all public modules
- Property testing: proptest for complex logic
- CLI testing: assert_cmd + predicates
- Coverage: cargo-tarpaulin with 80% threshold
<!-- SECTION:TESTING:END -->

## Code Quality
<!-- SECTION:CODE_QUALITY:BEGIN -->
- Linter: clippy (all lints, pedantic group)
- Formatter: rustfmt (edition 2021)
- Security: cargo-audit for dependency vulnerabilities
- Unused deps: cargo-udeps
- Outdated deps: cargo-outdated
<!-- SECTION:CODE_QUALITY:END -->

## CI/CD
<!-- SECTION:CICD:BEGIN -->
- Platform: GitHub Actions
- Workflows: test.yml, release.yml
- Cross-compilation: Linux, macOS, Windows
- Distribution: cargo-dist + GitHub Releases
- Signing: Cosign for binary attestation
<!-- SECTION:CICD:END -->

## CLI Standards
<!-- SECTION:CLI:BEGIN -->
- Follow Unix philosophy (do one thing well)
- Support --help and --version flags
- Use clap derive API for type-safe commands
- Structured error messages with context
- Color output: supports NO_COLOR environment variable
- Progress bars for long operations
<!-- SECTION:CLI:END -->

## Error Handling
<!-- SECTION:ERROR_HANDLING:BEGIN -->
- Use thiserror for library errors
- Use anyhow for application errors
- Provide context with .context() or .with_context()
- User-facing errors: clear, actionable messages
- Debug errors: detailed technical information
- Exit codes follow sysexits.h conventions
<!-- SECTION:ERROR_HANDLING:END -->

## Dependencies
<!-- SECTION:DEPENDENCIES:BEGIN -->
- Prefer standard library when possible
- Minimize dependency tree (cargo-tree audit)
- Pin major versions in Cargo.toml
- Regular dependency updates (Dependabot)
- License compatibility check (cargo-deny)
<!-- SECTION:DEPENDENCIES:END -->

## Performance
<!-- SECTION:PERFORMANCE:BEGIN -->
- Profile with cargo-flamegraph
- Benchmark critical paths with criterion
- Binary size optimization (strip symbols, LTO)
- Compile time: incremental compilation enabled
- Release profile: opt-level = 3, lto = true
<!-- SECTION:PERFORMANCE:END -->

## Security
<!-- SECTION:SECURITY:BEGIN -->
- No unsafe code without explicit // SAFETY: comment
- Input validation on all user data
- Sensitive data: use secrecy crate
- Cryptography: use well-audited crates (ring, rustls)
- File permissions: proper umask for output files
<!-- SECTION:SECURITY:END -->

## Documentation
<!-- SECTION:DOCUMENTATION:BEGIN -->
- README.md: installation, usage, examples
- CHANGELOG.md: keep-a-changelog format
- API docs: cargo doc --no-deps --open
- Examples: examples/ directory with runnable code
- Man pages: generated from clap (clap_mangen)
<!-- SECTION:DOCUMENTATION:END -->
```

## repo-facts.md Generated

```yaml
---
detected_at: "2025-12-04T10:30:00"
languages:
  - Rust
frameworks:
  - clap
  - tokio
build_tool: Cargo
ci_cd: GitHub Actions
test_framework: cargo test
linter: clippy
formatter: rustfmt
security_tools:
  - cargo-audit
  - cargo-deny
distribution: cargo-dist
platforms:
  - Linux
  - macOS
  - Windows
---
```

## Key Customization Points

1. **Technology Stack**: Rust 1.75+, clap v4, anyhow/thiserror
2. **Quality Standards**: 80% coverage, no unsafe without justification
3. **Testing**: cargo test, assert_cmd for CLI tests, proptest
4. **CLI Standards**: Unix philosophy, color support, progress bars
5. **Error Handling**: thiserror for libraries, anyhow for applications
6. **Performance**: Benchmarking, binary size optimization

## Usage

```bash
# After running /speckit:constitution
specify constitution validate

# Apply customizations from this example
# Edit .specify/memory/constitution.md
# Replace template sections with customized versions
```

## Project Structure Example

```
project/
├── src/
│   ├── main.rs              # Entry point
│   ├── cli.rs               # Command definitions
│   ├── commands/            # Command implementations
│   ├── lib.rs               # Library API (if applicable)
│   └── error.rs             # Error types
├── tests/
│   └── integration_tests.rs # CLI integration tests
├── examples/
│   └── basic_usage.rs       # Example programs
├── benches/
│   └── benchmarks.rs        # Performance benchmarks
├── Cargo.toml
├── Cargo.lock
└── README.md
```

## Cargo.toml Example

```toml
[package]
name = "my-cli"
version = "0.1.0"
edition = "2021"
rust-version = "1.75"

[dependencies]
clap = { version = "4.5", features = ["derive"] }
anyhow = "1.0"
thiserror = "1.0"

[dev-dependencies]
assert_cmd = "2.0"
predicates = "3.0"
proptest = "1.4"

[profile.release]
opt-level = 3
lto = true
strip = true
```

## Common Customizations

### Async CLI

If building an async CLI:

```markdown
## Technology Stack
<!-- SECTION:TECH_STACK:BEGIN -->
- **Primary Language**: Rust 1.75+ (2021 edition)
- **CLI Framework**: clap v4 (derive API)
- **Async Runtime**: tokio with full features
- **HTTP Client**: reqwest with rustls
<!-- SECTION:TECH_STACK:END -->
```

### Library + CLI

If building both a library and CLI:

```markdown
## Project Structure
<!-- SECTION:STRUCTURE:BEGIN -->
- Library: src/lib.rs with public API
- Binary: src/main.rs as thin wrapper
- Separate CLI and library features
- Library must be usable standalone
<!-- SECTION:STRUCTURE:END -->
```

### Cross-Platform Considerations

```markdown
## Platform Support
<!-- SECTION:PLATFORMS:BEGIN -->
- Primary: Linux x86_64 + ARM64
- Secondary: macOS (Intel + Apple Silicon), Windows
- CI: Test on all platforms before release
- Platform-specific code: cfg attributes
<!-- SECTION:PLATFORMS:END -->
```
