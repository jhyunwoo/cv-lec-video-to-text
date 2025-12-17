import os
import time
from google import genai
from google.genai import types

# --------------------------------------------------------------------------
# --- Setup ---
# --------------------------------------------------------------------------
# Using the same API key as main.py
API_KEY = os.environ["GEMINI_API_KEY"]

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3-pro-preview"

def summarize_text(text):
    """Summarizes the given text using the Gemini model."""
    if not text or text.strip() == "":
        return "No text to summarize."

    print("🤖 Sending request to Gemini for summarization...")
    
    prompt = f"""
    Please summarize the following lecture content.
    Summarize the key points and main ideas in a structured way (e.g., using bullet points).
    Write the summary in Korean.
    
    Lecture Content:
    {text}
    """

    max_retries = 5
    for attempt in range(max_retries):

            try:
                response = client.models.generate_content(
                    model=MODEL_NAME, 
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=1.0
                    )
                )
                return response.text
            except Exception as e:
                print(e)
                # User asked to judge based on response content/error match
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    
                    wait_time = 30 * (2 ** attempt) # 30s, 60s, 120s...
                    print(f"⚠️ Quota exceeded (429). Waiting {wait_time} seconds before retrying (Attempt {attempt + 1}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    return f"❌ Error during summarization: {e}"
    
    return "❌ Failed to summarize after multiple retries due to quota exhaustion."
    

def process_files():
    text_dir = "./text"
    summary_dir = "./summary"
    
    if not os.path.exists(text_dir):
        print(f"❌ '{text_dir}' directory not found.")
        return

    # Create summary directory if it doesn't exist
    if not os.path.exists(summary_dir):
        os.makedirs(summary_dir)
        print(f"📂 Created '{summary_dir}' directory.")

    files = [f for f in os.listdir(text_dir) if f.endswith("_original.txt")]
    files.sort()

    if not files:
        print("⚠️ No '_original.txt' files found.")
        return

    print(f"📂 Found {len(files)} files to summarize.")

    for i, filename in enumerate(files):
        print(f"\n[{i+1}/{len(files)}] Processing: {filename}")
        
        file_path = os.path.join(text_dir, filename)
        # Change output filename and path
        summary_filename = filename.replace("_original.txt", "_summary.md")
        summary_file_path = os.path.join(summary_dir, summary_filename)

        # Skip if summary already exists? (Optional, but good for resuming)
        # For now, I'll overwrite or just run it.
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            summary = summarize_text(content)
            
            with open(summary_file_path, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            print(f"✅ Summary saved to: {summary_filename}")
            
        except Exception as e:
            print(f"❌ Failed to process {filename}: {e}")
        
        # Rate limiting
        if i < len(files) - 1:
            print("⏳ Waiting 1 seconds before next file...")
            time.sleep(1)

if __name__ == "__main__":
    process_files()
