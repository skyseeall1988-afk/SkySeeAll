#!/bin/sh
# generate_env.sh - create a .env from .env.example with safe defaults
set -e
if [ -f .env ]; then
  echo ".env already exists. Backing up to .env.bak"
  cp .env .env.bak
fi
cat .env.example > .env
chmod 600 .env
echo ".env generated from .env.example (edit as needed)"