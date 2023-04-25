from dotenv import load_dotenv
import os
import openai
import requests
from datetime import datetime
import time
import sys

load_dotenv()
# Set up OpenAI API credentials
openai.api_key = os.getenv('OPENAI_SECRET_KEY')

def ask_openai(prompt, role, model_choice='gpt-3.5-turbo', tokens=5000, temp=0.85):
    role_content="You are a ChatGPT-powered chat bot"

    if role == 'machine':
        role_content="You are a computer program attempting to comply with the user's wishes."
    elif role == 'writer':
        role_content="""
            You are a professional fiction writer who is a best-selling author. 
            You use all of the rhetorical devices you know to write a compelling book.
        """
    now = datetime.now()
    num_retries = 0
    max_retry = 3
    while num_retries < max_retry:
        try:
            response = openai.ChatCompletion.create(
                model=model_choice,
                messages=[{"role": "system", "content": role_content}, {"role": "user", "content": prompt}],
                temperature=temp,
                max_tokens=tokens,
            )
        except openai.error.Timeout:
            print("Timeout occurred. Retrying in {} seconds...".format(2 ** num_retries))
            num_retries += 1
            time.sleep(2 ** num_retries)
    if num_retries > max_retry:
        print("Max retries reached. Aborting...")
        sys.exit(1)
    print(f"OpenAI Response Time: {datetime.now() - now} ms")
    return response