# Library RAG Project

An offline, terminal-based library management system built with Python and SQLite.
It uses TF-IDF to search a small catalog of books and library policies without an
LLM or external API.

## Setup

1. Install Python 3.
2. Open a terminal in this project folder.
3. Create and activate a virtual environment:

```text
python -m venv .venv
.venv\Scripts\activate
```

4. Install dependencies:

```text
pip install -r requirements.txt
```

## Run

Start the application:

```text
python library_rag.py
```

Start the Streamlit web interface:

```text
streamlit run app.py
```

Run the RAG test script:

```text
python test_rag.py
```

## Features

- SQLite storage for books, members, loans, and searchable documents
- 10 sample books across different genres
- 3 sample members
- 14-day borrowing periods
- A fine of 5 rupees per late day
- Book issue and return operations
- Catalog and policy search with TF-IDF
- Source names and similarity scores in search results
- Terminal menu: Ask, Catalog, Issue, Return, and Quit

## Limitations

Search is keyword-based rather than semantic: TF-IDF compares word overlap and
cannot reliably understand paraphrases, synonyms, or question intent. A query
may miss relevant information or rank a loosely related document first. It does
not use an LLM, so answers are limited to the catalog descriptions and policy
text in the database. The application is intentionally small and has no internet
services or API keys.
