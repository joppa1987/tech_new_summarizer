import os
import requests
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

# ==========================================
# 1. SETUP: Securely Connect your AI
# ==========================================
load_dotenv()
my_api_key = os.getenv("GEMINI_API_KEY")

if not my_api_key:
    print("Error: Could not find GEMINI_API_KEY. Make sure your .env file exists and is formatted correctly.")
    exit()

genai.configure(api_key=my_api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

def run_automation():
    print("Starting secure automation workflow...")

    # ==========================================
    # 2. THE FETCH: Grab live data from Hacker News
    # ==========================================
    try:
        top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        story_ids = requests.get(top_stories_url).json()
        top_story_id = story_ids[0]

        story_url = f"https://hacker-news.firebaseio.com/v0/item/{top_story_id}.json"
        story_data = requests.get(story_url).json()
        
        title = story_data.get("title", "No title")
        link = story_data.get("url", "No link provided")
        print(f"Fetched top story: '{title}'")
        
    except Exception as e:
        print(f"Failed to fetch data: {e}")
        return

    # ==========================================
    # 3. THE LOGIC: Send data to AI (with Auto-Retry)
    # ==========================================
    import time # Make sure this is at the top of your file!
    
    prompt = f"You are a tech analyst. Explain why a developer might find this news interesting. Keep it to 2 short, punchy bullet points. Format the response strictly in HTML using <ul>, <li>, and <strong> tags. Do not use Markdown. Title: '{title}'. Link: {link}."
    
    print("Asking AI to summarize...")
    
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            response = model.generate_content(prompt)
            ai_summary = response.text
            break # If it succeeds, break out of the retry loop!
            
        except Exception as e:
            error_message = str(e)
            if "429" in error_message or "Quota" in error_message:
                print(f"API is busy (Rate Limit). Waiting 60 seconds before trying again... (Attempt {attempt + 1} of {max_attempts})")
                time.sleep(60) # Pauses the script for 1 minute
            else:
                print(f"Failed to generate AI summary with a different error: {e}")
                return

    # ==========================================
    # 4. THE ACTION: Save the output as a styled HTML file
    # ==========================================
    date_str = datetime.now().strftime('%Y-%m-%d')
    date_display = datetime.now().strftime('%B %d, %Y')
    filename = f"daily_tech_summary_{date_str}.html"
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
            font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #f4f6f9;
            color: #2c3e50;
            margin: 0;
            padding: 40px;
            display: flex;
            justify-content: center;
        }}
        .container {{
            background-color: #ffffff;
            padding: 40px;
            border-top: 8px solid #3498db;
            border-radius: 6px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            max-width: 800px;
            width: 100%;
        }}
        .date {{
            font-size: 11pt;
            color: #7f8c8d;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 12px;
        }}
        h1.title {{
            font-size: 24pt;
            color: #1a252f;
            margin: 0 0 10px 0;
            line-height: 1.3;
        }}
        .link {{
            font-size: 10pt;
            color: #95a5a6;
            margin-bottom: 30px;
            border-bottom: 1px solid #ecf0f1;
            padding-bottom: 20px;
        }}
        .link a {{
            color: #3498db;
            text-decoration: none;
        }}
        h2.summary-header {{
            font-size: 15pt;
            color: #2c3e50;
            border-left: 4px solid #e74c3c;
            padding-left: 12px;
            margin-top: 30px;
            margin-bottom: 20px;
        }}
        .content {{
            font-size: 11pt;
            line-height: 1.7;
            color: #34495e;
        }}
    </style>
    </head>
    <body>
        <div class="container">
            <div class="date">Daily Tech Summary • {date_display}</div>
            <h1 class="title">{title}</h1>
            <div class="link">Source: <a href="{link}" target="_blank">{link}</a></div>

            <h2 class="summary-header">AI Analyst Summary</h2>
            <div class="content">
                {ai_summary}
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(html_template)

        print(f"Success! Workflow complete. Summary saved securely to {filename}")
    except Exception as e:
        print(f"Failed to save file: {e}")

if __name__ == "__main__":
    run_automation()