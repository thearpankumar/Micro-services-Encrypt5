-- Create the `keys` table
CREATE TABLE `keys` (
    user_id CHAR(36) NOT NULL,   -- Use CHAR(36) for UUID
    encryption_key VARCHAR(256) NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the `users` table
CREATE TABLE `users` (
    user_id CHAR(36) DEFAULT (UUID()) NOT NULL,   -- Use UUID() for MySQL
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    middle_name VARCHAR(255),
    last_name VARCHAR(255),
    email VARCHAR(255) NOT NULL,
    country_code VARCHAR(10) NOT NULL,
    phone_number VARCHAR(15) NOT NULL,
    birth_date DATE NOT NULL,
    gender VARCHAR(10) NOT NULL,
    last_ip_address VARCHAR(45)
);

-- Primary key for the `keys` table
ALTER TABLE `keys`
    ADD CONSTRAINT keys_pkey PRIMARY KEY (user_id);

-- Primary key for the `users` table
ALTER TABLE `users`
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);

-- Unique constraint for the `users` table
ALTER TABLE `users`
    ADD CONSTRAINT users_email_key UNIQUE (email);

-- Foreign key constraint for the `keys` table
ALTER TABLE `keys`
    ADD CONSTRAINT keys_user_id_fkey FOREIGN KEY (user_id)
    REFERENCES `users`(user_id) ON DELETE CASCADE;

-- Optional: Insert initial data (uncomment and replace with your data)
-- LOAD DATA INFILE '/path/to/your_file.csv' INTO TABLE `keys` 
-- FIELDS TERMINATED BY ',' 
-- ENCLOSED BY '"' 
-- LINES TERMINATED BY '\n' 
-- (user_id, encryption_key, created);

-- LOAD DATA INFILE '/path/to/your_file.csv' INTO TABLE `users`
-- FIELDS TERMINATED BY ','
-- ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- (user_id, password_hash, first_name, middle_name, last_name, email, country_code, phone_number, birth_date, gender, last_ip_address);

-- Ensure indexes for faster queries (Optional)
CREATE INDEX idx_users_email ON `users`(email);
CREATE INDEX idx_keys_user_id ON `keys`(user_id);
