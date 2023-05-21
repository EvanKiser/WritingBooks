import os
from dotenv import load_dotenv
import anthropic
from datetime import datetime

load_dotenv()
# Set up OpenAI API credentials
client = anthropic.Client(os.getenv('ANTHROPIC_SECRET_KEY'))
def ask_anthropic(prompt):
    now = datetime.now()
    response = client.completion(
        prompt=f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}",
        stop_sequences = [anthropic.HUMAN_PROMPT],
        model="claude-v1",
        max_tokens_to_sample=5000,
    )
    print(f"Anthropic Response Time: {datetime.now() - now} ms")
    print(response['completion'])
    return response['completion']