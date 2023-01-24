import arxivpy
from datetime import datetime, timedelta
import pytz
import os
import markdown
import json

"""

Save everyday new paper into corresponding markdown file

"""
def json_to_md(filename):
    """
    @param filename: str
    @return None
    """

    with open(filename, "r") as f:
        content = f.read()
        if not content:
            data = {}
        else:
            data = json.loads(content)

    md_filename = f"markdowns/{data[-1]['date']}.md"

    # judge if md_filename exist in the markdowns directory
    if os.path.exists(md_filename):
        print(f"{md_filename} already exist")
        return None


    # write data into README.md
    with open(md_filename, "a+", encoding='utf-8') as f:
        for idx, data_day in enumerate(data[-1:]):

            f.write("## Updated on " + data_day['date'] + "\n")

            # the head of each part
            f.write(f"## Computer Vision\n\n")

            f.write("|Publish Date|Title|Authors|PDF|Code|\n" + "|---|---|---|---|---|\n")

            for i, paper in enumerate(data_day['papers']):
                print()
                print(f'[{i+1}] {paper["title"]}')
                print()
                print(f'Authors: {paper["first_end_author"]}')
                print()
                print(f'Abstract: {paper["abs"]}')
                print()
                save = input("Save? (Space for save, Enter for skip)")
                # if save == ' ', save it, if save == '', skip it, and input any others will repeat the question
                while save != ' ' and save != '' and save != 'q':
                    save = input("Save? (Space for save, Enter for skip)")
                if save == ' ':
                    v = f"|**{paper['update_time']}**|**{paper['title']}**|{paper['first_end_author']} et.al.|[{paper['id']}]({paper['pdf_url']})|{paper['abs']}|\n"
                    f.write(v)
                    print("Saved")
                elif save == '':
                    print("Skipped")
                    continue
                elif save == 'q':
                    print("Quit")
                    return True


            f.write(f"\n")

    print("finished")
    return True

if __name__ == "__main__":
    json_file = "cv-arxiv-daily.json"
    ret = json_to_md(json_file)