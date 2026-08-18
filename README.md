<div align="center">

# 📊 Feedback & Bugs Bot

**Automated community feedback reporting for Discord, powered by Google Sheets**

[![CI](https://github.com/MiguelSJD/fb-report-bot/actions/workflows/unit-tests.yml/badge.svg?branch=main)](https://github.com/MiguelSJD/fb-report-bot/actions/workflows/unit-tests.yml)
[![Docker](https://img.shields.io/badge/Docker-Supported-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📖 Overview

`F&B Bot` bridges community feedback from **Google Sheets** (`gspread`) directly into structured **Discord reports**. It aggregates data, tracks vote thresholds, and organizes user feedback into readable executive summaries for development teams.

---

## ✨ Features

* 📅 **Daily Briefings (`/daily-report`):** Highlight high-priority feedback entries that cross specific community vote thresholds.
* 📈 **Mid-Week Overviews (`/mid-week-report`):** Categorize incoming entries sorted dynamically by popularity and engagement.
* 🏆 **Top 10 Summaries (`/weekly-report-top-10`):** Generate granular reports breaking down descriptions, observations, consequences, and proposed solutions.
* 🛠️ **SQLite Settings & Management Dashboard:** Manage guild configurations, cron schedules, and system logs through a local dashboard UI.

---

## 🛠️ Tech Stack

| Category | Technology |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **Discord Engine** | `discord.py` (App Commands / Slash Commands) |
| **Spreadsheet Integration** | `gspread` + Google OAuth2 Service Accounts |
| **Database & Logging** | SQLite3 + Structured JSONL Rotating Logger |
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
   git clone [https://github.com/MiguelSJD/fb-report-bot.git](https://github.com/MiguelSJD/fb-report-bot.git)
   cd fb-bot
   ```

2. **Add Google Service Account Credentials:**
   Place your downloaded Google Cloud service account key file in the root directory named `credentials.json`:
   ```text
   fb-bot/
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