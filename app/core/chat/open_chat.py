import os
from dotenv import load_dotenv # Import this
from openai import OpenAI
from utils.utils import logger
import httpx

# Load the .env file at the top of your file
load_dotenv()

class OpenChat:
    def __init__(self) -> None:
        self.api_key = os.getenv("GOOGLE_API_KEY")

        http_client = httpx.Client(proxies=None)
        # Ensure the base_url ends with 'openai/'
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

    def chat(self, messages):
        # Update the model string to match the name from your API response
        completion = self.client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=messages,
            stream=False
        )
        
        result = completion.choices[0].message.content
        return result

if __name__ == "__main__":
    oc = OpenChat()
    
    # Test scenario in English
    raw_messages = [
        {"chatMessageId": "m00001", "role": "system", "rawContent": "You are a helpful medical assistant."},
        {"chatMessageId": "m00002", "role": "user", "rawContent": "I have a cold, what medicine should I take?"},
        {"chatMessageId": "m00003", "role": "assistant", "rawContent": "You could try some over-the-counter cold relief medicine."},
        {"chatMessageId": "m00004", "role": "user", "rawContent": "I tried that and it doesn't seem to be working."}
    ]
    
    messages = [
        {"role": x.get('role').lower(), "content": x.get("rawContent")}
        for x in raw_messages
    ]
    
    print(f"Formatted Messages: {messages}")
    oc.chat(messages)