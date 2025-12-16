"""Fix pattern library for common vulnerabilities.

This module provides fix templates for common vulnerability types:
- SQL Injection (CWE-89)
- Cross-Site Scripting (CWE-79)
- Path Traversal (CWE-22)
- Hardcoded Secrets (CWE-798)
- Weak Cryptography (CWE-327)
"""

from dataclasses import dataclass, field

from flowspec_cli.security.fixer.models import FixPattern


@dataclass
class FixPatternLibrary:
    """Library of fix patterns for common vulnerabilities."""

    patterns: dict[str, FixPattern] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize with default patterns."""
        if not self.patterns:
            self._load_default_patterns()

    def get_pattern(self, cwe_id: str) -> FixPattern | None:
        """Get fix pattern for a CWE."""
        return self.patterns.get(cwe_id)

    def add_pattern(self, pattern: FixPattern) -> None:
        """Add or update a fix pattern."""
        self.patterns[pattern.cwe_id] = pattern

    def _load_default_patterns(self) -> None:
        """Load default fix patterns."""
        self.patterns = {
            "CWE-89": self._sql_injection_pattern(),
            "CWE-79": self._xss_pattern(),
            "CWE-22": self._path_traversal_pattern(),
            "CWE-798": self._hardcoded_secrets_pattern(),
            "CWE-327": self._weak_crypto_pattern(),
        }

    def _sql_injection_pattern(self) -> FixPattern:
        """SQL Injection fix pattern."""
        return FixPattern(
            cwe_id="CWE-89",
            name="SQL Injection",
            description="Use parameterized queries instead of string concatenation",
            vulnerable_pattern=r'(query|sql)\s*=\s*["\'].*["\']\s*\+',
            fix_template="""
# Fix: Use parameterized queries
# Before: query = "SELECT * FROM users WHERE id = " + user_id
# After:  cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# Python (sqlite3/psycopg2):
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# Python (SQLAlchemy):
session.query(User).filter(User.id == user_id).first()

# Node.js (pg):
client.query('SELECT * FROM users WHERE id = $1', [userId])
""",
            examples=[
                {
                    "before": 'query = "SELECT * FROM users WHERE id = " + user_id',
                    "after": 'cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))',
                    "language": "python",
                },
                {
                    "before": "query = f\"SELECT * FROM users WHERE name = '{name}'\"",
                    "after": 'cursor.execute("SELECT * FROM users WHERE name = ?", (name,))',
                    "language": "python",
                },
                {
                    "before": "const query = `SELECT * FROM users WHERE id = ${userId}`",
                    "after": "client.query('SELECT * FROM users WHERE id = $1', [userId])",
                    "language": "javascript",
                },
            ],
        )

    def _xss_pattern(self) -> FixPattern:
        """Cross-Site Scripting fix pattern."""
        return FixPattern(
            cwe_id="CWE-79",
            name="Cross-Site Scripting (XSS)",
            description="Escape user input before rendering in HTML",
            vulnerable_pattern=r"innerHTML\s*=|document\.write\(|dangerouslySetInnerHTML",
            fix_template="""
# Fix: Escape output or use safe DOM methods
# Before: element.innerHTML = userInput
# After:  element.textContent = userInput

# JavaScript (DOM):
element.textContent = userInput  // Safe - auto-escapes

# JavaScript (create element):
const text = document.createTextNode(userInput)
element.appendChild(text)

# React:
// Use JSX (auto-escapes): <div>{userInput}</div>
// Avoid: <div dangerouslySetInnerHTML={{__html: userInput}} />

# Python (Jinja2):
{{ user_input }}  // Auto-escapes by default
{{ user_input | e }}  // Explicit escape

# Python (Django):
{{ user_input }}  // Auto-escapes by default
""",
            examples=[
                {
                    "before": "element.innerHTML = userInput",
                    "after": "element.textContent = userInput",
                    "language": "javascript",
                },
                {
                    "before": "<div dangerouslySetInnerHTML={{__html: userInput}} />",
                    "after": "<div>{userInput}</div>",
                    "language": "jsx",
                },
                {
                    "before": "document.write(userInput)",
                    "after": "document.body.appendChild(document.createTextNode(userInput))",
                    "language": "javascript",
                },
            ],
        )

    def _path_traversal_pattern(self) -> FixPattern:
        """Path Traversal fix pattern."""
        return FixPattern(
            cwe_id="CWE-22",
            name="Path Traversal",
            description="Validate file paths against a base directory",
            vulnerable_pattern=r"open\(.*\+|Path\(.*\+|os\.path\.join\(.*request",
            fix_template="""
# Fix: Validate path is within allowed directory
# Before: open(user_path)
# After:  Validate path, then open

# Python (pathlib - recommended):
from pathlib import Path

base_dir = Path("/safe/directory").resolve()
user_path = (base_dir / user_input).resolve()

# Validate path is within base directory
if not user_path.is_relative_to(base_dir):
    raise ValueError("Path traversal attempt detected")

with open(user_path, encoding="utf-8") as f:
    content = f.read()

# Python (os.path):
import os

base_dir = os.path.realpath("/safe/directory")
user_path = os.path.realpath(os.path.join(base_dir, user_input))

if not user_path.startswith(base_dir):
    raise ValueError("Path traversal attempt detected")

# Node.js:
const path = require('path')
const baseDir = path.resolve('/safe/directory')
const userPath = path.resolve(baseDir, userInput)

if (!userPath.startsWith(baseDir)) {
    throw new Error('Path traversal attempt detected')
}
""",
            examples=[
                {
                    "before": "with open(user_path) as f:",
                    "after": """base_dir = Path("/safe/dir").resolve()
safe_path = (base_dir / user_path).resolve()
if not safe_path.is_relative_to(base_dir):
    raise ValueError("Invalid path")
with open(safe_path, encoding="utf-8") as f:""",
                    "language": "python",
                },
            ],
        )

    def _hardcoded_secrets_pattern(self) -> FixPattern:
        """Hardcoded Secrets fix pattern."""
        return FixPattern(
            cwe_id="CWE-798",
            name="Hardcoded Secrets",
            description="Use environment variables or secret management",
            vulnerable_pattern=r'(api_key|password|secret|token)\s*=\s*["\'][^"\']+["\']',
            fix_template="""
# Fix: Use environment variables or secret management
# Before: API_KEY = "sk-abc123..."
# After:  API_KEY = os.environ["API_KEY"]

# Python (environment variables):
import os

API_KEY = os.environ["API_KEY"]
# or with default (for non-sensitive values only):
API_KEY = os.environ.get("API_KEY", "")

# Python (python-dotenv):
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.environ["API_KEY"]

# Python (AWS Secrets Manager):
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='my-secret')

# Node.js:
const apiKey = process.env.API_KEY

# Node.js (dotenv):
require('dotenv').config()
const apiKey = process.env.API_KEY
""",
            examples=[
                {
                    "before": 'API_KEY = "sk-abc123xyz789"',
                    "after": 'API_KEY = os.environ["API_KEY"]',
                    "language": "python",
                },
                {
                    "before": 'const password = "supersecret123"',
                    "after": "const password = process.env.DB_PASSWORD",
                    "language": "javascript",
                },
            ],
        )

    def _weak_crypto_pattern(self) -> FixPattern:
        """Weak Cryptography fix pattern."""
        return FixPattern(
            cwe_id="CWE-327",
            name="Weak Cryptography",
            description="Use modern cryptographic algorithms",
            vulnerable_pattern=r"md5|sha1|des|rc4|blowfish",
            fix_template="""
# Fix: Use modern cryptographic algorithms
# Before: hashlib.md5(password)
# After:  bcrypt.hashpw(password, bcrypt.gensalt())

# Python (password hashing - use bcrypt/argon2):
import bcrypt
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
# Verify:
bcrypt.checkpw(password.encode(), hashed)

# Python (argon2 - preferred):
from argon2 import PasswordHasher
ph = PasswordHasher()
hashed = ph.hash(password)
# Verify:
ph.verify(hashed, password)

# Python (general hashing - use SHA-256+):
import hashlib
hash_value = hashlib.sha256(data).hexdigest()

# Python (encryption - use AES-256-GCM):
from cryptography.fernet import Fernet
key = Fernet.generate_key()
cipher = Fernet(key)
encrypted = cipher.encrypt(data)

# Node.js (password hashing):
const bcrypt = require('bcrypt')
const hash = await bcrypt.hash(password, 10)

# Node.js (encryption):
const crypto = require('crypto')
const cipher = crypto.createCipheriv('aes-256-gcm', key, iv)
""",
            examples=[
                {
                    "before": "hashlib.md5(password.encode()).hexdigest()",
                    "after": "bcrypt.hashpw(password.encode(), bcrypt.gensalt())",
                    "language": "python",
                },
                {
                    "before": "hashlib.sha1(data).hexdigest()",
                    "after": "hashlib.sha256(data).hexdigest()",
                    "language": "python",
                },
            ],
        )


# Global instance for convenience
DEFAULT_PATTERN_LIBRARY = FixPatternLibrary()
