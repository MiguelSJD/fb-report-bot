# 📊 Feedback/Bug Report Bot

`FB Report Bot` is a Python Discord bot designed to connect directly with Google Sheets (`gspread`). It retrieves real community feedback entries and vote metrics, organizing them into clean, structured Discord reports—with optional **Gemini AI** integration to sanitize typos, formatting, and inappropriate language automatically.

---

## ✨ Features

* 📅 **Daily Briefings (`/daily-report`):** Highlights high-priority feedback items hitting specific vote thresholds.
* 📈 **Mid-Week Overviews (`/mid-week-report`):** Organizes feedback into category breakdowns sorted by popularity.
* 🏆 **Top 10 Summaries (`/weekly-report-top-10`):** Granular reports detailing descriptions, observations, consequences, and solutions.
* 🛡️ **Gemini AI Content Moderation (`use-ai: True`):** Batches sheet feedback through `gemini-3.6-flash` with structured outputs to fix typos, bad spacing, and censor inappropriate wording on the fly.
* 🔄 **Fail-Safe Processing:** Automatic fallback to raw sheet data if AI quota or network limits are hit.

---

## 🛠️ Tech Stack

* **Language:** Python 3.10+
* **Discord Framework:** `discord.py` (App Commands / Slash Commands)
* **Spreadsheet API:** `gspread` + Google OAuth2 Service Accounts
* **AI Engine:** Google Gemini API (`google-genai` / Pydantic Structured Outputs)
* **Deployment:** Docker support with isolated `.env` environment loading

---

## 📝 License

Distributed under the [MIT License](LICENSE).
