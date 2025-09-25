#!/bin/bash
set -e

echo "Aplicando migraciones..."
flask db upgrade

echo "Iniciando la app Flask..."
exec flask run --host=0.0.0.0 --port=5000
