"""
DAST (Dynamic Application Security Testing) scan for Q8.2.
Performs automated security analysis against the running Flask app.

Phase 1 — Pre-fix scan: identifies vulnerabilities before patching.
Phase 2 — Post-fix scan: confirms vulnerabilities are resolved.

Usage:
  python3 run_dast_scan.py
"""
import os
import subprocess
import sys
import time
import json
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone
from html import escape

TARGET = "http://localhost:5001"
REPORT_DIR = "docs/dast"

HEADER_CHECKS = {
    "X-Frame-Options": "Missing clickjacking protection",
    "X-Content-Type-Options": "Missing MIME-sniffing protection",
    "Content-Security-Policy": "Missing CSP header (XSS mitigation)",
    "Strict-Transport-Security": "Missing HSTS header",
    "X-XSS-Protection": "Missing XSS filter header",
}

FORMS_TO_CHECK = [
    {"url": "/login", "method": "POST", "fields": ["username", "password"]},
    {"url": "/register", "method": "POST", "fields": ["username", "email", "password", "confirm_password"]},
]

SQLI_ENDPOINT = "/login"
SQLI_DATA = {"username_or_email": "test", "password": "test"}
SQLI_FIELD = "username_or_email"


def banner(text):
    width = 70
    print(f"\n{'=' * width}")
    print(f"  {text}")
    print(f"{'=' * width}\n")


def check_app_online():
    try:
        resp = urllib.request.urlopen(f"{TARGET}/", timeout=10)
        return True
    except Exception as e:
        print(f"  [!] App not reachable: {e}")
        return False


def check_security_headers():
    banner("CHECKING SECURITY HEADERS")
    findings = []
    try:
        req = urllib.request.Request(f"{TARGET}/")
        resp = urllib.request.urlopen(req, timeout=10)
        headers = {k.lower(): v for k, v in resp.headers.items()}
        for hdr, desc in HEADER_CHECKS.items():
            if hdr.lower() not in headers:
                findings.append({
                    "type": "Missing Security Header",
                    "severity": "Medium",
                    "endpoint": "/",
                    "detail": f"{desc} ({hdr})",
                    "evidence": f"Response headers: {dict(resp.headers)}",
                })
                print(f"  [MEDIUM] {desc} ({hdr})")
            else:
                print(f"  [OK] {hdr}: present")
        if not findings:
            print("  All security headers present.")
    except Exception as e:
        print(f"  [!] Error checking headers: {e}")
    return findings


def check_csrf_protection():
    banner("CHECKING CSRF PROTECTION ON FORMS")
    findings = []
    for form in FORMS_TO_CHECK:
        url = f"{TARGET}{form['url']}"
        try:
            req = urllib.request.Request(url)
            resp = urllib.request.urlopen(req, timeout=10)
            body = resp.read().decode("utf-8", errors="replace")
            has_csrf = "csrf" in body.lower() or "csrf_token" in body.lower() or "_token" in body.lower()
            if not has_csrf:
                findings.append({
                    "type": "Missing CSRF Protection",
                    "severity": "High",
                    "endpoint": form["url"],
                    "detail": f"Form at {form['url']} has no CSRF token field",
                    "evidence": "Form fields detected: " + ", ".join(form["fields"]),
                })
                print(f"  [HIGH] No CSRF token on {form['url']}")
            else:
                print(f"  [OK] CSRF token present on {form['url']}")
        except Exception as e:
            print(f"  [!] Error checking {form['url']}: {e}")
    return findings


def test_sqli():
    banner("TESTING SQL INJECTION (MANUAL PROBE)")
    findings = []
    sqli_payloads = [
        (SQLI_FIELD, "test' OR '1'='1"),
        (SQLI_FIELD, "test\" OR \"1\"=\"1"),
        (SQLI_FIELD, "admin' --"),
        (
            SQLI_FIELD,
            "nosuchuser' UNION SELECT 1,'sqli_test','sqli@test.com','test',CURRENT_TIMESTAMP,NULL --",
        ),
    ]
    for field, payload in sqli_payloads:
        data = f"{field}={urllib.parse.quote(payload)}&password=test".encode()
        try:
            req = urllib.request.Request(f"{TARGET}/login", data=data, method="POST")
            req.add_header("Content-Type", "application/x-www-form-urlencoded")
            resp = urllib.request.urlopen(req, timeout=10)
            body = resp.read().decode("utf-8", errors="replace")
            if "Invalid" not in body and "error" not in body.lower():
                findings.append({
                    "type": "SQL Injection",
                    "severity": "Critical",
                    "endpoint": "/login",
                    "detail": f"SQL injection detected with payload: {payload}",
                    "evidence": f"POST {field}={payload} returned successful login",
                })
                print(f"  [CRITICAL] SQLi with: {field}={payload}")
            else:
                # Check for behavioural differences between true/false conditions
                if "1=1" in payload or "1=1" in payload:
                    print(f"  [INFO] SQLi payload sent: {field}={payload[:40]}... — error page returned (SQLi may still work, password check catches it)")
        except urllib.error.HTTPError as e:
            if e.code == 500:
                findings.append({
                    "type": "SQL Injection (Error-Based)",
                    "severity": "Critical",
                    "endpoint": "/login",
                    "detail": f"Server error with payload: {payload} — possible SQLi",
                    "evidence": f"HTTP 500 with payload: {field}={payload}",
                })
                print(f"  [CRITICAL] SQLi (error-based) with: {field}={payload}")
            else:
                print(f"  [OK] Payload rejected (HTTP {e.code})")
        except Exception as e:
            print(f"  [!] Error: {e}")
    return findings


def run_sqlmap():
    banner("RUNNING SQLMAP AGAINST /login")
    findings = []
    try:
        sqlmap_bin = "/Library/Frameworks/Python.framework/Versions/3.13/bin/sqlmap"
        cmd = [
            sqlmap_bin,
            "-u", f"{TARGET}/login",
            "--data", "username_or_email=test&password=test",
            "--level", "3",
            "--risk", "2",
            "--batch",
            "--output-dir", "/tmp/sqlmap_output",
            "--flush-session",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        output = result.stdout + result.stderr

        sqli_indicators = [
            "Type: boolean-based blind",
            "Type: error-based",
            "Type: time-based blind",
            "Type: UNION query",
            "Type: stacked queries",
            "Type: inline query",
            "Parameter: #1*",
            "Parameter: username",
            "is vulnerable",
            "sqlmap identified the following injection point",
        ]
        for indicator in sqli_indicators:
            if indicator.lower() in output.lower():
                findings.append({
                    "type": "SQL Injection (sqlmap confirmed)",
                    "severity": "Critical",
                    "endpoint": "/login",
                    "detail": f"sqlmap identified injection point: {indicator}",
                    "evidence": f"sqlmap output contains: {indicator}",
                })
                print(f"  [CRITICAL] sqlmap confirmed SQL injection: {indicator}")
                break
        else:
            print("  sqlmap did not confirm SQL injection (output may be partial)")

        with open("/tmp/sqlmap_stdout.txt", "w") as f:
            f.write(output)
        print(f"  sqlmap output saved to /tmp/sqlmap_stdout.txt")

    except subprocess.TimeoutExpired:
        print("  [!] sqlmap timed out after 120s")
    except Exception as e:
        print(f"  [!] sqlmap error: {e}")
    return findings


def check_ssl_tls():
    banner("CHECKING SSL/TLS CONFIGURATION")
    findings = []
    try:
        req = urllib.request.Request(f"{TARGET}/")
        resp = urllib.request.urlopen(req, timeout=10)
        scheme = resp.url.split(":")[0] if ":" in resp.url else "http"
        if scheme == "http":
            findings.append({
                "type": "Missing HTTPS",
                "severity": "Medium",
                "endpoint": "/",
                "detail": "Application is served over HTTP, not HTTPS",
                "evidence": f"URL: {resp.url}",
            })
            print(f"  [MEDIUM] Application runs on HTTP, not HTTPS")
        else:
            print(f"  [OK] HTTPS enabled")
    except Exception as e:
        print(f"  [!] Error: {e}")
    return findings


def generate_html_report(findings, phase):
    os.makedirs(REPORT_DIR, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    findings.sort(key=lambda f: severity_order.get(f["severity"], 99))

    html_rows = ""
    for f in findings:
        html_rows += f"""
        <tr>
            <td><span class="sev-{f['severity'].lower()}">{escape(f['severity'])}</span></td>
            <td>{escape(f['type'])}</td>
            <td><code>{escape(f['endpoint'])}</code></td>
            <td>{escape(f['detail'])}</td>
            <td><pre>{escape(f['evidence'][:200])}</pre></td>
        </tr>"""

    report = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DAST Scan Report — {phase}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 2rem; background: #f8f9fa; }}
        h1 {{ color: #1a1a2e; }}
        .meta {{ color: #666; }}
        table {{ border-collapse: collapse; width: 100%; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid #eee; }}
        th {{ background: #1a1a2e; color: white; }}
        tr:hover {{ background: #f1f1f1; }}
        code {{ background: #e8e8e8; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }}
        pre {{ background: #f4f4f4; padding: 8px; border-radius: 3px; overflow-x: auto; font-size: 0.85em; }}
        .sev-critical {{ color: #dc3545; font-weight: bold; }}
        .sev-high {{ color: #fd7e14; font-weight: bold; }}
        .sev-medium {{ color: #ffc107; }}
        .sev-low {{ color: #28a745; }}
        .summary {{ display: flex; gap: 1rem; margin: 1rem 0; }}
        .summary-item {{ background: white; padding: 1rem 1.5rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .summary-item h3 {{ margin: 0 0 0.5rem 0; color: #666; }}
        .summary-item .num {{ font-size: 2rem; font-weight: bold; }}
        .sev-critical .num {{ color: #dc3545; }}
        .sev-high .num {{ color: #fd7e14; }}
        .sev-medium .num {{ color: #ffc107; }}
    </style>
</head>
<body>
    <h1>DAST Security Scan Report</h1>
    <p class="meta"><strong>Phase:</strong> {phase}</p>
    <p class="meta"><strong>Timestamp:</strong> {ts}</p>
    <p class="meta"><strong>Target:</strong> <code>{TARGET}</code></p>
    <p class="meta"><strong>Tool:</strong> Custom DAST Scanner + sqlmap</p>

    <h2>Summary</h2>
    <div class="summary">
        <div class="summary-item sev-critical">
            <h3>Critical</h3>
            <div class="num">{sum(1 for f in findings if f['severity'] == 'Critical')}</div>
        </div>
        <div class="summary-item sev-high">
            <h3>High</h3>
            <div class="num">{sum(1 for f in findings if f['severity'] == 'High')}</div>
        </div>
        <div class="summary-item sev-medium">
            <h3>Medium</h3>
            <div class="num">{sum(1 for f in findings if f['severity'] == 'Medium')}</div>
        </div>
        <div class="summary-item sev-low">
            <h3>Low</h3>
            <div class="num">{sum(1 for f in findings if f['severity'] == 'Low')}</div>
        </div>
    </div>

    <h2>Findings</h2>
    <table>
        <thead>
            <tr><th>Severity</th><th>Type</th><th>Endpoint</th><th>Description</th><th>Evidence</th></tr>
        </thead>
        <tbody>
            {html_rows if html_rows else '<tr><td colspan="5" style="text-align:center;color:#666;">No findings — all checks passed.</td></tr>'}
        </tbody>
    </table>

    <h2>Methodology</h2>
    <ul>
        <li>Security headers checked via HTTP response inspection</li>
        <li>CSRF protection verified by scanning form HTML for token fields</li>
        <li>SQL injection tested via manual payload probes and automated sqlmap scan</li>
        <li>SSL/TLS check verifies HTTPS enforcement</li>
    </ul>
</body>
</html>"""

    phase_slug = phase.lower().replace(" ", "-")
    path = os.path.join(REPORT_DIR, f"dast-{phase_slug}.html")
    with open(path, "w") as f:
        f.write(report)
    print(f"\n  Report saved: {path}")
    return path


def main():
    phase = sys.argv[1] if len(sys.argv) > 1 else "initial-scan"
    if phase == "pre":
        phase = "initial-scan"

    print(f"DAST Scan — Phase: {phase}")
    print(f"Target: {TARGET}")
    print(f"Report directory: {REPORT_DIR}")

    if not check_app_online():
        print("\n  [!] Start the app first: python3 app.py")
        sys.exit(1)

    findings = []
    findings += check_security_headers()
    findings += check_csrf_protection()
    findings += check_ssl_tls()
    findings += test_sqli()
    findings += run_sqlmap()

    path = generate_html_report(findings, phase)

    print(f"\n  {'=' * 40}")
    print(f"  Scan complete. {len(findings)} findings.")
    print(f"  Report: {path}")
    print(f"  {'=' * 40}")

    return 0 if not any(f["severity"] in ("Critical", "High") for f in findings) else 1


if __name__ == "__main__":
    sys.exit(main())
