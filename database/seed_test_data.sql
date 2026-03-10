-- Optional: Seed test data for development
-- Run after schema.sql
USE resume_screening_db;

-- Create test recruiter user and profile
INSERT INTO users (email, role, is_verified) VALUES ('recruiter@test.com', 'recruiter', TRUE)
ON DUPLICATE KEY UPDATE id=id;
SET @recruiter_user_id = (SELECT id FROM users WHERE email = 'recruiter@test.com' LIMIT 1);
INSERT INTO recruiters (user_id, name, email, company_name, phone)
SELECT @recruiter_user_id, 'Test Recruiter', 'recruiter@test.com', 'TechCorp Inc', '+1234567890'
WHERE NOT EXISTS (SELECT 1 FROM recruiters WHERE email = 'recruiter@test.com');

-- Create test candidate user and profile
INSERT INTO users (email, role, is_verified) VALUES ('candidate@test.com', 'candidate', TRUE)
ON DUPLICATE KEY UPDATE id=id;
SET @candidate_user_id = (SELECT id FROM users WHERE email = 'candidate@test.com' LIMIT 1);
INSERT INTO candidates (user_id, name, email, phone, skills, education, experience)
SELECT @candidate_user_id, 'Jane Doe', 'candidate@test.com', '+9876543210',
  'Python, React, SQL, AWS', 'B.Tech Computer Science, 2020', '2+ years Software Engineer'
WHERE NOT EXISTS (SELECT 1 FROM candidates WHERE email = 'candidate@test.com');

-- Create sample job (if recruiter exists)
INSERT INTO jobs (recruiter_id, job_title, company_name, required_skills, experience_required, job_description, number_of_openings)
SELECT r.id, 'Senior Software Engineer', 'TechCorp Inc', 'Python, React, SQL, AWS', '3+ years',
  'We are looking for a Senior Software Engineer to join our team. You will work on building scalable web applications using Python and React. Experience with AWS and SQL is required.',
  2
FROM recruiters r WHERE r.email = 'recruiter@test.com'
LIMIT 1;
