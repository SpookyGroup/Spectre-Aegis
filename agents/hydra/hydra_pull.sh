#!/data/data/com.termux/files/usr/bin/bash

# League can be passed in (default: NFL)
LEAGUE="${1:-americanfootball_nfl}"

# Call your Supabase Edge Function
curl -s "$SUPABASE_URL" \
  -H "Content-Type: application/json" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY" \
  -d "{\"league\":\"$LEAGUE\"}" |
jq -r '
  .games[] as $g
  | $g.bookmakers[0] as $b
  | $b.markets[] as $m
  | {
      home: $g.home_team,
      away: $g.away_team,
      time: $g.commence_time,
      market: $m.key,
      outcomes: $m.outcomes
    }
  | select(.market=="h2h" or .market=="spreads" or .market=="totals")
  | if .market=="h2h" then
      "🏈 " + .home + " vs " + .away + " @ " + .time + "\n" +
      "   Moneyline: " +
      ([.outcomes[] | "\(.name) \(.price)"] | join(" | "))
    elif .market=="spreads" then
      "   Spread: " +
      ([.outcomes[] | "\(.name) \(.point) \(.price)"] | join(" | "))
    else
      "   Total: " +
      ([.outcomes[] | "\(.name) \(.point) \(.price)"] | join(" | ")) + "\n---"
    end
'
