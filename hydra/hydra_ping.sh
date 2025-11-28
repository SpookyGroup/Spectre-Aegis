#!/data/data/com.termux/files/usr/bin/bash

curl -s "$SUPABASE_URL/functions/v1/check-upcoming-games" \
  -H "Content-Type: application/json" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY" \
  -d '{"league":"americanfootball_nfl"}'
