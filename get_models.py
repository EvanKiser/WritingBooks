from dotenv import load_dotenv
import os
import openai
import requests

load_dotenv()
# Set up OpenAI API credentials
openai.api_key = os.getenv('OPENAI_SECRET_KEY')

# Get a list of all the models
models = openai.Model.list()
print(models)
