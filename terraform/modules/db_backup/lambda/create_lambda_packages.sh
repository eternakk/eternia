#!/bin/bash
# Script to create Lambda function deployment packages

set -e

# Create a temporary directory for the packages
TEMP_DIR=$(mktemp -d)

# Create the backup Lambda package
echo "Creating backup Lambda package..."
cp backup_handler.py $TEMP_DIR/backup_handler.py
cd $TEMP_DIR
zip -r db_backup_lambda.zip backup_handler.py
cd -
mv $TEMP_DIR/db_backup_lambda.zip .

# Create the verification Lambda package
echo "Creating verification Lambda package..."
cp verification_handler.py $TEMP_DIR/verification_handler.py
cd $TEMP_DIR
zip -r db_backup_verification_lambda.zip verification_handler.py
cd -
mv $TEMP_DIR/db_backup_verification_lambda.zip .

# Clean up
rm -rf $TEMP_DIR

echo "Lambda packages created successfully."