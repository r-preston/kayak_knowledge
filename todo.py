#! /usr/bin/python

import json
import os
import sys

searches = ['TODO','todo']

# extract JSON data from all *.json files in the current directory
json_data = []
for file in os.listdir("./"):
    if file.endswith(".json"):
        with open(file, 'r') as jsonfile:
            try:
                data = jsonfile.read()
                json_data += json.loads(data)
                for i in range(0, len(json_data)):
                    if not 'origin_file' in json_data[i]:
                        json_data[i]['origin_file'] = file
            except:
                print("Syntax error for JSON in file "+file)
                exit();


for item in json_data:
    found = False
    found_line = None

    for search in searches:

        if 'title' in item:
            if search in item['title']:
                found = True
        if 'name' in item:
            if search in item['name']:
                found = True
        if 'subtitle' in item:
            if search in item['subtitle']:
                found = True
        if 'description' in item:
            if search in item['description']:
                found = True
        if 'url' in item:
            if search in item['url']:
                found = True
        if 'file' in item:
            try:
                with open('content/'+item['file'], 'r') as contentfile:
                    content = contentfile.read()
                    index = content.find(search)
                    if index > -1:
                        found = True
                        found_line = content[:index].count('\n')+1
            except:
                pass


    if found:
        print("Found in "+item['origin_file'])
        print("    Type:  "+item['type'])
        print("    Title: "+item['title'])
        print("    Name:  "+item['name'])
        if 'file' in item:
            if found_line is not None:
                print("    File:  {} (line {})".format(item['file'], found_line))
            else:
                print("    File:  "+item['file'])
        print()

