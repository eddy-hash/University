CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin','student') NOT NULL
);

CREATE TABLE courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) NOT NULL
);
CREATE TABLE results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    score DECIMAL(5,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
);
CREATE TABLE admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Admin
INSERT INTO admin (username, password) VALUES ('admin', 'Eddy@2023');

-- students
INSERT INTO students (student_code, first_name, last_name, email, password)
VALUES 
('STU001', 'John', 'Doe', 'john@example.com', 'pass123'),
('STU002', 'Jane', 'Smith', 'jane@example.com', 'pass123');

-- courses
INSERT INTO courses (course_code, course_name, credits)
VALUES 
('MATH101', 'Calculus', 3),
('PHY101', 'Physics', 3);

--results
INSERT INTO results (student_id, course_id, score)
VALUES 
(1, 1, 85.50),
(1, 2, 90.00),
(2, 1, 78.25),
(2, 2, 88.00);
