import library_rag


TESTS = [
    ("How many days is the loan period?", "Loan Policy"),
    ("What is the fine for a late return?", "Fine Policy"),
    ("Can I renew a borrowed book?", "Renewal Policy"),
    ("What happens when a book is lost?", "Lost Books Policy"),
    ("How do I become a member?", "Membership Policy"),
    ("When is the library open?", "Opening Hours Policy"),
    ("Which book is about survival on Mars?", "The Martian (Science Fiction)"),
    ("Quantum cooking recipes for dolphins", "No match"),
]


def main() -> None:
    library_rag.init_db()
    connection = library_rag.get_connection()
    passed = 0

    print("| # | Question | Expected top source | Actual top source | Score | Result |")
    print("|---|---|---|---|---:|---|")
    for number, (question, expected) in enumerate(TESTS, 1):
        matches = library_rag.ask(question, connection)
        if matches:
            actual, _text, score = matches[0]
        else:
            actual, score = "No match", 0.0
        is_pass = actual == expected
        passed += is_pass
        print(
            f"| {number} | {question} | {expected} | {actual} | "
            f"{score:.3f} | {'PASS' if is_pass else 'FAIL'} |"
        )

    connection.close()
    print(f"\nPassed: {passed}/{len(TESTS)}")


if __name__ == "__main__":
    main()
