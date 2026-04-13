import os
import time
import requests
from google import genai # NEW: Updated library import!
from dotenv import load_dotenv

# ==========================================
# 1. SETUP: Securely Connect your AI
# ==========================================
load_dotenv()
my_api_key = os.getenv("GEMINI_API_KEY")
discord_url = os.getenv("DISCORD_WEBHOOK")

if not my_api_key:
    print("Error: Could not find GEMINI_API_KEY.")
    exit()

# NEW: Updated way to initialize the client
client = genai.Client(api_key=my_api_key)

def run_automation():
    print("Starting modern Top 5 automation workflow...")

    # ==========================================
    # 2. THE FETCH: Grab the top 5 stories
    # ==========================================
    try:
        top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        story_ids = requests.get(top_stories_url).json()
        top_5_ids = story_ids[:5] 

        stories_text_for_ai = ""
        for i, story_id in enumerate(top_5_ids, 1):
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            story_data = requests.get(story_url).json()
            
            title = story_data.get("title", "No title")
            link = story_data.get("url", "No link provided")
            
            print(f"Fetched #{i}: '{title}'")
            stories_text_for_ai += f"Story {i}:\nTitle: {title}\nLink: {link}\n\n"
            
    except Exception as e:
        print(f"Failed to fetch data: {e}")
        return

    # ==========================================
    # 3. THE LOGIC: Ask the AI to summarize
    # ==========================================
    prompt = f"""You are a tech analyst. Read the following 5 top tech news stories. 
    For each story, provide the Title as a Markdown header (linked to the URL), followed by exactly 2 short, punchy bullet points explaining why a developer would find it interesting.
    
    Here are the stories:
    {stories_text_for_ai}
    """
    
    # SAFETY FIX: Define the variable as empty first!
    ai_summary = None 
    max_attempts = 3
    
    print("Asking AI to summarize the batch...")
    for attempt in range(max_attempts):
        try:
            # NEW: Updated generation syntax
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
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

    # SAFETY FIX: If it failed all 3 times, quit gracefully so it doesn't crash!
    if not ai_summary:
        print("Error: Could not get a response from the AI after 3 attempts. Ending workflow.")
        return

    # ==========================================
    # 4. THE ACTION: Send to Discord
    # ==========================================
    if discord_url:
        print("Sending to Discord...")
        payload = {
            "content": f"## Today's Top 5 Tech Stories\n\n{ai_summary}"
        }
        try:
            requests.post(discord_url, json=payload)
            print("Success! Notification sent to Discord.")
        except Exception as e:
            print(f"Failed to send to Discord: {e}")
    else:
        print("Warning: No DISCORD_WEBHOOK secret found. Could not send message.")

if __name__ == "__main__":
    run_automation()