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
    # 3. THE LOGIC (Updated to ask for Markdown instead of HTML)
    # ==========================================
    import time
    prompt = f"You are a tech analyst. Explain why a developer might find this news interesting. Keep it to 2 short, punchy bullet points. Use standard Markdown formatting. Title: '{title}'. Link: {link}."
    
    print("Asking AI to summarize...")
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            response = model.generate_content(prompt)
            ai_summary = response.text
            break 
        except Exception as e:
            error_message = str(e)
            if "429" in error_message or "Quota" in error_message:
                print(f"API is busy. Waiting 60 seconds... (Attempt {attempt + 1} of {max_attempts})")
                time.sleep(60) 
            else:
                print(f"Failed to generate AI summary: {e}")
                return

    # ==========================================
    # 4. THE ACTION: Save as a simple Markdown file
    # ==========================================
    try:
        # We save it as "summary.md" so the GitHub Action can easily find it
        with open("summary.md", "w", encoding="utf-8") as file:
            file.write(f"## [{title}]({link})\n\n")
            file.write("### AI Analyst Summary\n")
            file.write(ai_summary)

        print("Success! Summary saved locally to summary.md")
    except Exception as e:
        print(f"Failed to save file: {e}")

if __name__ == "__main__":
    run_automation()