from dotenv import load_dotenv
import os
import openai
import requests
from datetime import datetime

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
    response = openai.ChatCompletion.create(
        model=model_choice,
        messages=[{"role": "system", "content": role_content}, {"role": "user", "content": prompt}],
        temperature=temp,
        max_tokens=tokens,
    )
    print(f"OpenAI Response Time: {datetime.now() - now} ms")
    return response