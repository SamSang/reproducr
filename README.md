A class project to analyze data availablility accross PubMed Central

## Getting Started

I suggest two tools to get started:
- `git`
- `uv`

### git

Git is a version control utility. It's worth it to use git so we can all work on the same copy of code. We don't need to paste text to a forum page or email files. Git fits all of our changes together.

### uv

`uv` is a python code manager. It talks to that `pyproject.toml` file. It can install python if you tell it to. I will figures out what version of python to use and install the extra code this project needs. It's better than alternatives, in my opinion.

## `config.json`

Various files reference `config.json`. This is a file you'll need to create in this folder to store text that we don't want to be public on GitHub. It should have this structure:

```json
{
    "User-Agent": "Mozilla/5.0 (compatible; reproducr/0.1.0; +mailto:xx@psu.edu)",
    "ncbi-api-key": "it'sasecret",
    "tool_name": "reproducr",
    "version": "0.1.0",
    "email": "xx@psu.edu",
    "postgres": {
        "user": "secret",
        "pw": "supersecret",
        "host": "something.amazonaws.com",
        "db_name": "wouldn'tyouliketoknow"
    }
}
```

To run this locally, I suggest 
- getting an api key for the pubmed database and
- look at Matt's note and fill in the postgres secrets.

## Structure

The `main.py` script is intended to run and collect all of the data for our project, then load it to the shared AWS postgres database. It has several dependencies:

- `pubmed.py`
- `parser.py`
- `database.py`

There are other files, but they are from earlier iterations of the project.

It's helpful to keep code that does one kind of thing in one file. This helps us stay organized.

### pubmed

This file connects to the pubmed api and returns data that we want.

### parser

This file accepts the output from the pubmed api and transforms it to the format we want to store in our database.

### database

This file accepts data from the parser and stores it in our database.

There's also a folder named `postgres`. We can store our sql files in there, so we're not storing sql code in-line in our python code.