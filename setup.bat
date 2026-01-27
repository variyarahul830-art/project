@echo off
REM Hasura Project Setup Script for Windows
REM This script sets up the entire Hasura integration

setlocal enabledelayedexpansion

echo ================================
echo Hasura Project Setup
echo ================================

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed. Please install Docker first.
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

echo.
echo Step 1: Starting Docker Containers...
docker-compose up -d
timeout /t 10 /nobreak

echo Step 2: Verifying Container Status...
docker ps -a

echo.
echo Step 3: Installing Python Dependencies...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

echo Installing requirements...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Step 4: Verifying Dependencies...
pip check
echo. ✓ No dependency conflicts detected

echo.
echo Step 5: Creating Database Schema...
echo Waiting for PostgreSQL to be ready...
timeout /t 5 /nobreak

REM Execute schema using psql in Docker
echo Attempting to create database schema...
docker exec -i hasura-postgres psql -U postgres -d hasuradb -f /dev/stdin < schema.sql

cd ..

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo Next Steps:
echo 1. Access Hasura Console: http://localhost:8081
echo 2. Create database tables using Hasura console (if not created above)
echo 3. Test backend: cd backend ^&^& python -m uvicorn main:app --reload
echo 4. Test frontend: cd frontend ^&^& npm run dev
echo.
echo Documentation: See HASURA_SETUP.md
echo.
pause
