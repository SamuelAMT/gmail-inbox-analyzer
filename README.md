# Gmail Inbox Analyzer

A Python script to analyze your Gmail inbox and identify which senders are flooding your Primary, Social, and Promotions categories. Perfect for deciding who to unsubscribe from or whose emails to delete.

## What It Does

- 📊 Analyzes Primary, Social, and Promotions inboxes
- 🔍 Counts emails per sender without reading email content
- 📝 Generates detailed reports showing top senders
- 🔒 Preserves read/unread status - only accesses email headers
- 📈 Provides breakdown by Gmail category

## Features

- Uses official Gmail API (secure, won't get you banned)
- Respects Gmail's rate limits and authentication
- Works with 2FA enabled accounts
- Exports results to text file for easy reference

## Setup

### 1. Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Navigate to **APIs & Services** → **Library**
4. Search for "Gmail API" and enable it
5. Go to **APIs & Services** → **OAuth consent screen**
   - Choose "External" user type
   - Fill in app name (e.g., "Gmail Analyzer")
   - Add your email as a test user
6. Go to **APIs & Services** → **Credentials**
   - Create credentials → OAuth 2.0 Client ID
   - Select "Desktop application"
   - Download the JSON file and rename it to `credentials.json`

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Script

```bash
python script.py
```

On first run, it will:
- Open your browser for Google authentication
- Save credentials for future runs
- Analyze your inbox and generate reports

## Output

The script generates:
- **Console output**: Top 20 senders with email counts
- **gmail_analysis.txt**: Detailed breakdown by category
- **token.pickle**: Authentication token (auto-generated)

## File Structure

```
gmail-inbox-analyzer/
├── script.py              # Main analyzer script
├── credentials.json       # OAuth credentials (keep private)
├── requirements.txt       # Python dependencies
├── token.pickle          # Auth token (auto-generated, keep private)
├── gmail_analysis.txt    # Results (auto-generated)
└── .gitignore           # Git ignore file
```

## Security Notes

- `credentials.json` and `token.pickle` contain sensitive data - never commit to version control
- Script only reads email headers, not content
- Uses read-only Gmail API permissions
- Your email password is never stored or required

## Example Output

```
GMAIL INBOX ANALYSIS RESULTS
=====================================

EMAILS BY CATEGORY:
Primary: 245 emails
Social: 89 emails  
Promotions: 412 emails

TOP 20 SENDERS (Total emails):
newsletter@company.com: 45 emails
  └─ Promotions: 45

notifications@social.com: 32 emails
  └─ Social: 32

updates@service.com: 28 emails
  └─ Primary: 28
```

## Troubleshooting

- **"Access blocked" error**: Add your email as a test user in OAuth consent screen
- **"Credentials not found"**: Ensure `credentials.json` is in the same folder as script
- **"Gmail API not enabled"**: Enable Gmail API in Google Cloud Console

## Requirements

- Python 3.7+
- Gmail account with API access
- Google Cloud project with Gmail API enabled

---

*This tool helps you identify email senders flooding your inbox so you can make informed decisions about unsubscribing or deleting emails.*