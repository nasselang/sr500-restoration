#!/bin/bash
# SR500 Daglig rutine — sjekk epost, oppdater handleliste, push til GitHub
# Kjøres daglig fra cron

set -e

WORKSPACE="/home/johnny/.openclaw/workspace"
PROJECT="$WORKSPACE/projects/sr500-restoration"
SHOPPING="$PROJECT/data/notes/shopping_list.md"
LOG="$WORKSPACE/scripts/sr500-daglig.log"

echo "===== $(date) =====" | tee -a "$LOG"

# --- 1. Sjekk Gmail etter ordrer / forsendelser ---
echo "📬 Sjekker Gmail..." | tee -a "$LOG"

# Søk etter nye ordrerelaterte eposter (siste 2 dager)
gog gmail search "order OR shipping OR tracking OR dispatched OR shipped OR package after:2026-07-08" --max-results 20 2>/dev/null > /tmp/sr500-email-check.txt || true
gog gmail search "bestilling OR forsendelse OR sporingsnummer OR pakke OR levert after:2026-07-08" --max-results 20 2>/dev/null >> /tmp/sr500-email-check.txt || true

# Søk spesifikt etter kjente leverandører
for supplier in "CMSNL" "eBay" "AliExpress" "TOLA" "motogadget" "MegaZip" "Cafe Racer" "Online MC" "Thansen" "Yambits" "Højstyling"; do
    gog gmail search "$supplier after:2026-07-08" --max-results 10 2>/dev/null >> /tmp/sr500-email-check.txt || true
done

ORDRE_FUNNET=false
if grep -qi "order\|shipping\|tracking\|dispatched\|bestilling\|forsendelse\|sporings\|pakke\|levert\|shipped" /tmp/sr500-email-check.txt 2>/dev/null; then
    ORDRE_FUNNET=true
    echo "📦 Relevante eposter funnet:" | tee -a "$LOG"
    grep -i "order\|shipping\|tracking\|dispatched\|bestilling\|forsendelse\|sporings\|pakke\|levert\|shipped" /tmp/sr500-email-check.txt 2>/dev/null | head -10 | tee -a "$LOG"
fi

# --- 2. Sjekk om handlelista har endret seg ---
cd "$PROJECT"

if git diff --quiet "$SHOPPING"; then
    echo "📋 Handlelista uendret siden sist commit" | tee -a "$LOG"
else
    echo "📋 Handlelista har endringer" | tee -a "$LOG"
    git diff "$SHOPPING" | tee -a "$LOG"
fi

# --- 3. Commit og push om det er noe nytt ---
if ! git diff --quiet; then
    echo "⬆️  Pusher endringer til GitHub..." | tee -a "$LOG"
    git add -A
    git commit -m "📋 Daglig oppdatering $(date +%Y-%m-%d)"
    git push origin main 2>&1 | tee -a "$LOG"
    echo "✅ Push OK" | tee -a "$LOG"
else
    echo "✅ Ingen endringer — hopper over push" | tee -a "$LOG"
fi

echo "===== Ferdig $(date) =====" | tee -a "$LOG"
echo "" >> "$LOG"
