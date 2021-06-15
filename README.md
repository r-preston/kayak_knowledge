# Warwick Canoe Knowledge Base

## About

This is a collection of varied short articles and resources intended to overhaul the Warwick Canoe Website's existing informational pages.

It covers a wide variety of topics, mainly whitewater kayaking, however much is applicable to other disciplines.

These resources do not replace proper safety and leadership qualifications, but are hopefully a good starting point and place to discover new things or refresh memories.

## Structure

Content is distributed among many `pages`. Each `page` belongs to a single `subcategory`, and each `subcategory` belongs to one or more `categories`. Navigation therefore goes `index` > `category` > `subcategory` > `page`.

Data for each level is stored in `.json` files, which can be compiled into a set of linked up `.html` files with `build.py`. Content for each page is written in github-flavoured markdown in a file like `content/{name}.md`, the name of which is specified in thre JSON

Note: categories and subcategories are collapsed if they have only one child: for example if a subcategory has only one associated page then any references to that subcategory will map directly to the page instead.

All images/videos should be placed in `assets/knowledge/` and linked using relative paths (e.g. `src="assets/knowledge/image.jpg"`)

## Usage

- Create structure in `.json` files in the same directory as `build.py`.
- Create content in markdown files located in `content/`
- Use `build.py` to compile data into a linked heirarchy of pages
  - By default `build.py` compiles a collection of HTML pages in `knowledge/`
  - When passed the command line argument `sql` (`> ./build.py sql`) then it compiles a SQL script with data in the correct format to be inserted into the Warwick Canoe website's database
- `todo.py` locates 'TODO' in any markdown files. Writing TODO at any point therefore leaves a marker which anyone can find and come back to
- `search.py` searches markdown files for matches to a given string
- All images/videos should be placed in `assets/` and linked using relative paths


