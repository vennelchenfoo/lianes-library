import os
import sys
import streamlit as st
import pandas as pd

# Ensure project root is on sys.path so `from src import ...` works
# This helps when running the script directly or via Streamlit which
# may not include the repo root on sys.path.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# ==== IMPORTS from back  ====
from src.CRUD_Blueprint import (
    get_engine,
    # BOOKS
    create_book,
    get_books,
    get_book_by_id,
    update_book_details,
    update_book_status,
    # BORROWERS
    create_borrower,
    get_borrower_by_id,
    get_borrowers,
    update_borrower_contact,
    set_borrower_status,
    delete_borrower,
    # LOANS / TRANSACTIONS
    create_loan,
    process_return,
    process_return_by_book,
    get_active_loans,
    get_overdue_loans,
    get_loan_history_by_book,
    get_loan_history_by_borrower,
    # DASHBOARD / REPORTS
    get_dashboard_stats,
    get_most_borrowed_books,
    get_most_active_borrowers,
)

# =========================================
# CONFIG STREAMLIT
# =========================================
st.set_page_config(
    page_title="Liane's Library",
    page_icon="📚",
    layout="wide",
)

# -----------------------------------------
# SESSION STATE
# -----------------------------------------
if "active_section" not in st.session_state:
    st.session_state.active_section = "dashboard"  # 'books', 'borrowers', 'transactions'

if "books_filter_df" not in st.session_state:
    st.session_state.books_filter_df = None  # DataFrame com resultado de busca de livros


# =========================================
# FUNÇÕES DE ESTATÍSTICA
# =========================================

def compute_stats_from_df(df_books: pd.DataFrame) -> dict:
    """
    Computa estatísticas a partir de um DataFrame de livros (resultado filtrado).
    Supõe que existe coluna `book_status` com valores como 'available','borrowed','overdue','removed'.
    """
    if df_books is None or df_books.empty:
        return {
            "total_books": 0,
            "available_books": 0,
            "borrowed_books": 0,
            "active_loans": 0,
            "overdue_loans": 0,
            "total_borrowers": None,  # vamos deixar None, dashboard oficial cuida disso
        }

    total_books = len(df_books)
    available_books = (df_books["book_status"] == "available").sum()
    borrowed_books = (df_books["book_status"] == "borrowed").sum()
    overdue_loans = (df_books["book_status"] == "overdue").sum()

    # Active loans ~ livros emprestados
    active_loans = borrowed_books

    return {
        "total_books": total_books,
        "available_books": available_books,
        "borrowed_books": borrowed_books,
        "active_loans": active_loans,
        "overdue_loans": overdue_loans,
        "total_borrowers": None,
    }


def get_stats_for_dashboard():
    """
    Decide se mostra estatísticas globais (DB) ou filtradas (resultado de busca).
    """
    # Se houver filtro de livros, usar stats desse resultado
    if st.session_state.books_filter_df is not None:
        df = st.session_state.books_filter_df
        stats = compute_stats_from_df(df)

        # Para total_borrowers, usamos o dashboard oficial para não perder info
        try:
            db_stats = get_dashboard_stats()
            stats["total_borrowers"] = db_stats.get("total_borrowers", 0)
        except Exception:
            stats["total_borrowers"] = 0

        return stats

    # Caso contrário, usamos as stats oficiais do banco
    try:
        return get_dashboard_stats()
    except Exception as e:
        st.error(f"Erro ao carregar estatísticas do dashboard: {e}")
        return {
            "total_books": 0,
            "available_books": 0,
            "borrowed_books": 0,
            "active_loans": 0,
            "overdue_loans": 0,
            "total_borrowers": 0,
        }


# =========================================
# CSS (MESMO ESTILO DO LAYOUT ANTERIOR)
# =========================================
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
        max-width: 1100px;
    }
    body {
        background-color: #f5f7fb;
    }
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    .brand {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 600;
        font-size: 1.05rem;
    }
    .brand-icon {
        width: 28px;
        height: 28px;
        border-radius: 8px;
        background: linear-gradient(135deg, #4f46e5, #6366f1);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 18px;
    }
    .nav-menu {
        display: flex;
        gap: 1.5rem;
        font-size: 0.95rem;
    }
    .nav-item {
        color: #6b7280;
        text-decoration: none;
        font-weight: 500;
    }
    .nav-item.active {
        color: #4f46e5;
        border-bottom: 2px solid #4f46e5;
        padding-bottom: 2px;
    }
    .card {
        background-color: #ffffff;
        border-radius: 18px;
        padding: 1.3rem 1.4rem;
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
    }
    .card-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .card-small-header {
        font-size: 0.85rem;
        color: #6b7280;
        margin-bottom: 0.35rem;
    }
    .card-small-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #111827;
    }
    .card-icon-pill {
        width: 32px;
        height: 32px;
        border-radius: 999px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
    }
    .pill-books { background-color: #eef2ff; color: #4f46e5; }
    .pill-borrowers { background-color: #ecfdf5; color: #16a34a; }
    .pill-active { background-color: #fffbeb; color: #f59e0b; }
    .pill-overdue { background-color: #fef2f2; color: #ef4444; }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================
# TOP BAR
# =========================================
st.markdown(
    """
    <div class="top-bar">
        <div class="brand">
            <div class="brand-icon">📚</div>
            <span>Liane's Library</span>
        </div>
        <div class="nav-menu">
            <span class="nav-item active">Dashboard</span>
            <span class="nav-item">Books</span>
            <span class="nav-item">Borrowers</span>
            <span class="nav-item">Transactions</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("## Liane's Library")
st.markdown("Manage your collection, borrowers, and loans with ease.")

# =========================================
# CARDS DO TOPO (DASHBOARD)
# =========================================
stats = get_stats_for_dashboard()
total_books = stats.get("total_books", 0)
total_borrowers = stats.get("total_borrowers", 0)
active_loans = stats.get("active_loans", 0)
overdue_loans = stats.get("overdue_loans", 0)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="card">
          <div class="card-row">
            <div>
              <div class="card-small-header">Total Books</div>
              <div class="card-small-value">{total_books}</div>
            </div>
            <div class="card-icon-pill pill-books">📘</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="card">
          <div class="card-row">
            <div>
              <div class="card-small-header">Borrowers</div>
              <div class="card-small-value">{total_borrowers}</div>
            </div>
            <div class="card-icon-pill pill-borrowers">👤</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="card">
          <div class="card-row">
            <div>
              <div class="card-small-header">Active Loans</div>
              <div class="card-small-value">{active_loans}</div>
            </div>
            <div class="card-icon-pill pill-active">📊</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
        <div class="card">
          <div class="card-row">
            <div>
              <div class="card-small-header">Overdue</div>
              <div class="card-small-value">{overdue_loans}</div>
            </div>
            <div class="card-icon-pill pill-overdue">⚠️</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# =========================================
# "CARDS BOTÕES" PARA SEÇÕES
# =========================================
ca, cb, cc = st.columns(3)

with ca:
    if st.button("📘 Books", use_container_width=True):
        st.session_state.active_section = "books"

with cb:
    if st.button("👤 Borrowers", use_container_width=True):
        st.session_state.active_section = "borrowers"

with cc:
    if st.button("📊 Transactions", use_container_width=True):
        st.session_state.active_section = "transactions"

st.markdown("")  # espaço

# =========================================
# CONTAINER PRINCIPAL (ABAIXO DOS CARDS)
# =========================================
section = st.session_state.active_section

# -----------------------------
# SEÇÃO BOOKS
# -----------------------------
if section == "books":
    st.subheader("📘 Books – Actions")

    books_action = st.radio(
        "Choose an action:",
        ["Search books", "Create book", "Update book", "Change status", "View book by ID"],
        horizontal=True,
    )

    # --- Search books (atualiza cards com filtro) ---
    if books_action == "Search books":
        with st.form("search_books_form"):
            title = st.text_input("Title (partial match)", "")
            author = st.text_input("Author (partial match)", "")
            status = st.selectbox(
                "Status",
                ["(any)", "available", "borrowed", "overdue", "removed"],
                index=0,
            )
            limit = st.number_input("Limit", min_value=1, max_value=500, value=50)
            submitted = st.form_submit_button("Search")

        if submitted:
            status_param = None if status == "(any)" else status
            # Atenção: sua função get_books ainda usa 'genre' e 'status' antigos.
            # Use apenas title/author/limit por enquanto, ou ajuste a função.
            df = get_books(title=title or None, author=author or None, limit=int(limit))
            if df.empty:
                st.warning("No books found.")
                st.session_state.books_filter_df = None
            else:
                st.success(f"Found {len(df)} book(s).")
                st.dataframe(df)
                # salva para atualizar métricas do topo
                st.session_state.books_filter_df = df

    # --- Create book ---
    elif books_action == "Create book":
        with st.form("create_book_form"):
            title = st.text_input("Title *")
            author = st.text_input("Author *")
            isbn = st.text_input("ISBN")
            cost = st.number_input("Cost", min_value=0.0, step=0.01)
            submitted = st.form_submit_button("Create book")

        if submitted:
            try:
                msg = create_book(title=title, author=author, isbn=isbn or None, cost=cost)
                st.success(msg)
            except Exception as e:
                st.error(f"Error creating book: {e}")

    # --- Update book details ---
    elif books_action == "Update book":
        with st.form("update_book_form"):
            book_id = st.number_input("Book ID", min_value=1, step=1)
            new_title = st.text_input("New title (optional)")
            new_author = st.text_input("New author (optional)")
            new_isbn = st.text_input("New ISBN (optional)")
            new_cost = st.text_input("New cost (optional, e.g. 9.99)")
            submitted = st.form_submit_button("Update book")

        if submitted:
            try:
                cost_val = float(new_cost) if new_cost.strip() else None
            except ValueError:
                st.error("Invalid cost value.")
                cost_val = None

            try:
                msg = update_book_details(
                    book_id=int(book_id),
                    title=new_title or None,
                    author=new_author or None,
                    isbn=new_isbn or None,
                    cost=cost_val,
                )
                st.success(msg)
            except Exception as e:
                st.error(f"Error updating book: {e}")

    # --- Change book status ---
    elif books_action == "Change status":
        with st.form("change_status_form"):
            book_id = st.number_input("Book ID", min_value=1, step=1)
            new_status = st.selectbox(
                "New status",
                ["available", "borrowed", "overdue", "removed"],
            )
            submitted = st.form_submit_button("Change status")

        if submitted:
            try:
                # ⚠️ sua função update_book_status ainda usa ENUM antigo (AVAILABLE/BORROWED/...)
                # Ajuste a função para aceitar lower-case e usar o ENUM certo no banco.
                msg = update_book_status(int(book_id), new_status)
                st.success(msg)
            except Exception as e:
                st.error(f"Error changing status: {e}")

    # --- View book by ID ---
    elif books_action == "View book by ID":
        book_id = st.number_input("Book ID", min_value=1, step=1)
        if st.button("Load book"):
            try:
                data = get_book_by_id(int(book_id))
                if data:
                    st.json(data)
                else:
                    st.warning(f"No book found with ID {book_id}.")
            except Exception as e:
                st.error(f"Error fetching book: {e}")


# -----------------------------
# SEÇÃO BORROWERS
# -----------------------------
elif section == "borrowers":
    st.subheader("👤 Borrowers – Actions")

    borrowers_action = st.radio(
        "Choose an action:",
        ["Search borrowers", "Create borrower", "Update contact", "Set status", "Delete borrower"],
        horizontal=True,
    )

    # Search borrowers
    if borrowers_action == "Search borrowers":
        with st.form("search_borrowers_form"):
            first_name = st.text_input("First name (partial)")
            last_name = st.text_input("Last name (exact)")
            limit = st.number_input("Limit", min_value=1, max_value=500, value=50)
            submitted = st.form_submit_button("Search")

        if submitted:
            try:
                rows = get_borrowers(
                    first_name=first_name or None,
                    last_name=last_name or None,
                    limit=int(limit),
                )
                if not rows:
                    st.warning("No borrowers found.")
                else:
                    st.success(f"Found {len(rows)} borrower(s).")
                    st.dataframe(pd.DataFrame(rows))
            except Exception as e:
                st.error(f"Error searching borrowers: {e}")

    # Create borrower
    elif borrowers_action == "Create borrower":
        with st.form("create_borrower_form"):
            first_name = st.text_input("First name *")
            last_name = st.text_input("Last name *")
            email = st.text_input("Email")
            phone = st.text_input("Phone number")
            relationship_type = st.text_input("Relationship type (e.g. friend, family, neighbour)")
            address = st.text_input("Address")
            submitted = st.form_submit_button("Create borrower")

        if submitted:
            try:
                borrower = create_borrower(
                    first_name=first_name,
                    last_name=last_name,
                    email=email or None,
                    phone_number=phone or None,
                    relationship_type=relationship_type or None,
                    address=address or None,
                )
                st.success("Borrower created successfully:")
                st.json(borrower)
            except Exception as e:
                st.error(f"Error creating borrower: {e}")

    # Update contact
    elif borrowers_action == "Update contact":
        with st.form("update_borrower_form"):
            person_id = st.number_input("person_id", min_value=1, step=1)
            first_name = st.text_input("New first name (optional)")
            last_name = st.text_input("New last name (optional)")
            email = st.text_input("New email (optional)")
            phone = st.text_input("New phone (optional)")
            address = st.text_input("New address (optional)")
            submitted = st.form_submit_button("Update borrower")

        if submitted:
            try:
                updated = update_borrower_contact(
                    person_id=int(person_id),
                    first_name=first_name or None,
                    last_name=last_name or None,
                    email=email or None,
                    phone=phone or None,
                    address=address or None,
                )
                st.success("Borrower updated:")
                st.json(updated)
            except Exception as e:
                st.error(f"Error updating borrower: {e}")

    # Set status
    elif borrowers_action == "Set status":
        with st.form("set_status_form"):
            person_id = st.number_input("person_id", min_value=1, step=1)
            new_status = st.selectbox("New status", ["ACTIVE", "INACTIVE"])
            submitted = st.form_submit_button("Update status")

        if submitted:
            try:
                updated = set_borrower_status(int(person_id), new_status)
                st.success("Borrower status updated:")
                st.json(updated)
            except Exception as e:
                st.error(f"Error updating status: {e}")

    # Delete borrower
    elif borrowers_action == "Delete borrower":
        st.info("Use filters carefully – this will delete matching borrowers.")
        with st.form("delete_borrower_form"):
            person_id = st.text_input("person_id (leave blank to ignore)")
            first_name = st.text_input("First name (LIKE, optional)")
            last_name = st.text_input("Last name (exact, optional)")
            submitted = st.form_submit_button("Delete borrower(s)")

        if submitted:
            try:
                count = delete_borrower(
                    person_id=person_id or None,
                    first_name=first_name or None,
                    last_name=last_name or None,
                )
                st.success(f"Deleted {count} borrower(s).")
            except Exception as e:
                st.error(f"Error deleting borrower(s): {e}")


# -----------------------------
# SEÇÃO TRANSACTIONS
# -----------------------------
elif section == "transactions":
    st.subheader("📊 Transactions – Actions")

    trans_action = st.radio(
        "Choose an action:",
        ["Create loan", "Process return", "Return by book", "Active loans", "Overdue loans", "Loan history by book", "Loan history by borrower"],
        horizontal=False,
    )

    # Create loan
    if trans_action == "Create loan":
        from datetime import date

        with st.form("create_loan_form"):
            book_id = st.number_input("Book ID", min_value=1, step=1)
            person_id = st.number_input("person_id (borrower)", min_value=1, step=1)
            loan_date = st.date_input("Loan date", value=date.today())
            due_date = st.date_input("Due date (optional – leave as is to auto-calc)", value=date.today())
            use_auto_due = st.checkbox("Calculate due date automatically (14 days from loan date)", value=True)
            submitted = st.form_submit_button("Create loan")

        if submitted:
            try:
                if use_auto_due:
                    result = create_loan(
                        book_id=int(book_id),
                        person_id=int(person_id),
                        loan_date=loan_date,
                        due_date=None,          # lascia None pra função calcular
                    )
                else:
                    result = create_loan(
                        book_id=int(book_id),
                        person_id=int(person_id),
                        loan_date=loan_date,
                        due_date=due_date,
                    )
                st.success("Loan created successfully:")
                st.json(result)
            except Exception as e:
                st.error(f"Error creating loan: {e}")

    # Process return
    elif trans_action == "Process return":
        from datetime import date

        with st.form("process_return_form"):
            transaction_id = st.number_input("Transaction ID", min_value=1, step=1)
            return_date = st.date_input("Return date", value=date.today())
            submitted = st.form_submit_button("Process return")

        if submitted:
            try:
                result = process_return(int(transaction_id), return_date=return_date)
                st.success("Return processed successfully:")
                st.json(result)
            except Exception as e:
                st.error(f"Error processing return: {e}")

    # Return by book (book_id or partial title)
    elif trans_action == "Return by book":
        from datetime import date

        with st.form("process_return_by_book_form"):
            book_id = st.text_input("Book ID (optional)")
            book_title = st.text_input("Book title (optional, partial match)")
            return_date = st.date_input("Return date", value=date.today())
            submitted = st.form_submit_button("Process return by book")

        if submitted:
            try:
                bid = None
                if book_id and book_id.strip():
                    try:
                        bid = int(book_id)
                    except Exception:
                        st.error("Invalid Book ID value. Use an integer or leave blank.")
                        bid = None

                result = process_return_by_book(
                    book_id=bid,
                    book_title=book_title or None,
                    return_date=return_date,
                )
                st.success("Return processed successfully:")
                st.json(result)
            except Exception as e:
                st.error(f"Error processing return by book: {e}")

    # Active loans
    elif trans_action == "Active loans":
        try:
            df = get_active_loans()
            if df.empty:
                st.info("No active loans.")
            else:
                st.dataframe(df)
        except Exception as e:
            st.error(f"Error fetching active loans: {e}")

    # Overdue loans
    elif trans_action == "Overdue loans":
        try:
            df = get_overdue_loans()
            if df.empty:
                st.info("No overdue loans.")
            else:
                st.dataframe(df)
        except Exception as e:
            st.error(f"Error fetching overdue loans: {e}")

    # Loan history by book
    elif trans_action == "Loan history by book":
        book_id = st.number_input("Book ID (history)", min_value=1, step=1)
        if st.button("Load history (book)"):
            try:
                df = get_loan_history_by_book(int(book_id))
                if df.empty:
                    st.info("No loan history for this book.")
                else:
                    st.dataframe(df)
            except Exception as e:
                st.error(f"Error fetching loan history for book: {e}")

    # Loan history by borrower
    elif trans_action == "Loan history by borrower":
        person_id = st.number_input("person_id (history)", min_value=1, step=1)
        if st.button("Load history (borrower)"):
            try:
                df = get_loan_history_by_borrower(int(person_id))
                if df.empty:
                    st.info("No loan history for this borrower.")
                else:
                    st.dataframe(df)
            except Exception as e:
                st.error(f"Error fetching loan history for borrower: {e}")
