USE lianes_library;

-- ============================
-- 1) CREATE TABLE books (RAW)
-- ============================
CREATE TABLE books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    ISBN VARCHAR(20) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,            -- Will be migrated to authors table
    publisher VARCHAR(255),
    number_of_pages INT,
    publishing_date DATE,
    acquisition_date DATE,
    edition VARCHAR(50),
    reading_status ENUM('not started', 'in progress', 'finished')
);

-- ============================
-- 2) CREATE TABLE borrowers
-- ============================
CREATE TABLE borrowers (
    person_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255), 
    last_name VARCHAR(255), 
    relationship_type VARCHAR(255), 
    phone_number VARCHAR(20), 
    email VARCHAR(255), 
    address VARCHAR(255)
);

-- ============================
-- 3) CREATE TABLE transactions
-- ============================
CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    person_id INT NOT NULL,
    loan_date DATE NOT NULL, 
    expected_return_date DATE,
    actual_return_date DATE,
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (person_id) REFERENCES borrowers(person_id)
);

