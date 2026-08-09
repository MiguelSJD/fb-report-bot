<div align="center">

# 📊 FB Report Bot

**Automated community feedback reporting for Discord, powered by Google Sheets and Google Gemini.**

[![CI](https://github.com/MiguelSJD/fb-report-bot/actions/workflows/unit-tests.yml/badge.svg?branch=main)](https://github.com/MiguelSJD/fb-report-bot/actions/workflows/unit-tests.yml)
[![Docker](https://img.shields.io/badge/Docker-Supported-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📖 Overview

`FB Report Bot` bridges community feedback from **Google Sheets** (`gspread`) directly into structured **Discord reports**. It aggregates data, tracks vote thresholds, and organizes user feedback into readable executive summaries for development teams.

---

## ✨ Features

* 📅 **Daily Briefings (`/daily-report`):** Highlight high-priority feedback entries that cross specific community vote thresholds.
* 📈 **Mid-Week Overviews (`/mid-week-report`):** Categorize incoming entries sorted dynamically by popularity and engagement.
* 🏆 **Top 10 Summaries (`/weekly-report-top-10`):** Generate granular reports breaking down descriptions, observations, consequences, and proposed solutions.
* 🛠️ **SQLite Settings & Management Dashboard:** Manage guild configurations, cron schedules, and system logs through a local dashboard UI.

---

## 🗺️ Product Roadmap

### 🤖 AI Moderation (In Development)
We are actively building optional AI-powered content moderation (`use-ai: True`) utilizing the **Google Gemini API**. 

When enabled, the moderation pipeline will:
* **Sanitize Output:** Clean up community formatting, awkward spacing, and common typos automatically.
* **Auto-Redact Violations:** Automatically redact hate speech, profanity, illegal content, or severe harassment from being rendered in public Discord embeds.
* **Structured Output Parsing:** Utilize strict JSON schemas to guarantee safe data extraction without altering original database records.

---

## 🛠️ Tech Stack

| Category | Technology |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **Discord Engine** | `discord.py` (App Commands / Slash Commands) |
| **Spreadsheet Integration** | `gspread` + Google OAuth2 Service Accounts |
| **Database & Logging** | SQLite3 + Structured JSONL Rotating Logger |
| **AI Moderation Stack** | Google Gemini API (`google-genai` / Pydantic) |
| **Containerization** | Docker & Docker Compose |

---

## 🚀 Quick Start

### Prerequisites
* Python 3.10+ or Docker / Docker Compose
* Google Cloud Service Account Credentials (`credentials.json`)
* Discord Bot Token

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/fb-report-bot.git](https://github.com/your-username/fb-report-bot.git)
   cd fb-report-bot
   ```

2. **Add Google Service Account Credentials:**
   Place your downloaded Google Cloud service account key file in the root directory named `credentials.json`:
   ```text
   fb-report-bot/
   ├── credentials.json  <-- Place key here
   ├── .env
   └── docker-compose.yml
   ```

3. **Configure Environment Variables:**
   Copy `.env.example` to `.env` and fill in your secrets:
   ```bash
   cp .env.example .env
   ```

4. **Deploy via Docker Compose:**
   ```bash
   docker compose up -d --build
   ```

---

## 📝 License

Distributed under the [MIT License](LICENSE).