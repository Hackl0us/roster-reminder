CREATE TABLE IF NOT EXISTS stand_up_roster (
   id INTEGER PRIMARY KEY,
   name TEXT NOT NULL,
   slack_member_id TEXT NOT NULL,
   is_today NUMERIC NOT NULL,
)

CREATE TABLE IF NOT EXISTS stand_up_roster_stash(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    slack_member_id TEXT NOT NULL,
    mute_for_today NUMERIC NOT NULL
)