#!/bin/bash
set -euo pipefail

# Legacy manual publisher. Normal updates use Actions > Fetch Links.
# Publish the root data file, matching the current GitHub Pages source.
cd "$(dirname "$0")/../.."
if [ "$(git branch --show-current)" != "main" ]; then
  echo "Legacy publishing requires main. Switch branches before fetching."
  exit 1
fi
if ! git diff --cached --quiet; then
  echo "Staged changes exist. Unstage them before using this legacy publisher."
  exit 1
fi

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

if git diff --quiet -- data.json; then
  echo -e "${YELLOW}No changes to data.json.${NC}"
  exit 0
fi

echo -e "${YELLOW}Committing changes...${NC}"
git add -- data.json
git commit -m "Update links - $(date '+%Y-%m-%d %H:%M')"
git push origin main

echo -e "${GREEN}Deployed! Check GitHub Pages in 2-3 minutes.${NC}"
