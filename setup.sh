#!/bin/bash
# Hasura Project Setup Script
# This script sets up the entire Hasura integration

set -e

echo "================================"
echo "Hasura Project Setup"
echo "================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "ERROR: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo ""
echo "Step 1: Starting Docker Containers..."
docker-compose up -d
sleep 10

echo "Step 2: Verifying Container Status..."
docker ps -a

echo ""
echo "Step 3: Installing Python Dependencies..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

echo "Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Step 4: Verifying Dependencies..."
pip check
echo "✓ No dependency conflicts detected"

echo ""
echo "Step 5: Creating Database Schema..."
echo "Waiting for PostgreSQL to be ready..."
sleep 5

# Try to execute schema.sql
docker exec -i hasura-postgres psql -U postgres -d hasuradb -f /dev/stdin < schema.sql 2>/dev/null || {
    echo "Note: Schema creation requires manual setup. See HASURA_SETUP.md for details."
}

cd ..

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Next Steps:"
echo "1. Access Hasura Console: http://localhost:8081"
echo "2. Create database tables using Hasura console or:"
echo "   docker exec -i hasura-postgres psql -U postgres -d hasuradb < backend/schema.sql"
echo "3. Test backend: cd backend && python -m uvicorn main:app --reload"
echo "4. Test frontend: cd frontend && npm run dev"
echo ""
echo "Documentation: See HASURA_SETUP.md"
