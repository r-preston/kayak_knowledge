# Warwick Canoe Knowledge Base

## About

This is a collection of varied short articles and resources intended to overhaul the Warwick Canoe Website's existing informational pages.

It covers a wide variety of topics, mainly whitewater kayaking, however much is applicable to other disciplines.

These resources do not replace proper safety and leadership qualifications, but are hopefully a good starting point and place to discover new things or refresh memories.

## Structure

Content is distributed among many `pages`. Each `page` belongs to a single `subcategory`, and each `subcategory` belongs to one or more `categories`. Navigation therefore goes `index` > `category` > `subcategory` > `page`.

Data for each level is stored in a corresponding `.json` file, which can be compiled into a set of linked up `.html` files with `build.py`. Content for each page is written in github-flavoured markdown in a file like `content/{name}.md`, the name of which is specified in `pages.json`

Note: categories and subcategories are collapsed if they have only one child: for example if a subcategory has only one associated page then any references to that subcategory will map directly to the page instead.

All images/videos should be placed in `resources/` and linked using relative paths

## Usage

- Create structure in `categories.json`, `subcategories.json` or `pages.json`.
- Create content in markdown files located in `content/`
- Use `build.py` to compile into `html` heirarchy in `knowledge/`
- `todo.py` locates 'TODO' in any markdown files. Writing TODO at any point therefore leaves a marker which anyone can find and come back to
- `search.py` searches markdown files for matches to a given string
- All images/videos should be placed in `resources/` and linked using relative paths


