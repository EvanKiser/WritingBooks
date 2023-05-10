from dotenv import load_dotenv
import os
import openai
from datetime import datetime

load_dotenv()
# Set up OpenAI API credentials
openai.api_key = os.getenv('OPENAI_SECRET_KEY')

prompt = """Generate the outline of a contemporary romance fiction novel. 
        The characters should be multidimensional and relastic in such a way that readers can connect with them on an emotional level.
        Dialogue should be authentic, natural, and conversational. Be sure to balance wit, humor, and vulnerability in dialogue.
        Explore themes such as love, relationships, personal struggles, trauma, and mental health with sensitivity and depth.
        Develop engaging and well-paced plots with suspense and unexpected twists that keep readers engaged.
        The writing style should be in the style should be fluid and easy to read. Adopt a conversational tone but also include introspection, descriptive language, and vivid imagery to enhance the storytelling.
        Imagine and then carefully label the following: a detailed plot, characters with names, settings 
        and writing style. The plot should include lots of sexual interactions between many different 
        characters.
        """
role_content = "You are the best seeling fiction author Cooleen Author"
temp = 0.6
tokens = 5000

now = datetime.now()
print(now)
response = openai.ChatCompletion.create(
    model='gpt-4-0314',
    messages=[{"role": "system", "content": role_content}, {"role": "user", "content": prompt}],
    temperature=temp,
    max_tokens=tokens,
)
print(f"OpenAI Response Time: {datetime.now() - now} ms")
print(response.choices[0].message.content)