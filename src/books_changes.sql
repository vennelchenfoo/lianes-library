USE lianes_library;

ALTER TABLE books
    DROP COLUMN number_of_pages,
    DROP COLUMN publisher,
    DROP COLUMN publishing_date,
    DROP COLUMN acquisition_date,
    DROP COLUMN edition,
    DROP COLUMN reading_status,
    ADD COLUMN cost_book DECIMAL(10, 2),
    ADD COLUMN book_status ENUM('available', 'borrowed', 'overdue') NOT NULL DEFAULT 'available';
    
    SELECT *
    FROM books;