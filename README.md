# LinkedIn Post Automation with GitHub Actions

![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Scheduled-2088FF?logo=githubactions)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)
![LinkedIn API](https://img.shields.io/badge/LinkedIn-API-0A66C2?logo=linkedin)
![License](https://img.shields.io/badge/license-MIT-green)

Automate your LinkedIn posts using the **LinkedIn API** and **GitHub Actions** scheduled workflows. Write your posts as markdown files, set a date, and let the automation handle publishing — no manual posting needed.

---

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│                   GitHub Repository                      │
│                                                          │
│  posts/                    .github/workflows/            │
│  ├── 2024-01-15.md  ──────▶ scheduled-post.yml          │
│  ├── 2024-01-22.md         (cron: every Monday 9am)     │
│  └── 2024-01-29.md                  │                   │
│                                     ▼                   │
│                          src/post_scheduler.py           │
│                                     │                   │
│                          src/linkedin_client.py          │
│                                     │                   │
└─────────────────────────────────────┼───────────────────┘
                                      │
                                      ▼
                          ┌─────────────────────┐
                          │   LinkedIn API       │
                          │  POST /ugcPosts      │
                          │  (publishes post)    │
                          └─────────────────────┘
```

1. Write post content in `posts/` directory (markdown files with a date)
2. GitHub Actions runs on a schedule (cron job — every Monday 9am UTC)
3. The script reads the next scheduled post
4. Posts it to LinkedIn via the LinkedIn API (OAuth 2.0)
5. Marks the post as `published: true` and commits back

---

## Step-by-Step Setup

### Step 1: Create a LinkedIn Developer App

1. Go to [developer.linkedin.com](https://developer.linkedin.com/)
2. Click **"Create App"**
3. Fill in:
   - App Name (e.g., "My Post Automation")
   - LinkedIn Page (create one if needed — can be a personal page)
   - App Logo
4. Under **"Products"**, request access to:
   - ✅ **Share on LinkedIn** (gives `w_member_social` scope)
5. Once approved, go to **"Auth"** tab — copy your **Client ID** and **Client Secret**

### Step 2: Get Your OAuth Tokens

LinkedIn uses OAuth 2.0 Authorization Code Flow.

**Option A — Use the LinkedIn OAuth Tool (easiest):**
1. In your LinkedIn Developer App → **Auth** tab
2. Use the OAuth 2.0 tools section to generate tokens

**Option B — Manual OAuth Flow:**

Construct the authorization URL:
```
https://www.linkedin.com/oauth/v2/authorization
  ?response_type=code
  &client_id=YOUR_CLIENT_ID
  &redirect_uri=https://localhost
  &scope=w_member_social%20r_liteprofile
```

Open in browser → authorize → copy the `code` parameter from the redirect URL.

Exchange code for tokens:
```bash
curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
  -d "grant_type=authorization_code" \
  -d "code=YOUR_CODE" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "redirect_uri=https://localhost"
```

Save the `access_token` and `refresh_token` from the response.

### Step 3: Find Your LinkedIn Person URN

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  https://api.linkedin.com/v2/me
```

Your URN is: `urn:li:person:{id_from_response}`

### Step 4: Configure GitHub Secrets

In your repo: **Settings → Secrets and variables → Actions → New repository secret**

| Secret Name | Value | Notes |
|-------------|-------|-------|
| `LINKEDIN_CLIENT_ID` | Your app's Client ID | From Developer Portal |
| `LINKEDIN_CLIENT_SECRET` | Your app's Client Secret | From Developer Portal |
| `LINKEDIN_ACCESS_TOKEN` | OAuth Access Token | Expires in 60 days |
| `LINKEDIN_REFRESH_TOKEN` | OAuth Refresh Token | Expires in 365 days |
| `LINKEDIN_PERSON_URN` | `urn:li:person:XXXXXXX` | Your LinkedIn member URN |

### Step 5: Write Your First Post

Create a file in `posts/` named with the date:

```markdown
<!-- posts/2024-01-15.md -->
---
scheduled: 2024-01-15
published: false
---

Excited to share a project I've been working on — a full-stack app
built with .NET 8 and React 18!

Check out the repo in my profile if you're exploring modern .NET development.

#dotnet #react #softwaredevelopment #csharp
```

### Step 6: Push and You're Done!

Push to GitHub — the workflow runs automatically on schedule.

**To test manually:**
1. Go to **Actions** tab in your repo
2. Select **"Post to LinkedIn"**
3. Click **"Run workflow"**

---

## Customizing the Schedule

Edit `.github/workflows/scheduled-post.yml`:

```yaml
on:
  schedule:
    - cron: '0 9 * * 1'    # Every Monday at 9am UTC
    # - cron: '0 9 * * *'  # Every day at 9am UTC
    # - cron: '0 9 1 * *'  # First of every month at 9am UTC
```

Use [crontab.guru](https://crontab.guru/) to build your schedule.

---

## Post Types

| Type | How to use |
|------|-----------|
| Text only | Just write your content |
| With hashtags | Add `#hashtag` at the bottom |
| With link | Include a URL — LinkedIn auto-previews it |
| Multi-paragraph | Use blank lines between paragraphs |

---

## Token Refresh

Access tokens expire every **60 days**. The script automatically refreshes using your refresh token. If your refresh token also expires (365 days), re-authorize via the OAuth flow and update your GitHub secrets.

---

## Limitations

- LinkedIn API allows ~150 posts per day per app
- Posts are text-only by default (image/video requires additional API setup)
- LinkedIn may throttle rapid posting

---

## Project Structure

```
linkedin-post-automation/
├── src/
│   ├── linkedin_client.py      # LinkedIn API wrapper (OAuth 2.0)
│   ├── post_scheduler.py       # Reads posts/ and publishes next one
│   └── config.example.env      # Environment variable template
├── posts/
│   └── example-post.md         # Example post file
├── .github/workflows/
│   └── scheduled-post.yml      # GitHub Actions cron job
├── requirements.txt
└── README.md
```

---

## License

MIT © [miteshdekate93](https://github.com/miteshdekate93)
