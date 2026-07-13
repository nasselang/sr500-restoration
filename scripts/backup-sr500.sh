#!/bin/bash
# SR500 prosjektbackup — kjøres hver 3. dag
set -e

cd /home/johnny/.openclaw/workspace/projects/sr500-restoration/blog_repo

# Sync project data fra arbeidsmappa
rsync -a --delete /home/johnny/.openclaw/workspace/projects/sr500-restoration/data/ prosjektdata/data/
rsync -a --delete /home/johnny/.openclaw/workspace/projects/sr500-restoration/memory/ prosjektdata/memory/
rsync -a --delete /home/johnny/.openclaw/workspace/projects/sr500-restoration/reference/ prosjektdata/reference/
rsync -a --delete /home/johnny/.openclaw/workspace/projects/sr500-restoration/bibliotek/ prosjektdata/bibliotek/

# Sync agent-filer
cp /home/johnny/.openclaw/workspace/projects/sr500-restoration/AGENTS.md prosjektdata/
cp /home/johnny/.openclaw/workspace/projects/sr500-restoration/SOUL.md prosjektdata/
cp /home/johnny/.openclaw/workspace/projects/sr500-restoration/USER.md prosjektdata/
cp /home/johnny/.openclaw/workspace/projects/sr500-restoration/TOOLS.md prosjektdata/
cp /home/johnny/.openclaw/workspace/projects/sr500-restoration/IDENTITY.md prosjektdata/

# Sync MEMORY.md fra workspace root
cp /home/johnny/.openclaw/workspace/MEMORY.md prosjektdata/

# Sync handleliste
cp /home/johnny/.openclaw/workspace/projects/sr500-restoration/data/notes/shopping_list.md SHOPPINGLIST.md

# Commit og push om det er endringer
if ! git diff --quiet; then
    git add -A
    git commit -m "📦 Auto-backup $(date +%Y-%m-%d)"
    git push origin main
    echo "✅ Backup pushed $(date)"
else
    echo "✅ Ingen endringer — backup hoppet over $(date)"
fi
