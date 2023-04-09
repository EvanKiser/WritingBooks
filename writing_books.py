from dotenv import load_dotenv
import os
import openai
import requests

load_dotenv()
# Set up OpenAI API credentials
openai.api_key = os.getenv('OPENAI_SECRET_KEY')

# Define the prompt you want to generate text from
prompt = "In the style of {author}, write a story about Evan and Carli kissing for the first time."

# Define the OpenAI API parameters
params = {
    "prompt": prompt,
    "temperature": 0.7, # Controls the "creativity" of the generated text
    "max_tokens": 1024, # Controls the length of the generated text
    "stop": "\n", # Stops the generation at the first newline character
}

# Fine-tune the GPT-3 model on your favorite author's writing
def fine_tune_model(author_text):
    model_id = "gpt-4" # Change this to the model you want to fine-tune
    prompt = f"Fine-tune the {model_id} model on {author}'s writing:\n\n{author_text}"
    response = openai.Completion.create(
        engine=model_id,
        prompt=prompt,
        temperature=0.7,
        max_tokens=1024,
        n=1,
        stop=None,
    )
    return response.choices[0].text

# Generate text using the fine-tuned model
def generate_text(prompt, model_id):
    messages=[{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model_id,
        messages=messages,
        # temperature=0.7,
        max_tokens=1024,
        # n=1,
        # stop=None,
    )
    return response.choices[0].text

# Download your favorite author's works
def download_author_works(author):
    # Use web scraping or APIs to get the author's works
    # For example, you could use the Project Gutenberg API to download ebooks
    return author

# Send the generated text to a file
def output_to_file(text, filename):
    with open(filename, "w") as f:
        f.write(text)

# Main program logic
if __name__ == "__main__":
    author = "Collen Hoover" # Change this to your favorite author
    # author_text = download_author_works(author)
    # fine_tuned_model_id = fine_tune_model(author_text)
    # generated_text = generate_text(prompt, fine_tuned_model_id)
    generated_text = generate_text(prompt, "gpt-4")
    # output_to_file(generated_text, "book.txt")
    print(generated_text)
