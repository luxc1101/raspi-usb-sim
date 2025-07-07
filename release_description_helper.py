import re
import sys

import markdown

changelog_path = "CHANGELOG.md"

def find_version_in_changelog(changelog_path, version):
    # Read the content of the markdown file
    try:
        with open(changelog_path, 'r', encoding='utf-8') as file:
            changelog_content = file.readlines()
    except FileNotFoundError:
        print(f"Error: The changelog file '{changelog_path}' does not exist.")
        return None

    pattern = f"#### {version}"

    start_index = None
    for index, line in enumerate(changelog_content):
        if re.search(pattern, line):  # Case-sensitive search
            start_index = index
            break  

    if start_index is None:
        print(f"Pattern '{version}' not found in the changelog.")
        return None

    section = changelog_content[start_index:]

    section_text = ''.join(section)

    return section_text

def convert_markdown_to_html(markdown_text):
    html = markdown.markdown(markdown_text)

    html_content = '\n' +  html.replace('\n', '').replace('\r', '')

    return html_content

if __name__ == "__main__":
    version = 'version' + ' ' + str(sys.argv[1]).split('v')[-1]
    section_text = find_version_in_changelog(changelog_path, version)
    if section_text:
        print(convert_markdown_to_html(section_text))