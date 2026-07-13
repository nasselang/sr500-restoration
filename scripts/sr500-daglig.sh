#!/bin/bash
# SR500 Daglig rutine — sjekk epost, oppdater handleliste, push til GitHub
# Kjøres daglig kl 10:00 fra cron

set -e

WORKSPACE="/home/johnny/.openclaw/workspace"
PROJECT="$WORKSPACE/projects/sr500-restoration"
DETAILED="$PROJECT/data/notes/shopping_list.md"
SR500_BLOG="$PROJECT/blog_repo"
LOG="$WORKSPACE/scripts/sr500-daglig.log"

echo "===== $(date) =====" | tee -a "$LOG"

# --- 1. Sjekk Gmail etter ordrer / forsendelser ---
echo "📬 Sjekker Gmail..." | tee -a "$LOG"

gog gmail search "order OR shipping OR tracking OR dispatched OR shipped OR package after:2026-07-08" --max-results 20 2>/dev/null > /tmp/sr500-email-check.txt || true
gog gmail search "bestilling OR forsendelse OR sporingsnummer OR pakke OR levert after:2026-07-08" --max-results 20 2>/dev/null >> /tmp/sr500-email-check.txt || true

for supplier in "CMSNL" "eBay" "AliExpress" "TOLA" "motogadget" "MegaZip" "Cafe Racer" "Online MC" "Thansen" "Yambits" "Højstyling"; do
    gog gmail search "$supplier after:2026-07-08" --max-results 10 2>/dev/null >> /tmp/sr500-email-check.txt || true
done

if grep -qi "order\|shipping\|tracking\|dispatched\|bestilling\|forsendelse\|sporings\|pakke\|levert\|shipped" /tmp/sr500-email-check.txt 2>/dev/null; then
    echo "📦 Relevante eposter funnet:" | tee -a "$LOG"
    grep -i "order\|shipping\|tracking\|dispatched\|bestilling\|forsendelse\|sporings\|pakke\|levert\|shipped" /tmp/sr500-email-check.txt 2>/dev/null | head -10 | tee -a "$LOG"
fi

# --- 2. Sync detaljert handleliste → SHOPPINGLIST.md ---
if [ -f "$SR500_BLOG/SHOPPINGLIST.md" ] && [ -f "$DETAILED" ]; then
    cp "$DETAILED" "$SR500_BLOG/SHOPPINGLIST.md"
    echo "📋 Synket shopping_list.md → SHOPPINGLIST.md" | tee -a "$LOG"
fi

# --- 3. Commit og push prosjektrepo (master) ---
cd "$PROJECT"
PUSHED=false
if ! git diff --quiet; then
    echo "⬆️  Pusher master (prosjektdata)..." | tee -a "$LOG"
    git add -A .
    git commit -m "📋 Daglig oppdatering $(date +%Y-%m-%d)"
    git push origin master 2>&1 | tee -a "$LOG"
    PUSHED=true
fi

# --- 4. Commit og push blog (main) ---
cd "$SR500_BLOG"
if ! git diff --quiet; then
    echo "⬆️  Pusher main (SHOPPINGLIST.md)..." | tee -a "$LOG"
    git add -A
    git commit -m "📋 Handleliste oppdatert $(date +%Y-%m-%d)"
    git push origin main 2>&1 | tee -a "$LOG"
    PUSHED=true
fi

if [ "$PUSHED" = false ]; then
    echo "✅ Ingen endringer — hopper over push" | tee -a "$LOG"
fi

echo "===== Ferdig $(date) =====" | tee -a "$LOG"
echo "" >> "$LOG"
