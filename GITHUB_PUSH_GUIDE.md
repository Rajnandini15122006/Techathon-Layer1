# 🚀 GitHub Push Guide - PuneRakshak

## Quick Steps to Push to GitHub

### Step 1: Initialize Git (if not already done)

```bash
# Check if git is initialized
git status

# If not initialized, run:
git init
```

### Step 2: Create GitHub Repository

1. Go to https://github.com
2. Click the "+" icon (top right) → "New repository"
3. Repository name: `punerakshak` (or your choice)
4. Description: "Disaster Risk Assessment Platform for Pune City"
5. Choose: **Public** (for judges to see) or **Private**
6. **DO NOT** initialize with README (you already have one)
7. Click "Create repository"

### Step 3: Add All Files to Git

```bash
# Add all files (respects .gitignore)
git add .

# Check what will be committed
git status
```

### Step 4: Create First Commit

```bash
# Commit with a message
git commit -m "Initial commit: PuneRakshak Disaster Risk Assessment Platform"
```

### Step 5: Connect to GitHub

```bash
# Replace YOUR_USERNAME and YOUR_REPO with your actual GitHub username and repo name
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Verify remote is added
git remote -v
```

### Step 6: Push to GitHub

```bash
# Push to main branch
git branch -M main
git push -u origin main
```

### Step 7: Enter GitHub Credentials

When prompted:
- **Username**: Your GitHub username
- **Password**: Use a **Personal Access Token** (not your password)

#### How to Create Personal Access Token:
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name: "PuneRakshak Push"
4. Select scopes: Check **repo** (full control)
5. Click "Generate token"
6. **COPY THE TOKEN** (you won't see it again!)
7. Use this token as your password when pushing

---

## Complete Command Sequence

```bash
# 1. Check git status
git status

# 2. If not initialized
git init

# 3. Add all files
git add .

# 4. Commit
git commit -m "Initial commit: PuneRakshak Disaster Risk Assessment Platform"

# 5. Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/punerakshak.git

# 6. Push
git branch -M main
git push -u origin main
```

---

## What Gets Pushed (Safe Files)

✅ **Included:**
- All Python code (`app/`, `scripts/`)
- HTML/CSS/JS files (`app/static/`)
- Documentation (`.md` files)
- Configuration templates (`.env.example`)
- Requirements files
- Docker files

❌ **Excluded (by .gitignore):**
- `.env` (contains your database password!)
- `__pycache__/` (Python cache)
- `data/` folder (large data files)
- Virtual environment folders

---

## Troubleshooting

### Error: "remote origin already exists"
```bash
# Remove existing remote
git remote remove origin

# Add new remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

### Error: "failed to push some refs"
```bash
# Pull first (if repo has files)
git pull origin main --allow-unrelated-histories

# Then push
git push -u origin main
```

### Error: "Authentication failed"
- Make sure you're using a **Personal Access Token**, not your password
- Token must have **repo** permissions

---

## After Pushing - Update README

Add this badge to your README.md:

```markdown
![GitHub](https://img.shields.io/github/license/YOUR_USERNAME/punerakshak)
![GitHub last commit](https://img.shields.io/github/last-commit/YOUR_USERNAME/punerakshak)
```

---

## Future Updates

When you make changes:

```bash
# 1. Check what changed
git status

# 2. Add changes
git add .

# 3. Commit with descriptive message
git commit -m "Add real-time weather integration"

# 4. Push
git push
```

---

## Important Notes

⚠️ **NEVER commit:**
- `.env` file (contains secrets)
- Database passwords
- API keys (unless in `.env.example` as placeholders)

✅ **Always commit:**
- Code changes
- Documentation updates
- Configuration templates

---

## Share with Judges

After pushing, share this URL with judges:
```
https://github.com/YOUR_USERNAME/punerakshak
```

They can:
- View your code
- Read documentation
- Clone and run locally
- See commit history (shows your work)

---

## Quick Reference

```bash
# Check status
git status

# Add files
git add .

# Commit
git commit -m "Your message"

# Push
git push

# Pull latest
git pull

# View history
git log --oneline
```

---

**You're all set! 🎉**
