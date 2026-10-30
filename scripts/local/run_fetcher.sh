#!/bin/bash
set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

on_error() {
  echo -e "${RED}Error: fetch failed. Check logs above.${NC}"
}
trap on_error ERR

# Optional local helper; the live site is updated through GitHub Actions.
cd "$(dirname "$0")/../../backend"

echo -e "${YELLOW}Running telegram_fetcher.py...${NC}"
python3 telegram_fetcher.py

echo -e "${GREEN}Fetch completed at $(date)${NC}"
