import os
import webbrowser
import google.genai as genai
from google.genai import types
from dotenv import load_dotenv
import markdown

# Assuming RESUME_PROMPT is defined in prompts.py
from prompts import RESUME_PROMPT

load_dotenv()


PATH_TO_RESUME = "All_Projects_Master_Resume.pdf"
OUTPUT_MD_FILE = "job_search_results.md"
OUTPUT_HTML_FILE = "job_search_results.html"

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# for model in client.models.list():
#     print(f"{model.name:<40}")

google_search_tool = types.Tool(
    google_search=types.GoogleSearch()
)

def find_relevant_jobs():
    """Analyze resume, find jobs, and save results with inline markdown links."""

    uploaded_file = client.files.upload(file=PATH_TO_RESUME)
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[uploaded_file, RESUME_PROMPT],
        config=types.GenerateContentConfig(
            tools=[google_search_tool],
            temperature=1.0,
            thinking_config=types.ThinkingConfig(
                include_thoughts=True, # This lets you access the "raw thoughts"
            )
        ),
    )


    full_text = response.text
    metadata = response.candidates[0].grounding_metadata
    thoughts = ""
    for part in response.candidates[0].content.parts:
        if part.thought:
            thoughts = part.text
            break

    if thoughts:
        print("--- MODEL THINKING ---")
        print(thoughts)
        print("----------------------")

    # 1. Create a mapping of chunk index to the clean URL
    links_map = {}
    sources_section = "\n---\n### Sources & References\n"

    # Add this to your find_relevant_jobs function
    if metadata and metadata.web_search_queries:
        print(f"DEBUG: Gemini attempted these searches: {metadata.web_search_queries}")

    if metadata and metadata.grounding_chunks:
        for i, chunk in enumerate(metadata.grounding_chunks):
            if chunk.web:
                title = chunk.web.title
                uri = chunk.web.uri
                # Store it (1-indexed for citation style)
                links_map[i + 1] = {"title": title, "url": uri}
                sources_section += f"{i+1}. [{title}]({uri})\n"
                
                # OPTIONAL: Replace [1] in text with [1](url) for "clean" inline clicking
                citation_marker = f"[{i+1}]"
                if citation_marker in full_text:
                    full_text = full_text.replace(citation_marker, f"[[{i+1}]]({uri})")
    else:
        sources_section += "No external search sources were cited."

    # 2. Assemble the final markdown
    output_content = f"# Job Search Results\n\n{full_text}\n{sources_section}"

    # 3. Write to file
    with open(OUTPUT_MD_FILE, "w", encoding="utf-8") as f:
        f.write(output_content)
    
    return f"Success! Results saved to {OUTPUT_MD_FILE}"
    

def main():
    print(find_relevant_jobs())
    
    # Write to file
    with open(OUTPUT_MD_FILE, "r", encoding="utf-8") as f:
        text = f.read()
        html = markdown.markdown(text)

    with open(OUTPUT_HTML_FILE, "w", encoding="utf-8") as f:
        f.write(f'<html><body style="font-family: sans-serif; padding: 40px;">{html}</body></html>')
    
    # Open the file in the default web browser
    webbrowser.open('file://' + os.path.realpath(OUTPUT_HTML_FILE))

if __name__ == "__main__":
    main()