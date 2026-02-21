@echo off
REM PuneRakshak - Quick GitHub Push Script for Windows
REM Run this after creating your GitHub repository

echo.
echo ========================================
echo   PuneRakshak - GitHub Push Helper
echo ========================================
echo.

REM Check if git is initialized
if not exist .git (
    echo Initializing Git repository...
    git init
    echo Git initialized successfully!
) else (
    echo Git already initialized
)

echo.
set /p REPO_URL="Enter your GitHub repository URL (e.g., https://github.com/username/punerakshak.git): "

if "%REPO_URL%"=="" (
    echo Error: Repository URL cannot be empty
    pause
    exit /b 1
)

echo.
echo Adding files to git...
git add .

echo.
echo Creating commit...
git commit -m "Initial commit: PuneRakshak Disaster Risk Assessment Platform - Features: Real-time weather monitoring, 250m spatial grid, disaster risk assessment, interactive map visualization"

echo.
echo Adding remote repository...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo.
echo Pushing to GitHub...
git branch -M main
git push -u origin main

echo.
echo ========================================
echo   Done! Your code is now on GitHub!
echo ========================================
echo.
echo View your repository at:
echo %REPO_URL%
echo.
echo Share this link with judges!
echo.
pause
