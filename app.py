import streamlit as st

import library_rag


library_rag.init_db()

st.set_page_config(page_title="Library RAG", page_icon="📚", layout="wide")
st.title("Library RAG")

tab_ask, tab_catalog, tab_issue, tab_return = st.tabs(
    ["Ask", "Catalog", "Issue", "Return"]
)

with tab_ask:
    question = st.text_input("Ask about a book or library policy")
    if st.button("Search", type="primary"):
        if not question.strip():
            st.warning("Enter a question.")
        else:
            matches = library_rag.ask(question)
            if not matches:
                st.error(
                    "I couldn't find that in the library catalog or policies."
                )
            else:
                for source, text, score in matches:
                    st.markdown(
                        f"{text}\n\n**Source:** {source}  \n**Score:** {score:.3f}"
                    )

with tab_catalog:
    connection = library_rag.get_connection()
    rows = connection.execute(
        """
        SELECT title, author, genre, isbn, available_copies, total_copies, description
        FROM books
        ORDER BY title
        """
    ).fetchall()
    connection.close()

    st.subheader("Book Catalog")
    for row in rows:
        with st.expander(f"{row['title']} — {row['author']}"):
            st.write(row["description"])
            st.write(f"**Genre:** {row['genre']}")
            st.write(f"**ISBN:** {row['isbn']}")
            st.write(
                f"**Available:** {row['available_copies']} of {row['total_copies']}"
            )

with tab_issue:
    connection = library_rag.get_connection()
    members = connection.execute(
        "SELECT id, name FROM members ORDER BY name"
    ).fetchall()
    books = connection.execute(
        """
        SELECT id, title, available_copies
        FROM books
        ORDER BY title
        """
    ).fetchall()
    connection.close()

    member_labels = {row["name"]: row["id"] for row in members}
    book_labels = {
        f"{row['title']} ({row['available_copies']} available)": row["id"]
        for row in books
    }

    selected_member = st.selectbox("Member", list(member_labels))
    selected_book = st.selectbox("Book", list(book_labels))
    if st.button("Issue Book"):
        connection = library_rag.get_connection()
        success, message = library_rag.issue_book_for(
            connection,
            member_labels[selected_member],
            book_labels[selected_book],
        )
        connection.close()
        if success:
            st.success(message)
        else:
            st.error(message)

with tab_return:
    connection = library_rag.get_connection()
    loans = connection.execute(
        """
        SELECT loans.id, members.name, books.title, loans.due_at
        FROM loans
        JOIN members ON members.id = loans.member_id
        JOIN books ON books.id = loans.book_id
        WHERE loans.returned_at IS NULL
        ORDER BY loans.id
        """
    ).fetchall()
    connection.close()

    if not loans:
        st.info("No active loans.")
    else:
        loan_labels = {
            f"{row['id']} — {row['name']} — {row['title']} (due {row['due_at']}": row["id"]
            for row in loans
        }
        selected_loan = st.selectbox("Active loan", list(loan_labels))
        if st.button("Return Book"):
            connection = library_rag.get_connection()
            success, message, fine = library_rag.return_loan(
                connection, loan_labels[selected_loan]
            )
            connection.close()
            if success:
                st.success(message)
                if fine:
                    st.warning(f"Late fine: {fine} rupees")
            else:
                st.error(message)
