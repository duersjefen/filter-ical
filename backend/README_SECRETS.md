# Secrets Configuration

## Required Environment Variables

### PASSWORD_ENCRYPTION_KEY

**Generate a new key:**
```bash
cd backend
source venv/bin/activate
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Add to `.env.production` and `.env.staging`:**
```
PASSWORD_ENCRYPTION_KEY=your-generated-key-here
```

**Example:**
```
PASSWORD_ENCRYPTION_KEY=Uxw19FyOQEu3AqCuhxi9Z-0AckG5BcqVbgH9l43YnKc=
```

## Migration Notes

- **Development:** Uses the default dev key (safe for local testing)
- **Production/Staging:** MUST set `PASSWORD_ENCRYPTION_KEY` environment variable
- **Existing passwords:** If you change the key, existing encrypted passwords will fail. Users will need to re-enter credentials. For small projects with few users, this is acceptable.

## Security Best Practices

1. **Never commit** `.env.production` or `.env.staging` to git (already in .gitignore)
2. **Generate unique keys** for staging and production environments
3. **Rotate keys periodically** (document in deployment notes when users need to reset)
4. **Keep keys secure** - treat like database passwords
