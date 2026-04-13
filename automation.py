import os
import time
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
    print("Error: Could not find GEMINI_API_KEY.")
    exit()

genai.configure(api_key=my_api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

def run_automation():
    print("Starting Top 5 automation workflow...")

    # ==========================================
    # 2. THE FETCH: Grab the top 5 stories
    # ==========================================
    try:
        top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        story_ids = requests.get(top_stories_url).json()
        top_5_ids = story_ids[:5] # This slices the list to grab the first 5

        # We will store the combined text here to send to the AI later
        stories_text_for_ai = ""

        # Loop through each of the 5 IDs to get their details
        for i, story_id in enumerate(top_5_ids, 1):
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            story_data = requests.get(story_url).json()
            
            title = story_data.get("title", "No title")
            link = story_data.get("url", "No link provided")
            
            print(f"Fetched #{i}: '{title}'")
            
            # Add this story to our growing text block
            stories_text_for_ai += f"Story {i}:\nTitle: {title}\nLink: {link}\n\n"
            
    except Exception as e:
        print(f"Failed to fetch data: {e}")
        return

    # ==========================================
    # 3. THE LOGIC: Ask the AI to summarize the batch
    # ==========================================
    prompt = f"""You are a tech analyst. Read the following 5 top tech news stories. 
    For each story, provide the Title as a Markdown header (linked to the URL), followed by exactly 2 short, punchy bullet points explaining why a developer would find it interesting.
    
    Here are the stories:
    {stories_text_for_ai}
    """
    
    print("Asking AI to summarize the batch...")
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
    # 4. THE ACTION: Save the combined summary
    # ==========================================
    try:
        with open("summary.md", "w", encoding="utf-8") as file:
            file.write("## Today's Top 5 Tech Stories\n\n")
            file.write(ai_summary)

        print("Success! Summary saved locally to summary.md")
    except Exception as e:
        print(f"Failed to save file: {e}")

if __name__ == "__main__":
    run_automation()