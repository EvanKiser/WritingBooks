import os

# Set the folder path where the TXT files are located 
folder_path = "Title: Enchanted Desires: Secrets of the Moonlit Mansion/pages/"

# Set the name of the output DOCX file
output_file_name = "Title: Enchanted Desires: Secrets of the Moonlit Mansion/Enchanted Desires.txt"

text = ''
# Loop through each file in the folder
for chapter in range(1, 11):
    text += f"\nChapter {chapter}\n"
    for page in range(1, 11):
        filename = f"chapter_{chapter}_page_{page}.txt"
        
        # Open the TXT file and read its contents
        with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
            contents = f.read()
        # Add the contents of the TXT file to the Word document
        text += contents
print(text)
with open(output_file_name, 'w') as f:
    f.write(text)

print(f"All the pages have been combined into a single DOCX file named {output_file_name}.")