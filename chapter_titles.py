import argparse
from dotenv import load_dotenv
import json
import os
import sys
import openai
import random

from ask_openai import ask_openai
from GenresList import GENRES_LIST

load_dotenv()
# Set up OpenAI API credentials
openai.api_key = os.getenv('OPENAI_SECRET_KEY')

def output_to_file(is_dict, content, filename):
    with open(filename, "w") as f:
        if is_dict:
            json.dump(content, f)
        else:
            f.write(content)

def get_random_genre():
    random_genre = GENRES_LIST[random.randint(0, len(GENRES_LIST) - 1)]
    print("Genre is:", random_genre)
    return random_genre

def outline_generator(state):
    outline_prompt =  f"""
        Generate the outline of an original {state['desired_pages']}-page {state['plot_genre']} fiction book. 
        Imagine and then carefully label the following: a detailed plot, characters with names, settings 
        and writing style. You have {state['model']['token_limit'] - (40 + state['pad_amount'])} words remaining to write the outline. 
        It is CRITICAL you as many words as possible. DO NOT create a title!
        """
    print("Generating Outline...")

    outline = ask_openai(outline_prompt, 'writer', state['model']['name'], (state['model']['token_limit'] - (40 + state['pad_amount'])), 0.9)

    outline = outline.choices[0].message.content
    # print("Here is the raw outline:\n")
    # print(outline)
    return outline

def state_populator(state):
    print("\nPopulating state from raw outline...\n")

    items_to_populate = {
        'plot_outline': 'plot',
        'main_characters': 'main characters list',
        'minor_characters': 'minor characters list',
        'writing_style': 'writing style',
        'writing_adjectives': 'writing adjectives',
        'title': 'title',
    }

    for (key, value) in items_to_populate.items():
        state_populator_prompt = f"""
            I'm going to give you the outline of a book. From this outline, tell me the {value}. 
            Be sure to include plenty of detail while keeping it under {state['model']['token_limit']} tokens. 
            Here is the outline: {state['raw_outline']}`
        """

        state_populator_result = ask_openai(state_populator_prompt, 'machine', state['model']['name'], (state['model']['token_limit'] - (len(state['raw_outline']) + state['pad_amount'])), 0.9)
        state_populator_result = state_populator_result.choices[0].message.content;
        
        state[key] = state_populator_result

    state['filename'] = state['title']
    os.makedirs(state['filename'], exist_ok=True)
    output_to_file(True, state, f"{state['filename']}/{'state.json'}")
    return state

def plot_summary_by_chapter(state):
    print('\nGenerating chapter-by-chapter plot summary.\n')

    num_plot_outline_words = len(state['plot_outline'].split())
    chapter_summary_prompt = f"""
        You are writing a book with this plot summary: {state['plot_outline']}. The book is {state['desired_pages']} pages 
        long. Write a specific and detailed plot summary for each of the {state['num_chapters']} chapters of the book. 
        You must use at least a few paragraphs per chapter summary and can use up to one page or more per chapter. 
        Name any unnamed major or minor characters. Use the first few chapter summaries to introduce the characters 
        and set the story. Use the next few chapter summaries for action and character development. Use the last 
        few chapters for dramatic twists in the plot and conclusion. You have 
        {state['model']['token_limit'] - (num_plot_outline_words + 500 + state['pad_amount'])} tokens (or words) 
        left for the summaries. Try to use all the words you have available. 
    """

    chapter_summary_text = ask_openai(chapter_summary_prompt, 'writer', state['model']['name'], (state['model']['token_limit'] - (num_plot_outline_words + state['pad_amount'])), 0.9)
    chapter_summary_text = chapter_summary_text.choices[0].message.content
    # chapterSummaryText = chapterSummaryText.split(/\n/).filter((x) => x.length > 5);
    output_to_file(False, chapter_summary_text, f"{state['filename']}/{'chapter_summary.txt'}")
    
    return chapter_summary_text

def chapter_summary_array(state, starting_chapter=0):
    print("Generating chapter summary array...\n")

    for i in range(starting_chapter, state['num_chapters']):

        print(f"\nGenerating chapter summary for chapter {i + 1}...\n")

        num_plot_outline_words = len(state['plot_outline'].split())
        num_chapter_by_chapter_summary_words = len(state['chapter_by_chapter_summary_string'].split())
        chapter_summary_prompt = f"""
        You are writing a summary of chapter {i+1} of a {state['num_chapters']} chapters {state['plot_genre']} book. 
        The entire plot summary is {state['plot_outline']} 
        The chapter-by-chapter summary for the entire book is: \n{state['chapter_by_chapter_summary_string']}\n 
        Using those summaries, write a several page summary of only chapter {i+1}. Write the best summary you can, 
        you may add new subplots, character development, character background, planned dialogue and plot development 
        that you would typically find in such a work. You are NOT writing the actual book right now, you are writing 
        an outline and summary of what will happen in this chapter. 
        You have to write {state['model']['token_limit'] - (500 + num_plot_outline_words + num_chapter_by_chapter_summary_words + state['pad_amount'])} words.`
        """
        

        chapter_summary = ask_openai(chapter_summary_prompt, 'writer', state['model']['name'], (state['model']['token_limit'] - (num_plot_outline_words + num_chapter_by_chapter_summary_words + state['pad_amount'])), 0.9)
        chapter_summary = chapter_summary.choices[0].message.content
        state['chapter_summary_array'].append(chapter_summary)
        # chapterSummary = chapterSummary.split(/\n/).filter((x) => x.length > 5);
        output_to_file(False, chapter_summary, f"{state['filename']}/{'chapter_summary_'}{i + 1}.txt")
    
    return state['chapter_summary_array']    
    
def page_generator(state, starting_chapter=0, starting_page=0):
    print("\nEntering Page Generation module.\n")
    for i in range(starting_chapter, state['num_chapters']):
        for j in range(starting_page, state['chapter_length']):
            amendment = create_page_query_amendment(state, i, j);
            print(f"\nGenerating final full text for chapter {i+1} page {j+1}\n");
            page_gen_prompt = f"""
                You are an author writing page {j+1} in chapter {i+1} of a {state['num_chapters']}-chapter {state['plot_genre']} 
                novel. The plot summary for this chapter is {state['chapter_summary_array'][i]}. {amendment}. As you continue 
                writing the next page, be sure to develop the characters' background thoroughly, include dialogue and detailed 
                literary descriptions of the scenery, and develop the plot. Do not mention page or chapter numbers! Do not 
                jump to the end of the plot and make sure there is plot continuity. Carefully read the summaries of the prior 
                pages before writing new plot. Make sure you fill an entire page of writing.`
            """
            page_gen_text = ask_openai(page_gen_prompt, 'writer', state['model']['name'], (state['model']['token_limit'] - len(page_gen_prompt.split()) - state['pad_amount'] - 520), 0.9)
            page_gen_text = page_gen_text.choices[0].message.content
            state['full_text'].append(page_gen_text)
            header = f"\n\nChapter {i+1}, Page {j+1}\n\n"
            text_to_save = header + page_gen_text
            os.makedirs(f"{state['filename']}/pages", exist_ok=True)
            output_to_file(False, text_to_save, f"{state['filename']}/pages/chapter_{i+1}_page_{j+1}.txt")
            
            page_summary = generate_page_summary(state['full_text'][-1])
            state['page_summaries'].append(page_summary)
            os.makedirs(f"{state['filename']}/page_summaries", exist_ok=True)
            output_to_file(False, page_summary, f"{state['filename']}/page_summaries/summary_chapter_{i+1}_page_{j+1}.txt")
        starting_page=0
    return state['full_text'], state['page_summaries']

def generate_page_summary(page):
    page_summary_prompt = f"""
        Here is a full page of text. Please summarize it in a few sentences. 
        Text to summarize: ${page}
        """
    page_summary = ask_openai(page_summary_prompt, 'writer', state['model']['name'], (state['model']['token_limit'] - (len(page.strip()) + state['pad_amount'])), 0.5)
    page_summary = page_summary.choices[0].message.content
    return page_summary

def create_page_query_amendment(state, chapter, page):
    if page == 0:
        return "You are writing the first page of the chapter"
    elif page == 1 and state['model']['name'] == 'gpt-4-0314':
        return f"Page 1 of this chapter reads as follows: \n{state['full_text'][(chapter * state['chapter_length'] + page-2)]}\n"
    elif page == 2 and state['model']['name'] == 'gpt-4-0314':
        return f"Page {page-1} of this chapter reads as follows: \n{state['full_text'][(chapter *state['chapter_length'] + page-2)]}\n"
    
    prior_pages = '';

    for k in range(0, page):
        prior_pages = prior_pages + f"\nChapter {chapter+1}, Page {k+1}: {state['page_summaries'][(chapter * state['chapter_length'] + k)]}\n"

    if (page > 2 and state['model']['name'] == 'gpt-4-0314'):
        amendment = f"""
        Here are the page summaries of the chapter thus far: {prior_pages}. The full text of pages {page-2}, {page-1} 
        and {page} read as follows: 
        Page {page-2}: {state['full_text'][(chapter * state['chapter_length'] + page-3)]} 
        Page {page-1}: {state['full_text'][(chapter * state['chapter_length'] + page-2)]} 
        Page {page}: {state['full_text'][(chapter * state['chapter_length'] + page-1)]}
        """
    if (page > 0 and state['model']['name'] == 'gpt-3.5-turbo'):
        amendment = f"""
        Here are the page summaries of the chapter thus far: {prior_pages}. Here is the full text of page 
        {page}: {state['full_text'][(chapter * state['chapter_length'] + page-1)]}
        """

    return amendment;

# Main program logic
if __name__ == "__main__":
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='gpt4', help='Which openai model to use')
    parser.add_argument('--chapter_length', default=10, help='How many pages each chapter should be')
    parser.add_argument('--pages', default=100, help='Approximatly how many pages to generate')
    parser.add_argument('--pad_amount', default=500, help='')
    parser.add_argument('--genre', default='', help='Which genre to use')
    parser.add_argument('--start_with', default='', help='outline, state, chapter_by_chapter_summary_string, chapter_summary_array, page_summaries')
    parser.add_argument('--folder', default='', help='Which folder stores the current story.')
    args = parser.parse_args()

    models = {
        'gpt35': {
            'name': 'gpt-3.5-turbo',
            'token_limit': 4097,
        },
        'gpt4': {
            'name': 'gpt-4-0314',
            'token_limit': 8000,
        } 
    }

    state = {
        "title": '',
        "desired_pages": args.pages,
        "chapter_length": args.chapter_length,
        "num_chapters": int(args.pages / args.chapter_length),
        "plot_genre": '',
        "raw_outline": '',
        "plot_outline": '',
        "main_characters": [],
        "minor_characters": [],
        "writing_style": '',
        "writing_adjectives": '',
        "plot_settings": [],
        "chapter_by_chapter_summary_string": '',
        "chapter_summary_array": [],
        "filename": '',
        "full_text": [],
        "page_summaries": [],
        "model": models[args.model],
        'pad_amount': args.pad_amount,
    }
    state['plot_genre'] = get_random_genre() if args.genre == '' else args.genre
    ### Check if given folder exists
    state['filename'] = args.folder
    if not os.path.exists(state['filename']):
        print(f"Folder {state['filename']} does not exist")
        sys.exit(1)

    ### STATE
    with open(f"{state['filename']}/state.json", "r") as f:
        print(f"Loading {state['filename']}/state.json")
        state = json.load(f)

    for i in range(state['num_chapters']):
        if os.path.exists(f"{state['filename']}/chapter_summary_{i+1}.txt"):
            with open(f"{state['filename']}/chapter_summary_{i+1}.txt", "r") as f:
                state['chapter_summary_array'].append(f.read())

    state['chapter_titles'] = []    
    for chapter_summary in [state['chapter_summary_array'][-2], state['chapter_summary_array'][-1]]:
        prompt = f"""
        Given a plot summary of a chapter for a {state['plot_genre']} novel, create a creative title for the chapter.
        Here is the summary. {chapter_summary}"""
        response = ask_openai(prompt, 'writer', state['model']['name'], state['model']['token_limit'] - 2000, 0.9)
        state['chapter_titles'].append(response.choices[0].message.content)
        print('\n\n\n', state['chapter_titles'][-1])
        import time
        time.sleep(10)

    print(state['chapter_titles'])