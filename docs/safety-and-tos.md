# Safety and LinkedIn terms
- LinkedIn has no official API for posting to a personal profile. Automating the browser or using third-party posting tools can break LinkedIn's User Agreement and get an account restricted. This project never posts on a schedule.
- Scheduled runs DRAFT and notify. A human reads the draft and approves each publish, one post at a time.
- Never let an agent react, repost, delete, or comment on other people's posts unattended.
- Never invent numbers, clients, quotes or incidents. Use placeholders and ask.
- Do not put personal data, employer or client names, credentials or analytics exports in a public repo.

## Before you push your own fork
Run `git grep -n -i "your-employer\|your-email\|client-name"` and make sure `state/` and generated media are git-ignored (see `.gitignore`).
