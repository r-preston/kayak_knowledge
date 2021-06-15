#! /usr/bin/python

import json
import os
import sys

search = ''
if len(sys.argv) > 1:
    search = sys.argv[1]
else:
    print('What am I meant to search for, muggins')
    exit()

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
                if search in content:
                    found = True
        except:
            pass


    if found:
        print("Found in "+item['origin_file'])
        print("    Type:  "+item['type'])
        print("    Title: "+item['title'])
        print("    Name:  "+item['name'])
        if 'file' in item:
            print("    File:  "+item['file'])
        print()

