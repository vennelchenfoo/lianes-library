
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

-- ============================
-- 3) CREATE borrowers_archive table
-- ============================

CREATE TABLE borrowers_archive (
    archive_id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT NOT NULL,
    first_name VARCHAR(255),
last_name VARCHAR(255),
    relationship_type VARCHAR(255) NOT NULL, 
    phone_number VARCHAR(20), 
    email VARCHAR(255), 
    address VARCHAR(255),
    deleted_at DATETIME NOT NULL
);

-- ============================
-- 4) CREATE TRIGGER to archive deleted borrowers
-- ============================

DELIMITER $$

CREATE TRIGGER trg_borrowers_before_delete
BEFORE DELETE ON borrowers
FOR EACH ROW
BEGIN
    INSERT INTO borrowers_archive (
        person_id,
        first_name,
        last_name,
        relationship_type,
        phone_number,
        email,
        address,
        deleted_at
    )
    VALUES (
        OLD.person_id,
        OLD.first_name,
        OLD.last_name,
        OLD.relationship_type,
        OLD.phone_number,
        OLD.email,
        OLD.address,
        NOW()
    );
END$$

DELIMITER ;