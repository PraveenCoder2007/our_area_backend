@echo off
echo Applying schema to Turso database...
turso db shell ourarea-praveencoder2007 < schema.sql
echo Schema applied successfully!