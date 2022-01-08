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
    found_type = None
    found_content = None

    if 'title' in item:
        if search in item['title']:
            found = True
    if 'name' in item:
        if search in item['name']:
            found = True
    if 'subtitle' in item:
        if search in item['subtitle']:
            found = True
            found_type = 'subtitle'
    if 'description' in item:
        if search in item['description']:
            found_type = 'description'
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
                    found_type = 'file'
                    temp = content[index:index+30].replace("\r", "")
                    end_pos = temp.find('\n')
                    if(end_pos == -1):
                        end_pos = len(temp)
                    found_content = "Line {}: \"...{}...\"".format(content[:index].count('\n')+1, temp[:end_pos])
        except:
            pass


    if found:
        print("Found in "+item['origin_file'])
        print("    Type:  "+item['type'])
        print("    Title: "+item['title'])
        print("    Name:  "+item['name'])
        if 'file' in item:
            print("    File:  "+item['file'])
        if found_type == 'description':
            print("    \"{}\"".format(item['description']))
        if found_type == 'subtitle':
            print("    \"{}\"".format(item['subtitle']))
        if found_type == 'file':
            print("      {}".format(found_content))
        print()

