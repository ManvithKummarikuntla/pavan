# Library RAG Project

## Goal
Small library management system with a RAG-based "Ask the Library" feature.
This is a basic test project, so keep it simple.

## Rules
- NO external APIs, no API keys, no internet at runtime.
- No LLM. Answers are built from retrieved text only.
- Language: Python 3. Database: SQLite. Retrieval: TF-IDF (scikit-learn).
- Keep the code in as few files as possible, with short comments.
- Use type hints and simple error handling.
- Don't add features I didn't ask for.
- After each step, run the code and test it before saying it's done.

## Features
- Books, members and loans stored in SQLite
- Issue a book (14-day loan, refuse if no copies)
- Return a book (fine of 5 rupees per late day)
- Ask questions about books and library policies, with sources shown

## Run
python library_rag.py