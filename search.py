import arxivpy
from datetime import datetime, timedelta
import pytz
import os
import markdown

"""

Arxiv Sanity Preserver:
1. Search for everyday papers according to max_results
2. Update everyday results into json file that save all arxiv paper of past (papers overlaped with last day will be removed)
3. Present json file into markdown file reversed by time

Json_data: [{date:date1, papers: [{k1:v1, k2:v2, ...} ]}, {date:date2, papers: [{k1:v1, k2:v2, ...} ]}, ...]

"""
import datetime
import requests
import json
import arxiv
import re

base_url = "https://arxiv.paperswithcode.com/api/v0/papers/"


def del_unicode(string):
    string = re.sub(r'\\u.{4}', '', string.__repr__())
    return string


def del_not_english(string):
    string = re.sub('[^A-Za-z]', '', string.__str__())
    return string


def get_authors(authors, first_author=False):
    output = str()
    if first_author == False:
        output = ", ".join(str(author) for author in authors)
    else:
        output = authors[0]
    return output


def sort_papers(papers):
    output = dict()
    keys = list(papers.keys())
    keys.sort(reverse=True)
    for key in keys:
        output[key] = papers[key]
    return output


def get_daily_papers(max_results=100):
    """
    @param topic: str
    @param query: str
    @return paper_with_code: dict
    """

    # output
    content = []

    articles = arxivpy.query(search_query=['cs.CV'],
                            start_index=0, max_index=max_results, results_per_iteration=100,
                            wait_time=1.0, sort_by='lastUpdatedDate') # grab 200 articles


    cnt = 0

    for result in articles:

        # dict_keys(['id', 'term', 'terms', 'main_author', 'authors', 'url', 'pdf_url', 'title', 'abstract', 'update_date', 'publish_date', 'comment', 'journal_ref'])

        # id and url
        paper_id = result['id']
        paper_url = result['url']
        paper_pdf_url = result['pdf_url']

        # title and abstract
        paper_title = result['title']
        paper_abstract = result['abstract']

        # authors
        paper_authors = result['authors']
        paper_first_author = result['main_author']
        paper_first_end_author = paper_authors.split(', ')[0] + '; ' + paper_authors.split(', ')[-1]

        # time
        publish_time = result['publish_date']
        update_time = result['update_date']

        print("Time = ", update_time,
              " title = ", paper_title,
              " author = ", paper_first_author)

        # eg: 2108.09112v1 -> 2108.09112
        ver_pos = paper_id.find('v')
        if ver_pos == -1:
            paper_key = paper_id
        else:
            paper_key = paper_id[0:ver_pos]

        # content[paper_key] = f"|**{update_time}**|**{paper_title}**|{paper_first_end_author} et.al.|[{paper_id}]({paper_pdf_url})|'null'|\n"
        paper = {'id': paper_key, 'url':paper_url, 'pdf_url': paper_pdf_url, 'title': paper_title, 
        'abs':paper_abstract, 'authors': paper_authors, 'first_author': paper_first_author, 'first_end_author':paper_first_end_author,
        'publish_time': str(publish_time), 'update_time': str(update_time)}
        content.append(paper)

    return content


def update_json_file(filename, everyday_data):
    # if filename not exist, create it
    if os.path.exists(filename) == False:
        with open(filename, "w") as f:
            json.dump([], f)

    with open(filename, "r+") as f:
        content = f.read()
        if not content:
            m = []
        else:
            m = json.loads(content)

    json_data = m.copy()

    DateNow = datetime.date.today()
    DateNow = str(DateNow)
    DateNow = DateNow.replace('-', '.')

    assert DateNow not in [data['date'] for data in json_data], "daily already exist"

    if json_data:
        last_ids = [paper['id'] for paper in json_data[-1]['papers']]
        filter_everyday_data = [paper for paper in everyday_data if paper['id'] not in last_ids]
        json_data.append({'date':DateNow, 'papers':filter_everyday_data})
    else:
        json_data.append({'date':DateNow, 'papers':everyday_data})
    

    with open(filename, "w") as f:
        json.dump(json_data, f)


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

    md_filename = "README.md"


    # write data into README.md
    with open(md_filename, "w+", encoding='utf-8') as f:
        for idx, data_day in enumerate(data[::-1]):

            f.write("## Updated on " + data_day['date'] + "\n\n")

            # the head of each part
            f.write(f"## Computer Vision\n\n")

            f.write("|Publish Date|Title|Authors|PDF|Code|\n" + "|---|---|---|---|---|\n")

            for paper in data_day['papers']:
                v = f"|**{paper['update_time']}**|**{paper['title']}**|{paper['first_end_author']} et.al.|[{paper['id']}]({paper['pdf_url']})|'null'|\n"
                f.write(v)

            f.write(f"\n")

    print("finished")

def json2html(filename):
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

    html_filename = "arxiv.html"
    total_paper = len([paper for data_day in data for paper in data_day['papers']])
    paper_idx = 0
    # write data into README.md
    with open(html_filename, "w+", encoding='utf-8') as f:
        for _, data_day in enumerate(data[::-1]):

            # f.write("## Updated on " + data_day['date'] + "\n\n")
            f.write("<!DOCTYPE html> \n")
            f.write("<html> \n")
            f.write("<h2>Updated on " + data_day['date'] + "</h2> \n")

            # the head of each part
            f.write(f"<h2> Computer Vision </h2> \n")

            # f.write("|Publish Date|Title|Authors|PDF|Code|\n" + "|---|---|---|---|---|\n")
            day_paper_num = len(data_day['papers'])
            for idx, paper in enumerate(data_day['papers']):
                strs = ''
                # strs += f'<dt><a name="item1">' + f'[{total_paper-day_paper_num+idx+1}]' + '</a>&nbsp;  <span class="list-identifier"><a href="' + f'{paper["url"]}' +'" title="Abstract">arXiv:'+f"{paper['id']}"+'</a> [<a href="'+f'{paper["pdf_url"]}'+'" title="Download PDF">pdf</a>]</span></dt> \n'
                # strs += '<dd> \n'
                strs += '<div class="meta"> \n'
                strs += '<div class="list-title mathjax"> \n'
                strs += f'<span class="descriptor"><h3><a name="item1">' + f'[{total_paper-day_paper_num+idx+1}] ' + f'</a></span> {paper["title"]} [<a href="' + f'{paper["url"]}' +'" title="Abstract">arXiv:'+f"{paper['id']}"+'</a>] [<a href="'+f'{paper["pdf_url"]}'+'" title="Download PDF">pdf</a>]</h3> \n'
                strs += '</div> \n'
                strs += '<div class="list-authors"> \n'
                strs += '<span class="descriptor"><strong>Authors:</strong></span> \n'
                strs += paper['authors'] + '\n'
                strs += '</div> \n'
                strs += '<br />' + '\n'
                strs += '<div class="list-abs"> \n'
                # <span class="descriptor"><strong>Abstract:</strong></span> 
                strs += '<span class="descriptor"><strong>Abstract:</strong></span> \n'
                strs += paper['abs'] + '\n'
                strs += '</div> \n'
                strs += '</div> \n'
                # strs += '</dd> \n'
                strs += '</dt> \n'
                strs += '<br />' + '\n'
                f.write(strs)
                paper_idx += 1

            f.write(f"\n")

    print("finished")



if __name__ == "__main__":

    # get max data accourding to the max_results
    everyday_data = get_daily_papers(max_results=200)


    # update README.md file
    json_file = "cv-arxiv-daily.json"
    # update json data
    update_json_file(json_file, everyday_data)
    # json data to markdown
    json2html(json_file)

    # # update docs/index.md file
    # json_file = "./docs/nlp-arxiv-daily-web.json"
    # #     if ~os.path.exists(json_file):
    # #         with open(json_file,'w')as a:
    # #             print("create " + json_file)

    # # update json data
    # update_json_file(json_file, data_collector)
    # # json data to markdown
    # json_to_md(json_file, to_web=True)

