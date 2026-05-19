# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| 0.1.x | Yes |

## Reporting a Vulnerability

If you discover a vulnerability in HIEM, please open a private security advisory
at https://github.com/BoozeLee/hiem/security/advisories.

Do **not** open a public issue for vulnerabilities.

## Security Principles

1. **No secrets in output.** Tokens are redacted as `***REDACTED***` before any log
   or stdout write, using `hiem.redact`.
2. **No `shell=True`.** Every subprocess call uses a list of arguments.
3. **No hardcoded credentials.** No PEM files, PATs, or API keys in the repo.
4. **Timeouts on all network calls.** No hanging processes.
5. **Structured exit codes.**
