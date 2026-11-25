import sqlite3
from datetime import date, timedelta
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DB_PATH = Path(__file__).with_name("library.db")
LOAN_DAYS = 14
DAILY_FINE = 5
MIN_MATCH_SCORE = 0.10


BOOKS = [
    ("The Hobbit", "J.R.R. Tolkien", "Fantasy", "9780547928227", 3, "Bilbo Baggins leaves his comfortable home to join a quest filled with dragons and dwarves. It is a warm adventure about courage, friendship, and unexpected heroism."),
    ("Dune", "Frank Herbert", "Science Fiction", "9780441172719", 2, "Paul Atreides navigates politics and survival on the desert planet Arrakis. The novel explores ecology, power, prophecy, and the risks of messianic belief."),
    ("To Kill a Mockingbird", "Harper Lee", "Historical Fiction", "9780061120084", 2, "Scout Finch recalls a childhood shaped by a landmark trial in a divided Southern town. The story examines justice, prejudice, empathy, and moral courage."),
    ("Pride and Prejudice", "Jane Austen", "Classic Romance", "9780141439518", 2, "Elizabeth Bennet challenges the assumptions and social expectations of Regency-era England. Her evolving relationship with Mr. Darcy explores pride, class, and first impressions."),
    ("The Silent Patient", "Alex Michaelides", "Mystery", "9781250301703", 2, "A celebrated painter becomes mute after being accused of murdering her husband. A psychotherapist investigates the silence, seeking a truth hidden behind uncertainty."),
    ("The Alchemist", "Paulo Coelho", "Fable", "9780061122415", 3, "A young shepherd follows his dreams across desert roads in search of a treasure. The fable emphasizes personal purpose, perseverance, and listening to one's inner calling."),
    ("Sapiens", "Yuval Noah Harari", "History", "9780062316097", 2, "This history traces humanity's development from hunter-gatherer groups to modern societies. It examines how shared stories and institutions have shaped civilizations."),
    ("The Song of Achilles", "Madeline Miller", "Mythology", "9780062060624", 2, "Patroclus tells the story of his close bond with the warrior Achilles and their role in the Trojan War. The novel blends Greek mythology with themes of love, loyalty, and fate."),
    ("Atomic Habits", "James Clear", "Self-Help", "9780735211292", 3, "Small, consistent improvements can compound into meaningful long-term change. The book presents practical methods for shaping habits and improving daily systems."),
    ("The Martian", "Andy Weir", "Science Fiction", "9780553418026", 2, "An astronaut stranded on Mars survives through ingenuity, science, and determination. The story combines technical problem-solving with humor and teamwork."),
]

MEMBERS = [
    ("Aarav Sharma",),
    ("Meera Patel",),
    ("Kabir Khan",),
]

POLICIES = [
    ("Loan Policy", f"Books may be borrowed for {LOAN_DAYS} days. The due date is {LOAN_DAYS} days after the loan is issued."),
    ("Fine Policy", f"Late returns incur a fine of {DAILY_FINE} rupees per day after the due date. The fine is not charged for an on-time or early return."),
    ("Renewal Policy", f"An eligible loan may be renewed once for another {LOAN_DAYS} days. Renewals are not allowed for overdue books or when another member is waiting."),
    ("Lost Books Policy", f"A lost book must be reported promptly. The member must pay the book's replacement cost; any outstanding late fine at the rate of {DAILY_FINE} rupees per day is also payable."),
    ("Membership Policy", "Membership is available to registered library members. Members must present their member ID when borrowing or returning books."),
    ("Opening Hours Policy", "The library is open Monday through Saturday from 9:00 AM to 6:00 PM."),
]


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                genre TEXT NOT NULL,
                isbn TEXT NOT NULL UNIQUE,
                total_copies INTEGER NOT NULL,
                available_copies INTEGER NOT NULL,
                description TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                issued_at TEXT NOT NULL,
                due_at TEXT NOT NULL,
                returned_at TEXT,
                fine INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (member_id) REFERENCES members(id),
                FOREIGN KEY (book_id) REFERENCES books(id)
            );

            CREATE TABLE IF NOT EXISTS library_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                text TEXT NOT NULL
            );
            """
        )

        if connection.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 0:
            connection.executemany(
                """
                INSERT INTO books
                    (title, author, genre, isbn, total_copies, available_copies, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (title, author, genre, isbn, copies, copies, description)
                    for title, author, genre, isbn, copies, description in BOOKS
                ],
            )

        if connection.execute("SELECT COUNT(*) FROM members").fetchone()[0] == 0:
            connection.executemany(
                "INSERT INTO members (name) VALUES (?)",
                MEMBERS,
            )

        if connection.execute("SELECT COUNT(*) FROM library_documents").fetchone()[0] == 0:
            documents: list[tuple[str, str]] = [
                (
                    f"{title} ({genre})",
                    f"{title} is a {genre.lower()} book by {author}. {description}",
                )
                for title, author, genre, _isbn, _copies, description in BOOKS
            ]
            connection.executemany(
                "INSERT INTO library_documents (source, text) VALUES (?, ?)",
                documents,
            )

        policy_sources = (
            "Loan Policy",
            "Fine Policy",
            "Renewal Policy",
            "Lost Books Policy",
            "Membership Policy",
            "Opening Hours Policy",
            "Availability Policy",
        )
        placeholders = ",".join("?" for _ in policy_sources)
        connection.execute(
            f"DELETE FROM library_documents WHERE source IN ({placeholders})",
            policy_sources,
        )
        connection.executemany(
            "INSERT INTO library_documents (source, text) VALUES (?, ?)",
            POLICIES,
        )


def list_books(connection: sqlite3.Connection) -> None:
    rows = connection.execute(
        "SELECT id, title, author, genre, available_copies, total_copies FROM books ORDER BY id"
    ).fetchall()
    print("\nBooks:")
    for row in rows:
        print(
            f"{row['id']}. {row['title']} by {row['author']} "
            f"[{row['genre']}] - {row['available_copies']}/{row['total_copies']} available"
        )


def list_members(connection: sqlite3.Connection) -> None:
    rows = connection.execute("SELECT id, name FROM members ORDER BY id").fetchall()
    print("\nMembers:")
    for row in rows:
        print(f"{row['id']}. {row['name']}")


def issue_book_for(connection: sqlite3.Connection, member_id: int, book_id: int) -> tuple[bool, str]:
    member = connection.execute("SELECT id FROM members WHERE id = ?", (member_id,)).fetchone()
    book = connection.execute(
        "SELECT title, available_copies FROM books WHERE id = ?", (book_id,)
    ).fetchone()
    if member is None:
        return False, "Member not found."
    if book is None:
        return False, "Book not found."
    if book["available_copies"] < 1:
        return False, f"No copies of '{book['title']}' are currently available."

    issued = date.today()
    due = issued + timedelta(days=LOAN_DAYS)
    with connection:
        connection.execute(
            """
            INSERT INTO loans (member_id, book_id, issued_at, due_at)
            VALUES (?, ?, ?, ?)
            """,
            (member_id, book_id, issued.isoformat(), due.isoformat()),
        )
        connection.execute(
            "UPDATE books SET available_copies = available_copies - 1 WHERE id = ?",
            (book_id,),
        )
    return True, f"Issued '{book['title']}'. Due date: {due.isoformat()}."


def issue_book(connection: sqlite3.Connection) -> None:
    list_members(connection)
    list_books(connection)
    try:
        member_id = int(input("Member ID: ").strip())
        book_id = int(input("Book ID: ").strip())
    except ValueError:
        print("Please enter numeric IDs.")
        return
    success, message = issue_book_for(connection, member_id, book_id)
    print(message)


def return_loan(connection: sqlite3.Connection, loan_id: int, returned_on: date | None = None) -> tuple[bool, str, int]:
    loan = connection.execute(
        """
        SELECT loans.id, loans.book_id, loans.due_at
        FROM loans
        WHERE loans.id = ? AND loans.returned_at IS NULL
        """,
        (loan_id,),
    ).fetchone()
    if loan is None:
        return False, "Active loan not found.", 0

    returned = returned_on or date.today()
    due = date.fromisoformat(loan["due_at"])
    late_days = max((returned - due).days, 0)
    fine = late_days * DAILY_FINE
    with connection:
        connection.execute(
            """
            UPDATE loans
            SET returned_at = ?, fine = ?
            WHERE id = ?
            """,
            (returned.isoformat(), fine, loan_id),
        )
        connection.execute(
            "UPDATE books SET available_copies = available_copies + 1 WHERE id = ?",
            (loan["book_id"],),
        )
    return True, f"Book returned. Fine: {fine} rupees.", fine


def return_book(connection: sqlite3.Connection) -> None:
    rows = connection.execute(
        """
        SELECT loans.id, members.name, books.title, loans.due_at
        FROM loans
        JOIN members ON members.id = loans.member_id
        JOIN books ON books.id = loans.book_id
        WHERE loans.returned_at IS NULL
        ORDER BY loans.id
        """
    ).fetchall()
    print("\nActive loans:")
    for row in rows:
        print(f"{row['id']}. {row['name']} - {row['title']} (due {row['due_at']})")
    if not rows:
        return

    try:
        loan_id = int(input("Loan ID: ").strip())
    except ValueError:
        print("Please enter a numeric loan ID.")
        return
    _success, message, _fine = return_loan(connection, loan_id)
    print(message)


def build_search_index(connection: sqlite3.Connection) -> tuple[TfidfVectorizer, object, list[sqlite3.Row]]:
    documents = connection.execute(
        "SELECT source, text FROM library_documents"
    ).fetchall()
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    searchable_text = [f"{row['source']} {row['text']}" for row in documents]
    matrix = vectorizer.fit_transform(searchable_text) if documents else None
    return vectorizer, matrix, documents


def ask(question: str, connection: sqlite3.Connection | None = None) -> list[tuple[str, str, float]]:
    if not question.strip():
        return []

    owns_connection = connection is None
    connection = connection or get_connection()
    try:
        vectorizer, matrix, documents = build_search_index(connection)
        if matrix is None or not documents:
            return []

        question_matrix = vectorizer.transform([question.strip()])
        similarities = cosine_similarity(question_matrix, matrix).flatten()
        top_indices = similarities.argsort()[::-1][:3]
        if float(similarities[top_indices[0]]) < MIN_MATCH_SCORE:
            return []
        matches = [
            (
                documents[index]["source"],
                documents[index]["text"],
                float(similarities[index]),
            )
            for index in top_indices
            if similarities[index] >= MIN_MATCH_SCORE
        ]
        return matches
    finally:
        if owns_connection:
            connection.close()


def ask_library(connection: sqlite3.Connection) -> None:
    question = input("Ask the library: ").strip()
    if not question:
        print("Please enter a question.")
        return

    matches = ask(question, connection)
    if not matches or matches[0][2] < MIN_MATCH_SCORE:
        print("I couldn't find that in the library catalog or policies.")
        return

    print("\nRelevant information:")
    for source, text, score in matches:
        print(f"- {text} [Source: {source}, Score: {score:.3f}]")


def print_menu() -> None:
    print(
        "\nLibrary Menu\n"
        "1. Ask\n"
        "2. Catalog\n"
        "3. Issue\n"
        "4. Return\n"
        "5. Quit"
    )


def main() -> None:
    init_db()
    with get_connection() as connection:
        while True:
            print_menu()
            choice = input("Choose an option: ").strip()
            choice = choice.lower()
            if choice in ("1", "ask"):
                ask_library(connection)
            elif choice in ("2", "catalog"):
                list_books(connection)
            elif choice in ("3", "issue"):
                issue_book(connection)
            elif choice in ("4", "return"):
                return_book(connection)
            elif choice in ("5", "quit"):
                print("Goodbye.")
                break
            else:
                print("Invalid option.")


if __name__ == "__main__":
    main()
