#!/bin/bash
set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

on_error() {
  echo -e "${RED}Deployment failed. Resolve the error and retry.${NC}"
}
trap on_error ERR

echo -e "${YELLOW}Fetching latest links...${NC}"
cd backend
python3 telegram_fetcher.py
cd ..

echo -e "${YELLOW}Copying to docs folder...${NC}"
mkdir -p docs
cp -r frontend/* docs/

echo -e "${YELLOW}Committing changes...${NC}"
git add .
git commit -m "Update links - $(date '+%Y-%m-%d %H:%M')" || echo -e "${YELLOW}No changes to commit.${NC}"
git push origin main

echo -e "${GREEN}Deployed! Check GitHub Pages in 2-3 minutes.${NC}"
