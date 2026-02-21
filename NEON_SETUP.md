# Neon PostgreSQL Setup Guide

## Step 1: Create Neon Database

1. Go to https://neon.tech and sign up/login
2. Create a new project
3. Note your connection string (it will look like):
   ```
   postgresql://user:password@ep-xxx-xxx.region.aws.neon.tech/dbname
   ```

## Step 2: Enable PostGIS Extension

Neon supports PostGIS, but you need to enable it manually.

### Method 1: Using Neon SQL Editor (Recommended)

1. Go to your Neon project dashboard
2. Click on "SQL Editor" in the left sidebar
3. Run this command:
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```
4. Verify installation:
   ```sql
   SELECT PostGIS_version();
   ```

### Method 2: Using psql

1. Install psql client if you don't have it
2. Connect to your Neon database:
   ```bash
   psql "postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require"
   ```
3. Run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```

## Step 3: Configure Application

1. Copy your Neon connection string
2. Add `?sslmode=require` at the end if not present
3. Update `.env` file:
   ```
   DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
   ```

## Step 4: Test Connection

Run the FastAPI application:
```bash
uvicorn app.main:app --reload
```

If PostGIS is properly configured, you should see:
```
INFO:     Initializing database...
INFO:     PostGIS version: 3.x.x
INFO:     Database initialized successfully
```

## Troubleshooting

### Error: "PostGIS extension not found"

**Solution:** Enable PostGIS extension in Neon SQL Editor:
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

### Error: "SSL connection required"

**Solution:** Ensure your connection string includes `?sslmode=require`:
```
DATABASE_URL=postgresql://...?sslmode=require
```

### Error: "Connection refused"

**Solution:** 
- Check your connection string is correct
- Verify your Neon project is active (not suspended)
- Check your IP is not blocked (Neon allows all IPs by default)

## Connection String Format

```
postgresql://[user]:[password]@[host]/[database]?sslmode=require
```

Example:
```
postgresql://myuser:mypassword@ep-cool-darkness-123456.us-east-2.aws.neon.tech/punerakshak?sslmode=require
```

## Important Notes

- Neon requires SSL connections (`sslmode=require`)
- PostGIS extension must be enabled manually
- Neon free tier has compute limits (check your plan)
- Connection pooling is configured in `app/database.py`
- The application uses `pool_pre_ping=True` for connection health checks
