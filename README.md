# ✅ **README.md**

# Direct SMTP RCPT Tester for Microsoft 365
A FastAPI micro-service that performs a direct SMTP handshake against Microsoft 365’s `*.mail.protection.outlook.com` infrastructure to determine whether inbound mail can bypass published MX records.

This allows security teams, email admins, and consultants to quickly verify if a Microsoft 365 tenant is properly locked down to reject unsolicited direct SMTP delivery.



## ✅ What This Tool Does
✔ Resolves MX records for a target domain  
✔ Detects if MX points to Microsoft 365  
✔ Optionally skips the test when Microsoft 365 MX is detected (default)  
✔ Performs a full SMTP handshake:
- `220` banner detection  
- `EHLO`  
- `MAIL FROM:<postmaster@ehlo.email>`  
- `RCPT TO:<postmaster@target-domain>`  
✔ Returns detailed transcript of every server response  
✔ Reports whether Microsoft 365 **ACCEPTS** or **REJECTS** direct delivery

> ✅ **If Microsoft 365 rejects RCPT → tenant is secure (MX-bypass blocked)**  
> ❌ **If Microsoft 365 accepts RCPT → tenant may be vulnerable to MX-bypass**



## ✅ Example Output (Secure Tenant)

```json
{
  "host": "example-org.mail.protection.outlook.com",
  "domain": "example.org",
  "rcpt_accepted": false,
  "results": [
    "S: 220 ...",
    "C: EHLO ...",
    "S: 250 ...",
    "C: MAIL FROM:<postmaster@ehlo.email>",
    "S: 250 2.1.0 Sender OK",
    "C: RCPT TO:<postmaster@example.org>",
    "S: 550 5.7.51 TenantInboundAttribution; Rejecting...",
    "C: QUIT",
    "S: 221 2.0.0 Service closing transmission channel"
  ]
}
````



## ✅ Example Output (Unsecure Tenant)

```json
{
  "host": "example-com.mail.protection.outlook.com",
  "domain": "example.com",
  "rcpt_accepted": true,
  "results": [
    "S: 220 ...",
    "C: EHLO ...",
    "S: 250 ...",
    "C: MAIL FROM:<postmaster@ehlo.email>",
    "S: 250 Sender OK",
    "C: RCPT TO:<postmaster@example.com>",
    "S: 250 Recipient OK",
    "C: QUIT",
    "S: 221 Service closing transmission channel"
  ]
}
```



## ✅ API Endpoints

### `POST /checkSmtp`

```json
{
  "domain": "example.com"
}
```

### `GET /checkSmtp?domain=example.com`

Returns JSON with:

* SMTP host used
* Whether RCPT was accepted
* Full SMTP transcript
* Skipped notice when Microsoft MX detected



## ✅ Skipping Logic (MX Detection)

If the domain’s lowest-preference MX record ends in `mail.protection.outlook.com`, the service assumes Microsoft 365 hosting and **skips** the test by default for performance and expected outcome:

```json
{
  "domain": "example.com",
  "skipped": true,
  "reason": "Domain uses Microsoft 365 MX; direct RCPT will always accept on hosted tenancy (forceCheck=1 to override)"
}
```

Force override:

```
/checkSmtp?domain=example.com&forceCheck=1
```



## ✅ Docker

### Pull and run:

```bash
docker run -it -p 8000:8000 ghcr.io/smck83/test-direct-smtp-relay
```

### Docker Compose:

```yaml
version: "3.8"
services:
  smtp-checker:
    image: ghcr.io/smck83/test-direct-smtp-relay:latest
    container_name: smtp-checker
    ports:
      - "8000:8000"
    restart: unless-stopped
```



## ✅ Intended Use Cases

✔ Validate Microsoft 365 tenant inbound connector security
✔ MSP / MSSP audit tool
✔ Email security assessments
✔ Demonstrate MX-bypass attack paths
✔ Confirm if a tenant rejects unauthorized direct SMTP inbound mail


## ✅ Security Notes

* No email content is sent — only envelope handshake (`MAIL FROM`, `RCPT TO`)
* All SMTP tests use `postmaster@<domain>` as recipient
* Safe for internal audit or customer assessment

---

## ✅ License

MIT

## ✅ Author

Created by **smck83** to help security teams validate Microsoft 365 tenant hardening and prevent MX-bypass attacks.

```

