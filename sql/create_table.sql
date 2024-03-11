CREATE TABLE IF NOT EXISTS emails (
    id SERIAL PRIMARY KEY,
    message_id VARCHAR(50),
    subject TEXT,
    sender TEXT,
    message TEXT,
    received_at TIMESTAMP
);