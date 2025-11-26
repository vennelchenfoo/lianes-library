
-- ============================
-- 1) MODIFY books to final format
-- ============================
ALTER TABLE books
    DROP COLUMN number_of_pages,
    DROP COLUMN publisher,
    DROP COLUMN publishing_date,
    DROP COLUMN acquisition_date,
    DROP COLUMN edition,
    DROP COLUMN reading_status,
    ADD COLUMN cost_book DECIMAL(10, 2),
    ADD COLUMN book_status ENUM('available', 'borrowed', 'overdue', 'removed') NOT NULL DEFAULT 'available';

-- ============================
-- 2) MODIFY books´author column to support longer names
-- ============================


ALTER TABLE books
MODIFY COLUMN author TEXT;
