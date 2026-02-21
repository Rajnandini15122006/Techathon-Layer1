#!/bin/bash

# PuneRakshak - Quick GitHub Push Script
# Run this after creating your GitHub repository

echo "🚀 PuneRakshak - GitHub Push Helper"
echo "===================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing Git repository..."
    git init
    echo "✓ Git initialized"
else
    echo "✓ Git already initialized"
fi

echo ""
echo "📝 Please enter your GitHub repository URL:"
echo "Example: https://github.com/username/punerakshak.git"
read -p "Repository URL: " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ Error: Repository URL cannot be empty"
    exit 1
fi

echo ""
echo "📋 Adding files to git..."
git add .

echo ""
echo "💬 Creating commit..."
git commit -m "Initial commit: PuneRakshak Disaster Risk Assessment Platform

Features:
- Real-time weather monitoring
- 250m x 250m spatial grid coverage
- Disaster risk assessment
- Interactive map visualization
- Professional government-style UI"

echo ""
echo "🔗 Adding remote repository..."
git remote remove origin 2>/dev/null
git remote add origin "$REPO_URL"

echo ""
echo "📤 Pushing to GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "✅ Done! Your code is now on GitHub!"
echo ""
echo "🌐 View your repository at:"
echo "$REPO_URL"
echo ""
echo "📚 Share this link with judges!"
