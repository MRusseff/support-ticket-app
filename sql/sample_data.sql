-- Support Ticket App Sample Data
-- Inserts at least 3 tickets with 2 messages each

-- Insert sample tickets
INSERT INTO tickets (title, status, created_by) VALUES
    ('Login issues on mobile app', 'open', 'sarah.johnson@example.com'),
    ('Dashboard not loading data', 'in_progress', 'mike.chen@example.com'),
    ('Export feature throwing errors', 'resolved', 'emma.davis@example.com'),
    ('Slow query performance', 'open', 'alex.martinez@example.com');

-- Insert sample messages for ticket 1
INSERT INTO ticket_messages (ticket_id, message_text, author) VALUES
    (1, 'Users are reporting they cannot log in using the mobile app. The error message says "Invalid credentials" even with correct username/password.', 'sarah.johnson@example.com'),
    (1, 'I''ve checked the authentication service logs. It appears the mobile app is sending an outdated API version header. Working on a fix.', 'support.team@example.com');

-- Insert sample messages for ticket 2
INSERT INTO ticket_messages (ticket_id, message_text, author) VALUES
    (2, 'The main dashboard fails to load any data after the latest deployment. Console shows a 500 error from /api/dashboard endpoint.', 'mike.chen@example.com'),
    (2, 'Found the issue - a database migration didn''t complete properly. Running the missing migration now.', 'devops@example.com');

-- Insert sample messages for ticket 3
INSERT INTO ticket_messages (ticket_id, message_text, author) VALUES
    (3, 'When trying to export reports to CSV, the app throws a "Memory exceeded" error for large datasets.', 'emma.davis@example.com'),
    (3, 'Fixed! Implemented streaming export to handle large datasets. Deployed in v2.1.3.', 'engineering@example.com');

-- Insert sample messages for ticket 4
INSERT INTO ticket_messages (ticket_id, message_text, author) VALUES
    (4, 'The analytics query on the reports page is taking over 30 seconds to complete. This affects all users.', 'alex.martinez@example.com'),
    (4, 'Investigating. Looks like we''re missing an index on the events table. Will add it during the next maintenance window.', 'dba@example.com');
