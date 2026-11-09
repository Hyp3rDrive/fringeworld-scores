# fringeworld-scores

A public copy of the comments on [Fringe World](https://hyp3rdrive.itch.io/fringe-world)'s itch.io page, for the game's Endless leaderboard.

Web builds of the game can't read itch.io pages directly, because browsers block it (no CORS headers). They can read raw files from a public GitHub repo, so a scheduled GitHub Action (`.github/workflows/scrape.yml`) copies the comments into [`posts.json`](posts.json) every ~15 minutes. It only commits when something changed. Desktop builds read itch.io directly and fall back to this file.

- **No trust needed:** this is just the raw posts (id, author, text). The game verifies every signed score itself, so nothing in this repo can make a score count.
- **Refresh now:** Actions tab → "Mirror itch.io comments" → Run workflow.
- **Test the parser on a saved page:** `python3 scrape.py page.html`. Keep it in step with `Leaderboard.parse_posts()` in the game.
- **Heads-up:** GitHub turns off scheduled workflows in repos with no activity for 60 days. Re-enable it from the Actions tab if the leaderboard ever stops updating.
