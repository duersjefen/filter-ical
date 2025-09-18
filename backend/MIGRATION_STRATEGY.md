# Database Migration Strategy

## Current Phase: Pre-User Development

**Status**: Using simple table creation from SQLModel models  
**Why**: No users exist yet, so we can safely reset the database when needed

### Current Approach
```python
# database.py
def create_db_and_tables():
    # DEVELOPMENT/PRE-USER PHASE: Simple table creation
    SQLModel.metadata.create_all(engine)
    
    # PRODUCTION WITH USERS: Enable migrations (uncomment below)
    # run_migrations()
```

**Benefits:**
- ✅ Zero migration complexity
- ✅ Instant schema updates (just restart server)
- ✅ No version conflicts
- ✅ Perfect for rapid development

## Future Phase: Production with Users

**When to Switch**: As soon as you have real users with data you can't lose

### Migration to Alembic (Future)

**1. Create Initial Migration from Current Schema:**
```bash
# When ready to switch to migrations
cd backend
. venv/bin/activate

# Create initial migration from current schema
alembic revision --autogenerate -m "Initial schema from pre-user phase"

# Review the generated migration file
# Edit if needed to match your exact current production schema
```

**2. Mark Current Production as Up-to-Date:**
```bash
# On production server (after deploying the initial migration)
alembic stamp head
```

**3. Enable Migrations in Code:**
```python
# In database.py, switch to:
def create_db_and_tables():
    """Create database tables and run migrations"""
    # PRODUCTION WITH USERS: Migrations enabled
    run_migrations()
    
    # DEVELOPMENT/PRE-USER PHASE: Simple table creation (comment out below)
    # SQLModel.metadata.create_all(engine)
```

**4. Future Schema Changes:**
```bash
# After changing models
alembic revision --autogenerate -m "Add new feature"
alembic upgrade head  # Or automatic via run_migrations()
```

## Why This Strategy Works

### Development Phase (Now)
- **Fast iteration**: Change models → restart → schema updated
- **No migration files**: Keep things simple until users arrive
- **Easy debugging**: Fresh schema every restart eliminates migration conflicts

### Production Phase (Later)
- **Data preservation**: Existing user data is never lost
- **Controlled changes**: Every schema change is versioned and reviewable
- **Rollback capability**: Can revert problematic changes
- **Team coordination**: Schema changes are tracked in git

## Transition Checklist

**Before switching to migrations:**
- [ ] Confirm you have real users with valuable data
- [ ] Document current production schema exactly
- [ ] Create initial migration that matches current production
- [ ] Test migration process on staging environment
- [ ] Update deployment scripts to use migrations
- [ ] Train team on migration workflow

## Commands Available

**Current Phase:**
```bash
make db-reset                    # Reset local database
make deploy-clean               # Deploy with fresh database (destroys data)
python scripts/reset_database.py # Manual database reset
```

**Future Phase (after enabling migrations):**
```bash
alembic revision --autogenerate -m "description"  # Create migration
alembic upgrade head            # Apply migrations
alembic downgrade -1           # Rollback last migration
make deploy                    # Deploy with automatic migrations
```

## Migration Infrastructure Ready

The Alembic infrastructure is already set up and ready:
- ✅ `alembic.ini` configured
- ✅ `alembic/env.py` set up
- ✅ `run_migrations()` function implemented
- ✅ Migration directory structure exists
- ✅ Just needs to be enabled when ready

**Summary**: You get the best of both worlds - simplicity now, and enterprise-grade migrations when you need them!