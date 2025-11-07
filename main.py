from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import socket
import dns.resolver

app = FastAPI()

class DomainRequest(BaseModel):
    domain: str
    forceCheck: int | None = 0

SMTP_TIMEOUT = 10
MAIL_FROM = "postmaster@ehlo.email"


def get_lowest_mx(domain: str):
    """Return (preference, hostname) of lowest MX, or None if no MX."""
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        records = sorted([(r.preference, str(r.exchange).rstrip(".")) for r in answers])
        return records[0]  # lowest preference MX
    except Exception:
        return None


def smtp_check(domain: str):
    results = []
    hyphenated = domain.replace(".", "-")
    host = f"{hyphenated}.mail.protection.outlook.com"
    rcpt_to = f"postmaster@{domain}"

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(SMTP_TIMEOUT)
        s.connect((host, 25))

        def recv():
            data = s.recv(4096).decode(errors='ignore').strip()
            results.append(f"S: {data}")
            return data

        def send(cmd):
            s.send((cmd + "\r\n").encode())
            results.append(f"C: {cmd}")
            return recv()

        banner = recv()
        if not banner.startswith("220"):
            return {"host": host, "success": False, "results": results}

        resp = send(f"EHLO {domain}")
        if not resp.startswith("250"):
            return {"host": host, "success": False, "error": "EHLO failed", "results": results}

        resp = send(f"MAIL FROM:<{MAIL_FROM}>")
        if not resp.startswith("250"):
            return {"host": host, "success": False, "error": "MAIL FROM rejected", "results": results}

        resp = send(f"RCPT TO:<{rcpt_to}>")
        rcpt_ok = resp.startswith("250")

        try:
            send("QUIT")
        except:
            pass

        return {
            "host": host,
            "domain": domain,
            "rcpt_accepted": rcpt_ok,
            "results": results,
        }

    except socket.timeout:
        return {"host": host, "success": False, "error": "SMTP timeout", "results": results}
    except Exception as e:
        return {"host": host, "success": False, "error": str(e), "results": results}
    finally:
        try:
            s.close()
        except:
            pass


def should_skip(domain: str, forceCheck: int):
    # No forceCheck — evaluate MX
    if forceCheck == 1:
        return False  # always check

    mx = get_lowest_mx(domain)

    if mx is None:
        return False  # No MX, must test

    (_, mx_host) = mx

    if mx_host.endswith("outlook.com") or mx_host.endswith("outlook.com."):
        return True

    return False


@app.post("/checkSmtp")
def check_smtp_post(request: DomainRequest):
    if "." not in request.domain:
        raise HTTPException(status_code=400, detail="Invalid domain provided")

    if should_skip(request.domain, request.forceCheck):
        return {
            "domain": request.domain,
            "skipped": True,
            "reason": "Domain uses Microsoft 365 MX; RCPT should always accept on hosted tenancy (forceCheck=1 to override)"
        }

    return smtp_check(request.domain)


@app.get("/checkSmtp")
def check_smtp_get(
    domain: str = Query(...),
    forceCheck: int | None = Query(0)
):
    if "." not in domain:
        raise HTTPException(status_code=400, detail="Invalid domain provided")

    if should_skip(domain, forceCheck):
        return {
            "domain": domain,
            "skipped": True,
            "reason": "Domain uses Microsoft 365 MX; RCPT should always accept on hosted tenancy (forceCheck=1 to override)"
        }

    return smtp_check(domain)
