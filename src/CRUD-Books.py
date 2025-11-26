def create_book(title, author, isbn=None, cost=None):
    """
    Insert a new book into `books`.

    Steps (implement):
    1. Validate required fields (title).
    2. Build parameterized INSERT using `text()`.
    3. Open connection and `with conn.begin():` to execute transaction.
    4. Return the new record id or inserted row metadata.
    """
    # TODO: implement using SQLAlchemy text and transactions
    query = text("""
    INSERT INTO books (title, author, ISBN, cost_book, book_status)
    VALUES (:title, :author, :isbn, :cost, :status)
""")
    with get_engine().connect() as conn:
        transaction = conn.begin()
        try:
            conn.execute(query,
            {
                "title": title,
                "author": author,
                "isbn": isbn,
                "cost": cost,
                "status": "AVAILABLE"
            })
            transaction.commit()
            return f"Added book '{title}' by {author}."
        except Exception as e:  
            transaction.rollback()
            raise e
    pass

def get_books(title=None, author=None, genre=None, status=None, limit=100):
    """
    Retrieve books with optional filters.
    Implement:
    - Build base SQL: SELECT * FROM books WHERE 1=1
    - Append filters only if provided, using parameterized values (LIKE for title/author).
    - Return list of dicts or pandas.DataFrame.
    """
    # TODO: implement dynamic SQL building safely with text()
    query = "SELECT * FROM books WHERE 1=1"
    params = {}
    if title:
        query += " AND title LIKE :title"
        params["title"] = f"%{title}%"
    if author:
        query += " AND author LIKE :author"
        params["author"] = f"%{author}%"
    if genre:
        query += " AND genre = :genre"
        params["genre"] = genre
    if status:
        query += " AND status = :status"
        params["status"] = status
    query += " LIMIT :limit"
    params["limit"] = limit
    query = text(query)
    with get_engine().connect() as conn:
        result = conn.execute(query, params)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df

    pass
def get_book_by_id(book_id):
    """
    Get a single book by `book_id`.
    Return None if not found.
    """
    # TODO: SELECT * FROM books WHERE book_id = :book_id
    query = text("SELECT * FROM books WHERE book_id = :book_id")
    with get_engine().connect() as conn:
        result = conn.execute(query, {"book_id": book_id})
        row = result.fetchone()
        if row:
            return dict(row._mapping)
        else:
            return None
    pass
def update_book_details(book_id, title=None, author=None, isbn=None, genre=None, cost=None):
    """
    Update book metadata. Only update fields that are not None.
    Use a transaction and dynamic SET building.
    """
    # TODO: build SET dynamically and execute inside a transaction
    set_clauses = []
    params = {"book_id": book_id}
    if title is not None:
        set_clauses.append("title = :title")
        params[ "title"] = title
    if author is not None:
        set_clauses.append("author = :author")
        params["author"] = author
    if isbn is not None:
        set_clauses.append("isbn = :isbn")
        params["isbn"] = isbn
    if genre is not None:
        set_clauses.append("genre = :genre")
        params["genre"] = genre
    if cost is not None:
        set_clauses.append("cost_book = :cost")
        params["cost"] = cost
    if not set_clauses:
        raise ValueError("No fields to update.")
    set_clause = ", ".join(set_clauses)
    query = text(f"UPDATE books SET {set_clause} WHERE book_id = :book_id")
    with get_engine().connect() as conn:
        transaction = conn.begin()
        try:
            conn.execute(query, params)
            transaction.commit()
            return f"Updated book id {book_id}."
        except Exception as e:
            transaction.rollback()
            raise e
        
    pass
def update_book_status(book_id, new_status):
    """
    Update `book_status` — validate allowed values.
    Allowed: 'AVAILABLE','BORROWED','LOST','DAMAGED'
    for now only implement 'AVAILABLE' and 'BORROWED'.
    when needed, extend to other statuses.
    """
    # TODO: validate new_status and perform UPDATE in a transaction
    allowed_statuses = {'AVAILABLE', 'BORROWED'}
    if new_status not in allowed_statuses:
        raise ValueError(f"Invalid status '{new_status}'. Allowed statuses: {allowed_statuses}")
    query = text("UPDATE books SET book_status = :new_status WHERE book_id = :book_id")
    with get_engine().connect() as conn:
        transaction = conn.begin()
        try:
            conn.execute(query, {"new_status": new_status, "book_id": book_id})
            transaction.commit()
            return f"Updated status of book id {book_id} to '{new_status}'."
        except Exception as e:  
            transaction.rollback()
            raise e
        
def delete_book(book_id):
    """
    Delete or logically remove a book.
    Rule: do NOT delete if book is currently BORROWED.
    Consider setting status = 'REMOVED' instead of hard delete.
    """
    # TODO: SELECT status, then conditional DELETE or UPDATE
    query_status = text("SELECT book_status FROM books WHERE book_id = :book_id")
    query_delete = text("DELETE FROM books WHERE book_id = :book_id")
    query_update = text("UPDATE books SET book_status = 'REMOVED' WHERE book_id = :book_id")
    with get_engine().connect() as conn:
        transaction = conn.begin()
        try:
            result = conn.execute(query_status, {"book_id": book_id})
            row = result.fetchone()
            if row is None:
                raise ValueError(f"Book id {book_id} not found.")
            current_status = row._mapping["book_status"]
            if current_status == "BORROWED":
                raise ValueError(f"Cannot delete book id {book_id} as it is currently BORROWED.")
            else:
                # Perform logical delete by updating status to 'REMOVED'
                conn.execute(query_update, {"book_id": book_id})
            transaction.commit()
            return f"Book id {book_id} marked as REMOVED."
        except Exception as e:  
            transaction.rollback()
            raise e