"""
Static mapping from tasks to OWASP Top 10 (2021) and CWE IDs.
Import this mapping wherever you want to annotate tables/plots.
"""
OWASP_CWE_MAP = {
    "task01_sql": {
        "owasp": ["A03:2021 Injection"],
        "cwe": ["CWE-89"],
    },
    "task02_password": {
        "owasp": ["A02:2021 Cryptographic Failures"],
        "cwe": ["CWE-256", "CWE-759"],
    },
    "task03_upload": {
        "owasp": ["A01:2021 Broken Access Control", "A05:2021 Security Misconfiguration"],
        "cwe": ["CWE-434", "CWE-22"],
    },
    "task04_command": {
        "owasp": ["A03:2021 Injection"],
        "cwe": ["CWE-78"],
    },
    "task05_jwt": {
        "owasp": ["A07:2021 Identification and Authentication Failures"],
        "cwe": ["CWE-287", "CWE-347"],
    },
    "task06_logging": {
        "owasp": ["A09:2021 Security Logging and Monitoring Failures"],
        "cwe": ["CWE-532"],
    },
    "task07_path": {
        "owasp": ["A01:2021 Broken Access Control"],
        "cwe": ["CWE-22"],
    },
    "task08_unpickle": {
        "owasp": ["A08:2021 Software and Data Integrity Failures"],
        "cwe": ["CWE-502"],
    },
    "task09_email": {
        "owasp": ["A04:2021 Insecure Design", "A05:2021 Security Misconfiguration"],
        "cwe": ["CWE-20"],
    },
    "task10_secrets": {
        "owasp": ["A02:2021 Cryptographic Failures"],
        "cwe": ["CWE-798", "CWE-321"],
    },
}
