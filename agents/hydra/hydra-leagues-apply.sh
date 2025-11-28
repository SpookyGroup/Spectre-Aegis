#!/data/data/com.termux/files/usr/bin/bash
set -e
CFG="$HOME/HYDRA/conf/leagues.json"
[[ -s "$CFG" ]] || { echo "[leagues] config missing"; exit 0; }
echo "[leagues] applied $(date -u +%FT%TZ) -> $CFG" >> "$HOME/.termux/logs/ao7_analytics.log"
if command -v termux-notification >/dev/null 2>&1; then
  title="AO-7 Leagues"
  msg="College leagues enabled: NCAAF & NCAAB (tighter caps)."
  termux-notification --id 7920 --title "$title" --content "$msg" >/dev/null 2>&1 || true
fi
exit 0
