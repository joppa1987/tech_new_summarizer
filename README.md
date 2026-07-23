# Tech News Summarizer

Automated Python workflow that pulls top stories from Hacker News, generates concise developer-focused summaries using Google Gemini, and posts the results to Discord via webhook.

## Features

- Fetches the **Top 5 Hacker News** stories in real time
- Builds an AI prompt from fetched titles and links
- Uses **Gemini 2.5 Flash** to generate short, punchy analysis
- Retries on temporary API quota/rate issues
- Optionally posts output directly to a Discord channel
- Includes sample generated outputs (`.txt` and `.html`)

---

## Project Structure

```text
tech_new_summarizer/
├── automation.py                          # Main automation script
├── daily_tech_summary_2026-04-13.txt      # Example plaintext output
├── daily_tech_summary_2026-04-13.html     # Example styled HTML output
└── .github/workflows/                     # CI/CD automation workflows (if configured)
```

---

## How It Works

1. Load secrets from environment variables (`.env`)
2. Request top story IDs from Hacker News API
3. Fetch metadata for the top 5 stories
4. Send a structured prompt to Gemini for summarization
5. Post formatted output to Discord (if webhook is configured)

---

## Requirements

- Python 3.10+
- A Google Gemini API key
- (Optional) Discord webhook URL

### Python dependencies

Install required packages:

```bash
pip install requests python-dotenv google-genai
```

---

## Configuration

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
DISCORD_WEBHOOK=your_discord_webhook_url_here
```

- `GEMINI_API_KEY` is required
- `DISCORD_WEBHOOK` is optional (script will still run without it, but won’t post to Discord)

---

## Usage

Run the automation script:

```bash
python automation.py
```

Expected console flow:

- Fetch top stories
- Generate AI summary
- Send to Discord (if webhook is set)

---

## Example Output

The repository includes example generated summaries:

- `daily_tech_summary_2026-04-13.txt`
- `daily_tech_summary_2026-04-13.html`

These show the intended output style and formatting.

---

## Error Handling

`automation.py` currently includes safeguards for:

- Missing API key
- Hacker News fetch failures
- Gemini quota/rate-limit retries (up to 3 attempts)
- Missing Discord webhook
- Discord post failures

---

## Security Notes

- Never commit your `.env` file
- Rotate API keys if accidentally exposed
- Prefer repository or CI secret managers for production use

---

## Roadmap Ideas

- Add `requirements.txt` for reproducible installs
- Save daily summaries automatically with date-based filenames
- Add CLI flags (e.g., number of stories, output format)
- Add unit tests and linting
- Schedule daily runs via GitHub Actions cron
- Export summaries to email/Slack/Notion

---

## License

No license file is currently present in this repository.  
If you plan to open-source this project, add a license such as MIT.

---

## Author

Maintained by [@joppa1987](https://github.com/joppa1987)
