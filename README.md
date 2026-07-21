# PSL Drop Checker

Watches PSL Source and STR Marketplace for **new listings** on the teams you
pick, and pings your Discord the second one shows up. Runs automatically,
every 10 minutes, for free — your computer doesn't need to stay on.

You already set this pattern up once for the LA28 project, so this will feel
familiar. No coding needed.

---

## Step 1 — Discord webhook (skip if you already have one from before)

If you already made a Discord webhook for the LA28 checker, you can reuse
that same one, or make a new channel just for this. To make a new one:
1. In Discord, create a channel (e.g. `#psl-alerts`).
2. Right-click it → **Edit Channel** → **Integrations** → **Webhooks** → **New Webhook** → **Copy Webhook URL**.

## Step 2 — Put this project on GitHub

Easiest method (avoids the hidden-folder issue from before):

1. Go to [github.com](https://github.com) → **New repository** → name it `psl-checker` → **Create repository**.
2. Click **uploading an existing file**, drag in `monitor.py`, `requirements.txt`, `teams.json`, `README.md`.
3. Click **Commit changes**.
4. Click **Add file** → **Create new file**.
5. Type this exact path (the slashes auto-create the folders):
   ```
   .github/workflows/check.yml
   ```
6. Paste in the contents of `check.yml` (open it in TextEdit, copy everything).
7. Click **Commit changes**.

## Step 3 — Add your Discord webhook as a secret

1. In the repo: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.
2. Name: `DISCORD_WEBHOOK_URL`
3. Value: paste your webhook URL.
4. **Add secret**.

## Step 4 — Turn it on

1. Go to the **Actions** tab → enable workflows if prompted.
2. Click **PSL Drop Checker** → **Run workflow** → **Run workflow** (first manual test).
3. Check your Discord — the *very first run* will silently record every existing listing (no spam). Every run *after that* only alerts on genuinely new listings.

---

## Adding more teams (this is the main thing you'll do)

Open `teams.json` in any text editor. It looks like this:

```json
{
  "pslsource_teams": [
    { "name": "Atlanta Falcons", "team_id": 1 }
  ],
  "strmarketplace_teams": [
    { "name": "Las Vegas Raiders", "code": "F02E65F", "subdomain": "raiders" }
  ]
}
```

Add a new `{ "name": ..., ... }` entry for each team you want, following the
same pattern, separated by commas. Save, re-upload to GitHub, done.

### How to find a team's PSL Source `team_id`

1. Go to that team's "Buy PSLs" page on pslsource.com (e.g. `pslsource.com/buy_dallas_cowboys_psl`).
2. Right-click → **View Page Source**.
3. Press `Cmd+F` to search the page for the word `inventory`.
4. You'll see something like `/inventory/7` — that number (`7`) is the `team_id`.

### How to find a team's STR Marketplace `code` and `subdomain`

1. Go to that team's page (e.g. `cowboys.strmarketplace.com`).
2. The `subdomain` is just the first word before `.strmarketplace.com` (e.g. `cowboys`).
3. Right-click the listings page → **View Page Source**.
4. Search (`Cmd+F`) for `data.json`.
5. You'll see something like `/WebServices/json/AB12CD3/data.json` — that code (`AB12CD3`) is the `code`.

If you get stuck finding one of these, paste me the page source (like you did
before) and I'll pull it out for you.

---

## Important notes

- **This only detects and notifies — it does not buy or bid for you.** You still make the offer yourself.
- **"New listing" = a listing ID we haven't seen before.** It won't catch price *drops* on existing listings yet — if your client wants that too, let me know and I'll add it.
- Both sites' internal data feeds were found by inspecting their page source, not through any official API — if either site changes its website structure, the feed URL might change and need updating.
