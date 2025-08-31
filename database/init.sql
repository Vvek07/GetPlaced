-- Create database schema and initial data

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes for better performance
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_jobs_title ON jobs(title);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_jobs_company ON jobs(company);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_jobs_active ON jobs(is_active);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_resumes_user ON resumes(user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_applications_job ON applications(job_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_applications_user ON applications(user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_job_matches_job ON job_matches(job_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_job_matches_user ON job_matches(user_id);

-- Insert sample data
INSERT INTO users (email, hashed_password, full_name, role, is_active, is_verified) VALUES
('admin@ats.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/z.M1jHQOm', 'Admin User', 'admin', true, true),
('student@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/z.M1jHQOm', 'John Student', 'student', true, true),
('recruiter@company.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/z.M1jHQOm', 'Jane Recruiter', 'recruiter', true, true),
('faculty@university.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/z.M1jHQOm', 'Dr. Faculty', 'faculty', true, true);

-- Insert sample jobs
INSERT INTO jobs (title, company, description, requirements, location, job_type, experience_level, posted_by_id, required_skills, preferred_skills, keywords) VALUES
(
    'Software Engineer Intern',
    'Tech Corp',
    'Join our dynamic team as a Software Engineer Intern. You will work on cutting-edge projects and gain hands-on experience in full-stack development.',
    'Currently pursuing a degree in Computer Science or related field. Knowledge of programming languages such as Python, Java, or JavaScript. Understanding of data structures and algorithms.',
    'San Francisco, CA',
    'internship',
    'entry',
    3,
    '["Python", "JavaScript", "SQL", "Git"]',
    '["React", "Node.js", "AWS", "Docker"]',
    '["software", "programming", "development", "intern", "coding"]'
),
(
    'Data Scientist',
    'AI Solutions Inc',
    'We are looking for a Data Scientist to analyze large amounts of raw information to find patterns that will help improve our company.',
    'Bachelor''s degree in Mathematics, Statistics, Computer Science, or related field. Experience with machine learning frameworks. Proficiency in Python and R.',
    'New York, NY',
    'full-time',
    'mid',
    3,
    '["Python", "R", "Machine Learning", "Statistics", "SQL"]',
    '["TensorFlow", "PyTorch", "Spark", "Tableau"]',
    '["data", "science", "machine learning", "analytics", "statistics"]'
);

-- Create full-text search indexes for better searching
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_jobs_search ON jobs USING gin(to_tsvector('english', title || ' ' || description || ' ' || requirements));
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_resumes_search ON resumes USING gin(to_tsvector('english', coalesce(raw_text, '')));