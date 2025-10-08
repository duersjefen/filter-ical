# Security Audit: Authentication System (2025-01-10)

## Executive Summary

A user authentication system was partially implemented on another laptop and pulled into the codebase. This audit identifies **critical security vulnerabilities** and **incomplete implementations** that must be addressed before production deployment.

**Status:** ⚠️ **NOT PRODUCTION-READY** - Multiple critical issues identified

---

## 🔴 CRITICAL SECURITY VULNERABILITIES

### 1. **CRITICALLY WEAK PASSWORD REQUIREMENTS**
**Severity:** 🔴 CRITICAL
**Location:** `backend/app/services/auth_service.py:248-269`

```python
# Current implementation - TOO WEAK
if len(password) < 4:  # ❌ Only 4 characters!
    return False, "Password must be at least 4 characters"
```

**Issues:**
- Minimum 4 characters (industry standard: 8-12 minimum)
- No complexity requirements (uppercase, numbers, symbols)
- No common password checking
- Vulnerable to brute force attacks

**Fix Required:**
```python
def is_valid_password(password: str) -> Tuple[bool, str]:
    """Validate password strength with industry standards."""
    if not password:
        return True, ""  # Password is optional

    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    if len(password) > 128:  # NIST recommendation
        return False, "Password too long (max 128 characters)"

    # Require at least 3 of 4: uppercase, lowercase, numbers, symbols
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(not c.isalnum() for c in password)

    complexity_score = sum([has_upper, has_lower, has_digit, has_symbol])
    if complexity_score < 3:
        return False, "Password must contain at least 3 of: uppercase, lowercase, numbers, symbols"

    # Check against common passwords (add library)
    # from password_strength import PasswordPolicy

    return True, ""
```

---

### 2. **NO RATE LIMITING ON AUTHENTICATION ENDPOINTS**
**Severity:** 🔴 CRITICAL
**Location:** All authentication endpoints

**Issues:**
- Login endpoint (`/api/users/login`) has NO rate limiting
- Password reset request (`/api/auth/request-reset`) has NO rate limiting
- Admin login (`/api/admin/login`) has NO rate limiting
- Vulnerable to:
  - Brute force password attacks
  - Credential stuffing
  - Email enumeration via password reset
  - DDoS attacks

**Fix Required:**
Install and configure `slowapi`:
```python
# requirements.txt
slowapi==0.1.9

# app/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# app/routers/users.py
@router.post("/api/users/login")
@limiter.limit("5/minute")  # 5 attempts per minute per IP
async def login_user(...):
    ...

@router.post("/api/auth/request-reset")
@limiter.limit("3/hour")  # 3 reset requests per hour
async def request_password_reset(...):
    ...
```

---

### 3. **USERNAME-ONLY AUTH IS FUNDAMENTALLY INSECURE**
**Severity:** 🔴 CRITICAL
**Location:** `backend/app/routers/users.py:193-195`, `backend/app/models/user.py:26-27`

**Issue:**
```python
# Anyone can access username-only accounts without password!
else:
    # Username-only account - no password check needed
    pass
```

This design allows **ANY person who knows a username** to access that account. This violates basic security principles.

**Impact:**
- Account takeover trivial (just guess usernames)
- No privacy for "username-only" users
- Data leakage
- Reputation damage

**Fix Required:**
```python
# REMOVE username-only authentication entirely
# OR require email verification for username-only accounts
# OR clearly warn users: "This account has NO security - anyone with your username can access it"
```

**Recommendation:** Remove this feature entirely. It's a security nightmare.

---

### 4. **NO ACCOUNT LOCKOUT AFTER FAILED ATTEMPTS**
**Severity:** 🔴 CRITICAL
**Location:** Missing implementation

**Issue:**
- No tracking of failed login attempts
- No temporary account lockout
- Enables unlimited brute force attempts (even with rate limiting, attackers can wait)

**Fix Required:**
```python
# Add to User model
failed_login_attempts = Column(Integer, default=0)
locked_until = Column(DateTime, nullable=True)

# In login endpoint
if user.locked_until and datetime.now(timezone.utc) < user.locked_until:
    raise HTTPException(status_code=429, detail=f"Account locked until {user.locked_until}")

if not verify_password(...):
    user.failed_login_attempts += 1
    if user.failed_login_attempts >= 5:
        user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
    db.commit()
    raise HTTPException(...)

# Reset on successful login
user.failed_login_attempts = 0
user.locked_until = None
```

---

### 5. **JWT SECRET KEY IS HARDCODED (Default Values)**
**Severity:** 🔴 CRITICAL
**Location:** `backend/app/core/config.py:59`

```python
jwt_secret_key: str = "change-me-in-production-use-strong-random-key"  # ❌ HARDCODED DEFAULT
```

**Issue:**
- Default secret is in source code (public on GitHub)
- Anyone can forge JWT tokens with this secret
- Complete authentication bypass

**Fix Required:**
```python
# Remove default value entirely
jwt_secret_key: str  # Required env var - no default

# Add validation
@property
def validate_secrets(self):
    if not self.jwt_secret_key or len(self.jwt_secret_key) < 32:
        raise ValueError("JWT_SECRET_KEY must be set and at least 32 characters")
    if self.jwt_secret_key == "change-me-in-production-use-strong-random-key":
        raise ValueError("JWT_SECRET_KEY must be changed from default")
```

Generate strong secret:
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## 🟠 HIGH SEVERITY ISSUES

### 6. **NO CSRF PROTECTION**
**Severity:** 🟠 HIGH
**Location:** Missing implementation

**Issue:**
- No CSRF tokens for state-changing operations
- Vulnerable to Cross-Site Request Forgery attacks
- Attacker can force authenticated users to perform actions

**Fix Required:**
```python
# Install fastapi-csrf-protect
from fastapi_csrf_protect import CsrfProtect

@app.post("/api/users/login")
async def login(csrf_protect: CsrfProtect = Depends()):
    await csrf_protect.validate_csrf_in_cookies(request)
    ...
```

---

### 7. **BASIC EMAIL VALIDATION (No Library)**
**Severity:** 🟠 HIGH
**Location:** `backend/app/services/auth_service.py:224-246`

```python
if '@' not in email or '.' not in email:  # ❌ Too simplistic
    return False, "Invalid email format"
```

**Issue:**
- Accepts invalid emails like `"test@.com"`, `"@test.com"`, etc.
- No DNS validation
- No disposable email detection

**Fix Required:**
```python
# Already in requirements.txt!
from email_validator import validate_email, EmailNotValidError

def is_valid_email(email: str) -> Tuple[bool, str]:
    if not email:
        return True, ""  # Optional

    try:
        valid = validate_email(email, check_deliverability=False)
        return True, ""
    except EmailNotValidError as e:
        return False, str(e)
```

---

### 8. **NO EMAIL VERIFICATION SYSTEM**
**Severity:** 🟠 HIGH
**Location:** Missing implementation

**Issue:**
- Users can register with any email (even fake ones)
- No confirmation that user owns the email
- Enables spam, abuse, fake accounts

**Fix Required:**
Add email verification flow:
1. Generate verification token on registration
2. Send verification email
3. Require verification before sensitive operations
4. Add `email_verified` field to User model

---

### 9. **PASSWORD RESET TOKENS NEVER CLEANED UP**
**Severity:** 🟠 HIGH
**Location:** `backend/app/models/user.py:40-41`

**Issue:**
- Reset tokens stored forever in database
- No automatic cleanup of expired tokens
- Database bloat + potential security issue

**Fix Required:**
```python
# Add cleanup job
from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def cleanup_expired_reset_tokens():
    """Remove expired reset tokens from database."""
    db = next(get_db())
    now = datetime.now(timezone.utc)
    db.query(User).filter(
        User.reset_token.isnot(None),
        User.reset_token_expires < now
    ).update({
        "reset_token": None,
        "reset_token_expires": None
    })
    db.commit()

# Run daily
scheduler.add_job(cleanup_expired_reset_tokens, 'interval', days=1)
```

---

### 10. **NO PASSWORD HISTORY (Allow Reuse)**
**Severity:** 🟠 HIGH
**Location:** Missing implementation

**Issue:**
- Users can set the same password repeatedly
- After breach, attacker can reset to known password

**Fix Required:**
Store hash of last 5 passwords, prevent reuse.

---

## 🟡 MEDIUM SEVERITY ISSUES

### 11. **JWT TOKENS NEVER EXPIRE (No Refresh Mechanism)**
**Severity:** 🟡 MEDIUM
**Location:** `backend/app/services/auth_service.py:68-91`

**Issue:**
- 30-day JWT tokens with no refresh mechanism
- If token is stolen, attacker has 30 days of access
- No way to revoke tokens (no blacklist)

**Fix Required:**
Implement refresh token pattern:
- Short-lived access tokens (15 minutes)
- Long-lived refresh tokens (30 days)
- Refresh token rotation on use
- Token blacklist for revocation

---

### 12. **NO HTTPS ENFORCEMENT**
**Severity:** 🟡 MEDIUM
**Location:** Missing configuration

**Issue:**
- JWT tokens sent over HTTP are vulnerable to interception
- Password reset emails contain HTTP links (not HTTPS)

**Fix Required:**
```python
# Middleware to enforce HTTPS
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
if settings.environment != Environment.DEVELOPMENT:
    app.add_middleware(HTTPSRedirectMiddleware)

# Set secure cookie flags
response.set_cookie(
    key="token",
    value=token,
    httponly=True,  # ✅ Already prevents XSS
    secure=True,    # ⚠️ ADD THIS - HTTPS only
    samesite="lax"  # ⚠️ ADD THIS - CSRF protection
)
```

---

### 13. **MISSING SECURITY HEADERS**
**Severity:** 🟡 MEDIUM
**Location:** Missing implementation

**Fix Required:**
```python
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

---

### 14. **NO AUDIT LOGGING**
**Severity:** 🟡 MEDIUM
**Location:** Missing implementation

**Issue:**
- No logging of authentication events
- Can't detect breaches or suspicious activity
- No compliance audit trail

**Fix Required:**
Log all authentication events:
- Login attempts (success/failure)
- Password changes
- Password resets
- Account lockouts
- Token generation

---

### 15. **TIMEZONE HANDLING INCONSISTENCY**
**Severity:** 🟡 MEDIUM
**Location:** `backend/app/services/auth_service.py:180-188`

**Issue:**
```python
# Sometimes timezone-aware, sometimes not
if expires.tzinfo is None:
    expires = expires.replace(tzinfo=timezone.utc)
```

**Fix Required:**
Always use timezone-aware datetimes. Configure SQLAlchemy:
```python
# All datetime columns should use timezone-aware defaults
created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
```

---

## 🔵 DATABASE SCHEMA ISSUES

### 16. **BROKEN: `domain_key` Removed from Calendar Model**
**Severity:** 🔴 CRITICAL (BREAKS EXISTING CODE)
**Location:** Migration `a1b2c3d4e5f6` moved `domain_key` from `calendars` to `domain_auth`

**Error in Logs:**
```
⚠️ Domain calendar 'exter' issue: Error ensuring domain calendar: type object 'Calendar' has no attribute 'domain_key'
```

**Issue:**
- Migration moved `domain_key` column
- Code still references `Calendar.domain_key`
- Application crashes on domain operations

**Files to Update:**
```bash
grep -r "Calendar.domain_key" backend/
grep -r "calendar.domain_key" backend/
```

**Fix Required:**
Update all code to access domain_key through domain_auth relationship:
```python
# OLD (broken)
calendar.domain_key

# NEW (correct)
domain_auth = db.query(DomainAuth).filter(DomainAuth.calendar_id == calendar.id).first()
domain_key = domain_auth.domain_key if domain_auth else None
```

---

## 🟢 MISSING FEATURES (Incomplete Implementation)

### 17. **Frontend Not Integrated with New Auth System**
- No login/register UI components linked to main app
- No user state management in app
- No protected routes
- No "logged in" indicator

### 18. **No Tests for Authentication**
- Zero unit tests for auth_service.py
- Zero integration tests for login/register
- Zero tests for password reset flow
- No security penetration tests

### 19. **No Admin Password Reset**
- Admin panel has "Forgot password?" button
- But `/reset-password` only works for regular users, not global_admin
- Confusing UX

### 20. **Environment Variables Not Documented**
Required env vars not listed:
- `JWT_SECRET_KEY`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `ADMIN_EMAIL`

---

## 📋 RECOMMENDATIONS

### Immediate Actions (Before ANY Deployment):
1. ✅ Fix password requirements (8+ chars, complexity)
2. ✅ Add rate limiting to all auth endpoints
3. ✅ Remove or heavily warn about username-only auth
4. ✅ Fix JWT secret key (require env var, no default)
5. ✅ Fix domain_key breaking change
6. ✅ Add account lockout mechanism

### Short-term (Within 1 Week):
7. Add CSRF protection
8. Implement email verification
9. Add audit logging
10. Use email-validator library
11. Add security headers
12. Write comprehensive tests

### Medium-term (Within 1 Month):
13. Implement refresh token pattern
14. Add password history
15. Complete frontend integration
16. Add 2FA support (optional)
17. Add OAuth providers (Google, GitHub)
18. Implement session management UI

---

## 🎯 Industry Best Practices Checklist

| Practice | Status | Priority |
|----------|--------|----------|
| **Password Requirements** | ❌ 4 chars (need 8+) | 🔴 CRITICAL |
| **Rate Limiting** | ❌ None | 🔴 CRITICAL |
| **Account Lockout** | ❌ None | 🔴 CRITICAL |
| **JWT Secret Management** | ❌ Hardcoded | 🔴 CRITICAL |
| **CSRF Protection** | ❌ None | 🟠 HIGH |
| **Email Verification** | ❌ None | 🟠 HIGH |
| **HTTPS Enforcement** | ⚠️ Production only | 🟡 MEDIUM |
| **Security Headers** | ❌ None | 🟡 MEDIUM |
| **Audit Logging** | ❌ None | 🟡 MEDIUM |
| **Password Hashing** | ✅ bcrypt (12 rounds) | ✅ GOOD |
| **Secure Cookies** | ⚠️ Partial (no secure flag) | 🟡 MEDIUM |
| **Token Expiry** | ⚠️ 30 days (no refresh) | 🟡 MEDIUM |

---

## 📚 References

- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [NIST Password Guidelines (SP 800-63B)](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/tutorial/security/)

---

**Audited By:** Claude (AI Security Analysis)
**Date:** 2025-01-10
**Status:** ⚠️ **DO NOT DEPLOY TO PRODUCTION WITHOUT FIXES**
