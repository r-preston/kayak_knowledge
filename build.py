#! /usr/bin/python

import json
import os
import os.path
import shutil
import pathlib
import datetime
import markdown
import re
import sys
import random

local = True
if len(sys.argv) > 1:
    if sys.argv[1] == 'sql':
        local = False

file_path = "content"
working_dir = str(pathlib.Path(__file__).parent.absolute())
url_base = '/'
show_sublevel_default = True

def objlistprint(l, level=0):
    print("{}[".format("  "*level))
    for x in l:
        if(type(x) is list):
            objlistprint(x, level+1)
        else:
            print("  {}{{".format("  "*level))
            for k,v in x.items():
                if(type(v) is list):
                    print("    {}{}: [...]".format("  "*level, k))
                else:
                    print("    {}{}: {}".format("  "*level, k, v))
            print("  {}}}".format("  "*level))
    print("{}]".format("  "*level))

def prettyprint(obj, level=0):
    if(level > 6):
        return
    try:
        for k,x in obj.items():
            if (type(x) is list) or (type(x) is dict):
                print("{}{}:".format("  "*level,k))
                prettyprint(x, level+2)
            else:
                print("{}{}: {}".format("  "*level,k,x))
        print()
    except:
        for x in obj:
            if (type(x) is list) or (type(x) is dict):
                prettyprint(x, level+1)
            else:
                print("{}{}".format("  "*level,x))

def find_children(obj):
    global categories, subcategories, pages

    filtered_pages = []
    filtered_subcats = []

    if obj == []:
        return obj

    if obj['type'] == 'category':
        filtered_subcats = [x for x in subcategories if ('categories' in x and obj['name'] in x['categories'])]
        filtered_pages = [x for x in pages if ('categories' in x and obj['name'] in x['categories'])]

    elif obj['type'] == 'subcategory':
        filtered_pages = [x for x in pages if ('subcategory' in x and obj['name'] == x['subcategory'])]

    return filtered_pages + filtered_subcats

def find_matching(name, obj_type):
    global categories, subcategories, pages, index

    matches = []
    if(obj_type == "category"):
        if(type(name) is list):
            matches = [x for x in (categories+[index]) if x['name'] in name]
        else:
            matches = [x for x in (categories+[index]) if x['name'] == name]
    if(obj_type == "subcategory"):
        matches = [x for x in subcategories if x['name'] == name]
    if(obj_type == "page"):
        matches = [x for x in pages if x['name'] == name]

    if len(matches) > 0:
        return matches[0]
    else:
        return []

def filter_redundant_subcategories(arr):
    return [x for x in arr if not ((x['type'] == 'subcategory') and (len(find_children(x)) < 2))]

def link_sort(val):
    if(val['type'] == "page"):
        return 0
    elif(val['type'] == "subcategory"):
        return 1
    else:
        return 2

def get_path(obj):
    global url_base, working_dir, local

    path_parts = []

    for i in range(0, len(obj['breadcrumb'])):
        if(type(obj['breadcrumb'][i]) is list):
            categories = [ x['url'] for x in obj['breadcrumb'][i] ]
            #categories.sort()
            #path_parts.append("_".join(categories))
            path_parts.append(categories[0])
        else:
            path_parts.append(obj['breadcrumb'][i]['url'])

    path_parts.append(obj['url'])

    path = "/".join(path_parts)

    if(local):
        path = working_dir + '/' + path
        if (obj['type'] == "page") or (obj['type'] == "sitemap"):
            path += ".html"
        else:
            path += "/index.html"
    else:
        path = url_base + path

    return path

def check_input(data, filename):
    """
        checks that required fields are set
    """
    global file_path
    for d in data:
        if (not 'name' in d) or (not isinstance(d['name'], str)) or d['name'] == '':
            print("-- ERROR --")
            print("entity without required field 'name' in file '{}'".format(filename))
            exit()
        if (not 'type' in d) or (not isinstance(d['type'], str)) or d['type'] == '':
            print("-- ERROR --")
            print("entity '{}' does not have required field 'type' in file '{}'".format(d['name'], filename))
            exit()
        if (not 'url' in d) or (not isinstance(d['url'], str)) or d['url'] == '':
            print("-- ERROR --")
            print("entity '{}' does not have required field 'url' in file '{}'".format(d['name'], filename))
            exit()
        if (not 'title' in d) or (not isinstance(d['title'], str)) or d['title'] == '':
            print("-- ERROR --")
            print("entity '{}' does not have required field 'title' in file '{}'".format(d['name'], filename))
            exit()

        if(d['type'] == "page"):
            if (not 'file' in d) or (not isinstance(d['file'], str)) or d['file'] == '':
                print("-- ERROR --")
                print("entity '{}' does not have required field 'file' in file '{}'".format(d['name'], filename))
                exit()
            if not os.path.isfile(file_path+"/"+d['file']):

                """
                # create file if not exists
                f = open(file_path+"/"+d['file'], 'w')
                f.write("TODO")
                f.close()
                """

                print("-- ERROR --")
                print("file '{}' specified for page '{}' in '{}' does not exist".format(d['file'], d['name'], filename))
                exit()

def page_header(obj):
    # create breadcrumb
    make_link = lambda item: '<a href="{}">{}</a>'.format(get_path(item), item['title'])
    bread_links = [make_link(x) if not type(x) is list else " / ".join([make_link(y) for y in x]) for x in obj['breadcrumb']]
    bread_links.append(obj['title'])
    head = " &#8250; ".join(bread_links)
    # add title
    head += '<h1>{}</h1>'.format(obj['title'])
    return head

def page_footer(obj, sitemap, search):
    foot = '<hr>'
    # add link to sitemap
    foot += 'Can\'t find what you\'re looking for? Try <a href="{}">searching</a> for it or check the <a href="{}">sitemap</a>.'.format(get_path(search), get_path(sitemap))
    foot += '<br>'
    # add last updated time
    now = datetime.datetime.now()
    foot += 'Last updated {}'.format(now.strftime("%d-%m-%Y"))
    # add contributors
    if 'contributors' in obj:
        foot += '<br>Contributors: '
        foot += ", ".join(obj['contributors'])
    return foot

def create_content(item):
    global index, sitemap, search, url_base

    item['content'] = '<div class="knowledgebase-page">'
    item['content'] += page_header(item)

    if(item['type'] == "page"):
        with open(file_path+"/"+item['file'], 'r') as markdown_file:
            data = markdown_file.read()
        html = markdown.markdown(data)
        # change image/video sources so they work (prepends working dir for development, forward slash for deploy)
        html = re.sub(r"(src=[\'\"])/?assets/?(.*?)([\'\"])", r"\1{}assets/{}/\2\3".format(working_dir+'/' if local else url_base, index['url']), html)
        item['content'] += html
    else:
        if 'description' in item:

            item['content'] += "<p>{}</p>".format(item['description'])

        item['content'] += '<ul>'
        for link in item['links_to']:
            item['content'] += '<li><a href="{}">{}</a>'.format(get_path(link), link['title'])
            if 'subtitle' in link:
                item['content'] += '<br><span>{}</span>'.format(link['subtitle'])
            item['content'] += '</li>'
        item['content'] += "</ul>"

    item['content'] += page_footer(item, sitemap, search)
    item['content'] += '</div>'

    # recurse onto linked pages
    for link in item['links_to']:
        create_content(link)

def create_sitemap(sitemap, index):
    global search
    sitemap['content'] = '<script>toggle_visible = function(btn, id) {{ var box = document.getElementById(id); if(box.style.display === "none") {{ box.style.display = ""; btn.innerHTML = "[&ndash;]" }} else {{ box.style.display = "none"; btn.innerText = "[+]" }} }}</script>'
    sitemap['content'] += '<div class="knowledgebase-page">'
    sitemap['content'] += page_header(sitemap)
    sitemap['content'] += site_tree(index)
    sitemap['content'] += page_footer(sitemap, sitemap, search)
    sitemap['content'] += '</div>'

def create_search(search, index):
    global sitemap
    search['content'] = '<div class="knowledgebase-page">'
    search['content'] += page_header(search)
    with open("search.md", 'r') as search_file:
        data = search_file.read()
    search['content'] += data
    search['content'] += page_footer(sitemap, sitemap, search)
    search['content'] += '</div>'

def site_tree(obj, prepend=''):
    whitespace = lambda width: '<span style="visibility:hidden">'+('&#9472;'*width)+'</span>'
    res = '<a href="'
    res += get_path(obj)
    res += '" style="'
    if (obj['type'] == "category"):
        res += "font-weight: bold; font-style:italic"
    elif (obj['type'] == "subcategory"):
        res += "font-weight: bold;"
    elif (obj['type'] == "index"):
        res += "font-weight: bold; font-size: 1.2em"
    res += '">'
    res += obj['title']
    sublevel_id = random.randint(0, sys.maxsize)
    res += "</a>"
    if len(obj['links_to']):
        res += "&ensp;<span style=\"cursor:pointer;text-decoration:underline;\"onclick='toggle_visible(this, \"{}\")'>[&ndash;]</span>".format(sublevel_id)
    res += "<br>"
    res += '<div id="{}">'.format(sublevel_id)
    # create sublevels
    for i in range(len(obj['links_to'])):
        res += prepend
        if (i < len(obj['links_to']) - 1):
            # ├────
            res += "&#9500;&#9472;&#9472;&#9472;&#9472;"
            res += site_tree(obj['links_to'][i], str(prepend+"&#9474;"+whitespace(4)))
        else:
            # └────
            res += "&#9492;&#9472;&#9472;&#9472;&#9472;"
            res += site_tree(obj['links_to'][i], str(prepend+whitespace(5)))
    res += "</div>"
    return res

json_data = []

# extract JSON data from all *.json files in the current directory
for file in os.listdir("./"):
    if file.endswith(".json"):
        with open(file, 'r') as jsonfile:
            try:
                data = jsonfile.read()
                json_data += json.loads(data)
            except:
                print("Syntax error for JSON in file "+file)
                exit();

        check_input(json_data, file)

categories =    [x for x in json_data if x['type'] == 'category'   ]
subcategories = [x for x in json_data if x['type'] == 'subcategory']
pages =         [x for x in json_data if x['type'] == 'page'       ]
index = {
    'type': 'index',
    'name': 'index',
    'title': 'Knowledge Base',
    'url': 'knowledge',
    'breadcrumb': [],
    'links_to': [],
    'display_in_menu': 1,
    'show_sublevel': False,
    'ordering': 4
}
# special page that shows the heirarchy of the knowledge base
# it is not explicitly linked in this script, a special link to it will appear on every finished page
sitemap = {
    'type': 'sitemap',
    'name': 'sitemap',
    'title': 'Knowledge Base Sitemap',
    'url': 'sitemap',
    'breadcrumb': [index],
    'links_to': []
}
# special search page
search = {
    'type': 'search',
    'name': 'search',
    'title': 'Search the Knowledge Base',
    'url': 'search',
    'breadcrumb': [index],
    'links_to': []
}


# create connections for pages
for item in pages:
    item['breadcrumb'] = []
    item['links_to'] = []

    # if subcategory set and subcategory links to more than one page, add to breadcrumb
    # (if subcategory links to only one page it is collapsed)
    if ('subcategory' in item) and len(find_children(find_matching(item['subcategory'],'subcategory'))) > 1:
        item['breadcrumb'].append(find_matching(item['subcategory'],'subcategory'))

    # if category set and category links to more than one item, add to breadcrumb
    # (if category links to only one item it is collapsed)
    linked_categories = []

    # look for directly linked categories or categories linked via subcategory
    if 'categories' in item:
        linked_categories = [find_matching(cat, 'category') for cat in item['categories']]
    if 'subcategory' in item:
        if 'categories' in find_matching(item['subcategory'], 'subcategory'):
            linked_categories = [find_matching(cat, 'category') for cat in find_matching(item['subcategory'], 'subcategory')['categories']]

    # filter out categories with only a single child (collapse redundant categories)
    linked_categories = [x for x in linked_categories if len(filter_redundant_subcategories(find_children(x))) > 1]

    if len(linked_categories) > 0:
        item['breadcrumb'] = ([linked_categories] if len(linked_categories) > 1 else linked_categories) + item['breadcrumb']

    # add top level page to breadcrumb
    item['breadcrumb'] = [index] + item['breadcrumb']

# create connections for subcategories
for item in subcategories:
    item['breadcrumb'] = [index]


    # subcategories can only link upwards to either the index or categories
    linked_categories = []
    if 'categories' in item:
        linked_categories = [find_matching(cat, 'category') for cat in item['categories']]
        linked_categories = [x for x in linked_categories if len(find_children(x)) > 1]
    if len(linked_categories) > 0:
        item['breadcrumb'] = item['breadcrumb'] + ([linked_categories] if len(linked_categories) > 1 else linked_categories)


    # subcategories can only link downwards to pages
    # note: no collapsing as pages can't have further downward connections anyway
    item['links_to'] = find_children(item)

    # sort in this order: pages > subcategories > categories
    item['links_to'].sort(key=link_sort)

# create connections for subcategories
for item in categories:
    # can only link to top level page
    item['breadcrumb'] = [index]

    # link to any of children that have more than one child themselves
    # if linking to something with only one child, try again with that child

    # step 1: find children
    children = find_children(item)
    # step 2: filter out subcategories with no children as they do nothing
    children = [x for x in children if ((len(find_children(x)) > 0) or (x['type'] == 'page'))]
    # step 3: collapse subcategories with one child only
    for i in range(0, len(children)):
        if len(find_children(children[i])) == 1:
            children[i] = find_children(children[i])[0]


    item['links_to'] = children

    # sort in this order: pages > subcategories > categories
    item['links_to'].sort(key=link_sort)


# create connections for index page
# will gather all items that only have the index page in their breadcrumb and then prune
consider = [x for x in (pages+subcategories+categories) if len(x['breadcrumb']) == 1]
# now remove anything with only one child
consider = [x for x in consider if len(filter_redundant_subcategories(find_children(x))) > 1 or x['type'] == "page"]

index['links_to'] = consider
index['links_to'].sort(key=link_sort, reverse=True)


# construct HTML page content
# this is a recursive function that will be called on each item in 'links_to'
# this means redundant pages are not constructed
create_content(index)
create_sitemap(sitemap, index)
create_search(search, index)


# check uniqueness of names and urls, ignoring redundant pages
url_list = [get_path(sitemap), get_path(search)]
track_list = [sitemap['name'], search['name']]
for x in categories:
    if not 'content' in x:
        continue
    if x['name'] in track_list:
        print("-- ERROR --")
        print("{} '{}': name is already in use. please choose a unique name".format(x['type'], x['name']))
        exit()
    else:
        track_list.append(x['name'])

    if get_path(x) in url_list:
        print("-- ERROR --")
        print("{} '{}': url '{}' is not unique. please change url to ensure it is unique".format(x['type'], x['name'], get_path(x)))
        exit()
    else:
        url_list.append(get_path(x))

track_list = [sitemap['name'], search['name']]
for x in subcategories:
    if not 'content' in x:
        continue
    if x['name'] in track_list:
        print("-- ERROR --")
        print("{} '{}': name is already in use. please choose a unique name".format(x['type'], x['name']))
        exit()
    else:
        track_list.append(x['name'])

    if get_path(x) in url_list:
        print("-- ERROR --")
        print("{} '{}': url '{}' is not unique. please change url to ensure it is unique".format(x['type'], x['name'], get_path(x)))
        exit()
    else:
        url_list.append(get_path(x))

track_list = [sitemap['name'], search['name']]
for x in pages:
    if not 'content' in x:
        continue
    if x['name'] in track_list:
        print("-- ERROR --")
        print("{} '{}': name is already in use. please choose a unique name".format(x['type'], x['name']))
        exit()
    else:
        track_list.append(x['name'])

    if get_path(x) in url_list:
        print("-- ERROR --")
        print("{} '{}': url '{}' is not unique. please change url to ensure it is unique".format(x['type'], x['name'], get_path(x)))
        exit()
    else:
        url_list.append(get_path(x))





if local:

    # delete previous build
    try:
        shutil.rmtree('./'+index['url']+"/")
    except:
        pass

    # write pages
    for x in [index]+[sitemap]+[search]+categories+subcategories+pages:
        if 'content' in x:
            filename = get_path(x)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as f:
                f.write(x['content'])

    print("HTML data written to '{}/'".format(index['url']))

else:

    with open('knowledge_pages.sql', "w") as f:
        f.write('DELETE FROM `pages` WHERE url LIKE "/{}%";\n\n'.format(index['url']))

        for x in [index]+[sitemap]+[search]+categories+subcategories+pages:
            if 'content' in x:
                f.write('''
INSERT INTO `pages`
(
    `name`,
    `url`,
    `category`,
    `menudisplay`,
    `content`,
    `ordering`,
    `everyone`,
    `pleb`,
    `exec`,
    `admin`
)
VALUES ("{}", "{}", "{}", {}, "{}", {}, 1, 0, 0, 0);
'''.format(
    x['title'].replace('"','""'),
    get_path(x),
    x['menu_category'] if 'menu_category' in x else "Canoe",
    x['display_in_menu'] if 'display_in_menu' in x else 0,
    x['content'].replace('"','""'),
    x['ordering'] if 'ordering' in x else 0

))

        print("SQL data written to 'knowledge_pages.sql'")