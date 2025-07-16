#!/bin/bash
# Setup PostgreSQL database for KMS-V1

set -e

# Configuration
DB_NAME="kms_v1"
DB_USER="postgres"
DB_PASSWORD="password"
DB_HOST="localhost"
DB_PORT="5432"

echo "🐘 Setting up PostgreSQL database for KMS-V1..."

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed. Please install PostgreSQL first:"
    echo "   macOS: brew install postgresql"
    echo "   Ubuntu: sudo apt-get install postgresql postgresql-contrib"
    echo "   CentOS: sudo yum install postgresql postgresql-server"
    exit 1
fi

# Check if PostgreSQL is running
if ! pg_isready -h $DB_HOST -p $DB_PORT &> /dev/null; then
    echo "❌ PostgreSQL is not running. Please start PostgreSQL first:"
    echo "   macOS: brew services start postgresql"
    echo "   Ubuntu: sudo systemctl start postgresql"
    echo "   CentOS: sudo systemctl start postgresql"
    exit 1
fi

echo "✅ PostgreSQL is running"

# Create database
echo "🗄️ Creating database '$DB_NAME'..."
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "CREATE DATABASE $DB_NAME;"

echo "✅ Database '$DB_NAME' created"

# Update environment file
echo "📝 Updating .env file..."
sed -i.bak "s|DATABASE_URL=.*|DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME|" .env

echo "✅ Environment updated"

echo "🎉 PostgreSQL setup complete!"
echo "📍 Database: $DB_NAME"
echo "🔗 Connection: postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
echo ""
echo "📝 Next steps:"
echo "   1. Run: python scripts/create_tables.py"
echo "   2. Run: python scripts/populate_sample_data.py" 
echo "   3. Restart API server"