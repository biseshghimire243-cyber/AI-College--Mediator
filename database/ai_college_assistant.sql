
CREATE DATABASE IF NOT EXISTS ai_college_assistant;

USE ai_college_assistant;

CREATE TABLE IF NOT EXISTS colleges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    address VARCHAR(255),
    phone VARCHAR(30),
    email VARCHAR(150),
    website VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    college_id INT,
    course_name VARCHAR(150) NOT NULL,
    degree_level VARCHAR(100),
    duration VARCHAR(100),
    description TEXT,
    FOREIGN KEY (college_id) REFERENCES colleges(id)
        ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS faqs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    college_id INT,
    category VARCHAR(100) NOT NULL,
    question VARCHAR(500) NOT NULL,
    answer TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (college_id) REFERENCES colleges(id)
        ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(190) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('student', 'admin') DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE SET NULL
);

-- Demo college: replace with your actual college details later.
INSERT INTO colleges (name, address, email)
SELECT
    'AI College Assistant Demo College',
    'Nepal',
    'info@example.com'
WHERE NOT EXISTS (
    SELECT 1 FROM colleges
    WHERE name = 'AI College Assistant Demo College'
);

INSERT INTO faqs (college_id, category, question, answer)
SELECT c.id, f.category, f.question, f.answer
FROM colleges c
CROSS JOIN (
    SELECT 'Admission' AS category,
           'How do I apply for admission?' AS question,
           'Contact the college administration for eligibility requirements, required documents, and application deadlines.' AS answer
    UNION ALL
    SELECT 'Fees',
           'Where can I find the fee structure?',
           'Contact the college administration for the latest tuition fees, payment deadlines, and applicable charges.'
    UNION ALL
    SELECT 'Examinations',
           'Where can I find the exam routine?',
           'Check the official college website or notice board for examination schedules and announcements.'
    UNION ALL
    SELECT 'Scholarships',
           'Are scholarships available?',
           'Contact the college administration to confirm scholarship eligibility, available programs, and application deadlines.'
) AS f
WHERE c.name = 'AI College Assistant Demo College'
AND NOT EXISTS (
    SELECT 1 FROM faqs existing
    WHERE existing.college_id = c.id
      AND existing.question = f.question
);
