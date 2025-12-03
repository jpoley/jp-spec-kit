"""OWASP Top 10 2021 definitions and CWE mappings.

This module provides the OWASP Top 10 categories with their
associated CWEs for compliance checking.
"""

from dataclasses import dataclass

from specify_cli.security.reporter.models import (
    OWASPCategory,
    ComplianceStatus,
)


@dataclass
class OWASPDefinition:
    """OWASP Top 10 category definition."""

    id: str
    name: str
    description: str
    cwes: list[str]


# OWASP Top 10 2021 with CWE mappings
OWASP_TOP_10: list[OWASPDefinition] = [
    OWASPDefinition(
        id="A01:2021",
        name="Broken Access Control",
        description="Restrictions on authenticated users not enforced",
        cwes=[
            "CWE-22",  # Path Traversal
            "CWE-23",  # Relative Path Traversal
            "CWE-35",  # Path Traversal
            "CWE-59",  # Improper Link Resolution
            "CWE-200",  # Exposure of Sensitive Information
            "CWE-201",  # Insertion of Sensitive Information Into Sent Data
            "CWE-219",  # Storage of File with Sensitive Data Under Web Root
            "CWE-264",  # Permissions, Privileges, and Access Controls
            "CWE-275",  # Permission Issues
            "CWE-276",  # Incorrect Default Permissions
            "CWE-284",  # Improper Access Control
            "CWE-285",  # Improper Authorization
            "CWE-352",  # Cross-Site Request Forgery (CSRF)
            "CWE-359",  # Exposure of Private Personal Information
            "CWE-377",  # Insecure Temporary File
            "CWE-402",  # Transmission of Private Resources into a New Sphere
            "CWE-425",  # Direct Request ('Forced Browsing')
            "CWE-441",  # Unintended Proxy or Intermediary
            "CWE-497",  # Exposure of Sensitive System Information
            "CWE-538",  # Insertion of Sensitive Information into Externally-Accessible File
            "CWE-540",  # Inclusion of Sensitive Information in Source Code
            "CWE-548",  # Exposure of Information Through Directory Listing
            "CWE-552",  # Files or Directories Accessible to External Parties
            "CWE-566",  # Authorization Bypass Through User-Controlled SQL Primary Key
            "CWE-601",  # URL Redirection to Untrusted Site
            "CWE-639",  # Authorization Bypass Through User-Controlled Key
            "CWE-651",  # Exposure of WSDL File
            "CWE-668",  # Exposure of Resource to Wrong Sphere
            "CWE-706",  # Use of Incorrectly-Resolved Name or Reference
            "CWE-862",  # Missing Authorization
            "CWE-863",  # Incorrect Authorization
            "CWE-913",  # Improper Control of Dynamically-Managed Code Resources
            "CWE-922",  # Insecure Storage of Sensitive Information
            "CWE-1275",  # Sensitive Cookie with Improper SameSite Attribute
        ],
    ),
    OWASPDefinition(
        id="A02:2021",
        name="Cryptographic Failures",
        description="Failures related to cryptography leading to exposure of sensitive data",
        cwes=[
            "CWE-261",  # Weak Encoding for Password
            "CWE-296",  # Improper Following of a Certificate's Chain of Trust
            "CWE-310",  # Cryptographic Issues
            "CWE-319",  # Cleartext Transmission of Sensitive Information
            "CWE-321",  # Use of Hard-coded Cryptographic Key
            "CWE-322",  # Key Exchange without Entity Authentication
            "CWE-323",  # Reusing a Nonce, Key Pair in Encryption
            "CWE-324",  # Use of a Key Past its Expiration Date
            "CWE-325",  # Missing Cryptographic Step
            "CWE-326",  # Inadequate Encryption Strength
            "CWE-327",  # Use of a Broken or Risky Cryptographic Algorithm
            "CWE-328",  # Use of Weak Hash
            "CWE-329",  # Generation of Predictable IV with CBC Mode
            "CWE-330",  # Use of Insufficiently Random Values
            "CWE-331",  # Insufficient Entropy
            "CWE-335",  # Incorrect Usage of Seeds in PRNG
            "CWE-336",  # Same Seed in PRNG
            "CWE-337",  # Predictable Seed in PRNG
            "CWE-338",  # Use of Cryptographically Weak PRNG
            "CWE-340",  # Generation of Predictable Numbers or Identifiers
            "CWE-347",  # Improper Verification of Cryptographic Signature
            "CWE-523",  # Unprotected Transport of Credentials
            "CWE-720",  # OWASP Top Ten 2007 Category A9 - Insecure Communications
            "CWE-757",  # Selection of Less-Secure Algorithm During Negotiation
            "CWE-759",  # Use of a One-Way Hash without a Salt
            "CWE-760",  # Use of a One-Way Hash with a Predictable Salt
            "CWE-780",  # Use of RSA Algorithm without OAEP
            "CWE-818",  # Insufficient Transport Layer Protection
            "CWE-916",  # Use of Password Hash With Insufficient Computational Effort
        ],
    ),
    OWASPDefinition(
        id="A03:2021",
        name="Injection",
        description="User-supplied data not validated, filtered, or sanitized",
        cwes=[
            "CWE-20",  # Improper Input Validation
            "CWE-74",  # Improper Neutralization of Special Elements in Output
            "CWE-75",  # Failure to Sanitize Special Elements
            "CWE-77",  # Command Injection
            "CWE-78",  # OS Command Injection
            "CWE-79",  # Cross-site Scripting (XSS)
            "CWE-80",  # Improper Neutralization of Script-Related HTML Tags
            "CWE-83",  # Improper Neutralization of Script in Attributes
            "CWE-87",  # Improper Neutralization of Alternate XSS Syntax
            "CWE-88",  # Improper Neutralization of Argument Delimiters
            "CWE-89",  # SQL Injection
            "CWE-90",  # LDAP Injection
            "CWE-91",  # XML Injection
            "CWE-93",  # Improper Neutralization of CRLF Sequences
            "CWE-94",  # Improper Control of Generation of Code
            "CWE-95",  # Improper Neutralization of Directives in Dynamically Evaluated Code
            "CWE-96",  # Improper Neutralization of Directives in Statically Saved Code
            "CWE-97",  # Improper Neutralization of Server-Side Includes
            "CWE-98",  # PHP Remote File Inclusion
            "CWE-99",  # Improper Control of Resource Identifiers
            "CWE-113",  # HTTP Response Splitting
            "CWE-116",  # Improper Encoding or Escaping of Output
            "CWE-138",  # Improper Neutralization of Special Elements
            "CWE-184",  # Incomplete List of Disallowed Inputs
            "CWE-470",  # Use of Externally-Controlled Input to Select Classes or Code
            "CWE-471",  # Modification of Assumed-Immutable Data (MAID)
            "CWE-564",  # SQL Injection: Hibernate
            "CWE-610",  # Externally Controlled Reference to a Resource in Another Sphere
            "CWE-643",  # Improper Neutralization of Data within XPath Expressions
            "CWE-644",  # Improper Neutralization of HTTP Headers for Scripting Syntax
            "CWE-652",  # Improper Neutralization of Data within XQuery Expressions
            "CWE-917",  # Improper Neutralization of Special Elements used in an Expression Language Statement
        ],
    ),
    OWASPDefinition(
        id="A04:2021",
        name="Insecure Design",
        description="Missing or ineffective control design",
        cwes=[
            "CWE-73",  # External Control of File Name or Path
            "CWE-183",  # Permissive List of Allowed Inputs
            "CWE-209",  # Generation of Error Message Containing Sensitive Information
            "CWE-213",  # Exposure of Sensitive Information Due to Incompatible Policies
            "CWE-235",  # Improper Handling of Extra Parameters
            "CWE-256",  # Plaintext Storage of a Password
            "CWE-257",  # Storing Passwords in a Recoverable Format
            "CWE-266",  # Incorrect Privilege Assignment
            "CWE-269",  # Improper Privilege Management
            "CWE-280",  # Improper Handling of Insufficient Permissions or Privileges
            "CWE-311",  # Missing Encryption of Sensitive Data
            "CWE-312",  # Cleartext Storage of Sensitive Information
            "CWE-313",  # Cleartext Storage in a File or on Disk
            "CWE-316",  # Cleartext Storage of Sensitive Information in Memory
            "CWE-419",  # Unprotected Primary Channel
            "CWE-430",  # Deployment of Wrong Handler
            "CWE-434",  # Unrestricted Upload of File with Dangerous Type
            "CWE-444",  # Inconsistent Interpretation of HTTP Requests
            "CWE-451",  # User Interface (UI) Misrepresentation of Critical Information
            "CWE-472",  # External Control of Assumed-Immutable Web Parameter
            "CWE-501",  # Trust Boundary Violation
            "CWE-522",  # Insufficiently Protected Credentials
            "CWE-525",  # Use of Web Browser Cache Containing Sensitive Information
            "CWE-539",  # Use of Persistent Cookies Containing Sensitive Information
            "CWE-579",  # J2EE Bad Practices: Non-serializable Object Stored in Session
            "CWE-598",  # Use of GET Request Method With Sensitive Query Strings
            "CWE-602",  # Client-Side Enforcement of Server-Side Security
            "CWE-642",  # External Control of Critical State Data
            "CWE-646",  # Reliance on File Name or Extension of Externally-Supplied File
            "CWE-650",  # Trusting HTTP Permission Methods on the Server Side
            "CWE-653",  # Improper Isolation or Compartmentalization
            "CWE-656",  # Reliance on Security Through Obscurity
            "CWE-657",  # Violation of Secure Design Principles
            "CWE-799",  # Improper Control of Interaction Frequency
            "CWE-807",  # Reliance on Untrusted Inputs in a Security Decision
            "CWE-840",  # Business Logic Errors
            "CWE-841",  # Improper Enforcement of Behavioral Workflow
            "CWE-927",  # Use of Implicit Intent for Sensitive Communication
            "CWE-1021",  # Improper Restriction of Rendered UI Layers or Frames
            "CWE-1173",  # Improper Use of Validation Framework
        ],
    ),
    OWASPDefinition(
        id="A05:2021",
        name="Security Misconfiguration",
        description="Missing appropriate security hardening",
        cwes=[
            "CWE-2",  # 7PK - Environment
            "CWE-11",  # ASP.NET Misconfiguration: Creating Debug Binary
            "CWE-13",  # ASP.NET Misconfiguration: Password in Configuration File
            "CWE-15",  # External Control of System or Configuration Setting
            "CWE-16",  # Configuration
            "CWE-260",  # Password in Configuration File
            "CWE-315",  # Cleartext Storage of Sensitive Information in a Cookie
            "CWE-520",  # .NET Misconfiguration: Use of Impersonation
            "CWE-526",  # Cleartext Storage of Sensitive Information in an Environment Variable
            "CWE-537",  # Java Runtime Error Message Containing Sensitive Information
            "CWE-541",  # Inclusion of Sensitive Information in an Include File
            "CWE-547",  # Use of Hard-coded, Security-relevant Constants
            "CWE-611",  # Improper Restriction of XML External Entity Reference
            "CWE-614",  # Sensitive Cookie in HTTPS Session Without 'Secure' Attribute
            "CWE-756",  # Missing Custom Error Page
            "CWE-776",  # Improper Restriction of Recursive Entity References in DTDs
            "CWE-942",  # Permissive Cross-domain Policy with Untrusted Domains
            "CWE-1004",  # Sensitive Cookie Without 'HttpOnly' Flag
            "CWE-1032",  # OWASP Top Ten 2017 Category A6 - Security Misconfiguration
            "CWE-1174",  # ASP.NET Misconfiguration: Improper Model Validation
        ],
    ),
    OWASPDefinition(
        id="A06:2021",
        name="Vulnerable and Outdated Components",
        description="Using components with known vulnerabilities",
        cwes=[
            "CWE-1035",  # OWASP Top Ten 2017 Category A9 - Using Components with Known Vulnerabilities
            "CWE-1104",  # Use of Unmaintained Third Party Components
        ],
    ),
    OWASPDefinition(
        id="A07:2021",
        name="Identification and Authentication Failures",
        description="Broken authentication mechanisms",
        cwes=[
            "CWE-255",  # Credentials Management Errors
            "CWE-259",  # Use of Hard-coded Password
            "CWE-287",  # Improper Authentication
            "CWE-288",  # Authentication Bypass Using an Alternate Path or Channel
            "CWE-290",  # Authentication Bypass by Spoofing
            "CWE-294",  # Authentication Bypass by Capture-replay
            "CWE-295",  # Improper Certificate Validation
            "CWE-297",  # Improper Validation of Certificate with Host Mismatch
            "CWE-300",  # Channel Accessible by Non-Endpoint
            "CWE-302",  # Authentication Bypass by Assumed-Immutable Data
            "CWE-304",  # Missing Critical Step in Authentication
            "CWE-306",  # Missing Authentication for Critical Function
            "CWE-307",  # Improper Restriction of Excessive Authentication Attempts
            "CWE-346",  # Origin Validation Error
            "CWE-384",  # Session Fixation
            "CWE-521",  # Weak Password Requirements
            "CWE-613",  # Insufficient Session Expiration
            "CWE-620",  # Unverified Password Change
            "CWE-640",  # Weak Password Recovery Mechanism for Forgotten Password
            "CWE-798",  # Use of Hard-coded Credentials
            "CWE-940",  # Improper Verification of Source of a Communication Channel
            "CWE-1216",  # Lockout Mechanism Errors
        ],
    ),
    OWASPDefinition(
        id="A08:2021",
        name="Software and Data Integrity Failures",
        description="Code and infrastructure that does not protect against integrity violations",
        cwes=[
            "CWE-345",  # Insufficient Verification of Data Authenticity
            "CWE-353",  # Missing Support for Integrity Check
            "CWE-426",  # Untrusted Search Path
            "CWE-494",  # Download of Code Without Integrity Check
            "CWE-502",  # Deserialization of Untrusted Data
            "CWE-565",  # Reliance on Cookies without Validation and Integrity Checking
            "CWE-784",  # Reliance on Cookies without Validation and Integrity Checking in a Security Decision
            "CWE-829",  # Inclusion of Functionality from Untrusted Control Sphere
            "CWE-830",  # Inclusion of Web Functionality from an Untrusted Source
            "CWE-915",  # Improperly Controlled Modification of Dynamically-Determined Object Attributes
        ],
    ),
    OWASPDefinition(
        id="A09:2021",
        name="Security Logging and Monitoring Failures",
        description="Insufficient logging and monitoring",
        cwes=[
            "CWE-117",  # Improper Output Neutralization for Logs
            "CWE-223",  # Omission of Security-relevant Information
            "CWE-532",  # Insertion of Sensitive Information into Log File
            "CWE-778",  # Insufficient Logging
        ],
    ),
    OWASPDefinition(
        id="A10:2021",
        name="Server-Side Request Forgery (SSRF)",
        description="Fetching a remote resource without validating the user-supplied URL",
        cwes=[
            "CWE-918",  # Server-Side Request Forgery (SSRF)
        ],
    ),
]


def get_owasp_category(cwe_id: str) -> OWASPDefinition | None:
    """Get OWASP category for a CWE."""
    for category in OWASP_TOP_10:
        if cwe_id in category.cwes:
            return category
    return None


def check_owasp_compliance(
    findings: list, triage_results: list | None = None
) -> list[OWASPCategory]:
    """Check OWASP Top 10 compliance based on findings.

    Args:
        findings: List of security findings.
        triage_results: Optional triage results for filtering FPs.

    Returns:
        List of OWASPCategory with compliance status.
    """
    # Build triage lookup
    triage_map = {}
    if triage_results:
        for result in triage_results:
            triage_map[result.finding_id] = result

    results = []

    for definition in OWASP_TOP_10:
        # Count findings for this OWASP category
        category_findings = []
        for finding in findings:
            if finding.cwe_id in definition.cwes:
                # Skip false positives if triage available
                triage = triage_map.get(finding.id)
                if triage and triage.classification.value == "FP":
                    continue
                category_findings.append(finding)

        finding_count = len(category_findings)
        critical_count = sum(
            1 for f in category_findings if f.severity.value == "critical"
        )

        # Determine compliance status
        if finding_count == 0:
            status = ComplianceStatus.COMPLIANT
        elif critical_count > 0:
            status = ComplianceStatus.NON_COMPLIANT
        else:
            status = ComplianceStatus.PARTIAL

        results.append(
            OWASPCategory(
                id=definition.id,
                name=definition.name,
                status=status,
                finding_count=finding_count,
                critical_count=critical_count,
                cwes=definition.cwes,
            )
        )

    return results
