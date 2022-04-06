-- $ sqlite3 answers.db < answers.sql

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS Answers;
CREATE TABLE Answers (
    id INT PRIMARY KEY,
    word CHAR(5) UNIQUE 
);
COMMIT;
