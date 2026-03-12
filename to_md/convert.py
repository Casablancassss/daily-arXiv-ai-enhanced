import json
import argparse
import os
from itertools import count


def escape_template_chars(text):
    """
    Escape characters that could cause template formatting issues.
    Handles { and } which are used by str.format() by doubling them.
    Also handles backslash-escaped braces.
    """
    if not text:
        return ''
    # First, normalize backslash-escaped braces
    text = str(text).replace(r'\{', '{').replace(r'\}', '}')
    # Then double all braces for str.format()
    return text.replace('{', '{{').replace('}', '}}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, help="Path to the jsonline file")
    args = parser.parse_args()
    data = []
    preference = os.environ.get('CATEGORIES', 'cs.CV, cs.CL').split(',')
    preference = list(map(lambda x: x.strip(), preference))
    def rank(cate):
        if cate in preference:
            return preference.index(cate)
        else:
            return len(preference)

    with open(args.data, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line))

    # Safely get categories with default handling
    categories = set()
    for item in data:
        cats = item.get("categories", [])
        if cats:
            categories.add(cats[0])

    # Safely read template file
    try:
        with open("paper_template.md", "r", encoding="utf-8") as f:
            template = f.read()
    except FileNotFoundError:
        print("Error: paper_template.md not found", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error reading template file: {e}", file=sys.stderr)
        sys.exit(1)

    categories = sorted(categories, key=rank)
    cnt = {cate: 0 for cate in categories}
    for item in data:
        cats = item.get("categories", [])
        if not cats:
            continue
        primary_cat = cats[0]
        if primary_cat in cnt:
            cnt[primary_cat] += 1

    markdown = f"<div id=toc></div>\n\n# Table of Contents\n\n"
    for idx, cate in enumerate(categories):
        markdown += f"- [{cate}](#{cate}) [Total: {cnt[cate]}]\n"

    idx = count(1)
    for cate in categories:
        markdown += f"\n\n<div id='{cate}'></div>\n\n"
        markdown += f"# {cate} [[Back]](#toc)\n\n"
        papers = []
        for item in data:
            cats = item.get("categories", [])
            if not cats or cats[0] != cate:
                continue

            # Safely access AI fields with default values
            ai_data = item.get('AI', {})
            if not ai_data or not isinstance(ai_data, dict):
                print(f"Skipping item '{item.get('title', 'Unknown')}' due to missing or invalid AI data")
                continue

            # Check if all required AI fields are present
            required_fields = ['tldr', 'motivation', 'method', 'result', 'conclusion']
            if not all(field in ai_data for field in required_fields):
                print(f"Skipping item '{item.get('title', 'Unknown')}' due to incomplete AI fields")
                continue

            papers.append(
                template.format(
                    title=escape_template_chars(item.get("title", "Untitled")),
                    authors=escape_template_chars(",".join(item.get("authors", []))),
                    summary=escape_template_chars(item.get("summary", "")),
                    url=item.get('abs', item.get('url', '')),
                    tldr=escape_template_chars(ai_data.get('tldr', '')),
                    motivation=escape_template_chars(ai_data.get('motivation', '')),
                    method=escape_template_chars(ai_data.get('method', '')),
                    result=escape_template_chars(ai_data.get('result', '')),
                    conclusion=escape_template_chars(ai_data.get('conclusion', '')),
                    cate=cats[0],
                    idx=next(idx)
                )
            )
        markdown += "\n\n".join(papers)
    with open(args.data.split('_')[0] + '.md', "w", encoding="utf-8") as f:
        f.write(markdown)