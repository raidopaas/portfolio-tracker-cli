CREATE DATABASE portfolio_tracker;

USE portfolio_tracker;

CREATE TABLE accounts (
	id INT AUTO_INCREMENT PRIMARY KEY,
    account_name VARCHAR(20),
    account_type ENUM("cash", "broker") NOT NULL,
    balance DECIMAL(10,2) DEFAULT 0.00,
    stock_value DECIMAL(10,2) DEFAULT 0.00,
    currency CHAR(3) DEFAULT 'EUR'
);

CREATE TABLE transactions (
	id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    txn_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    description VARCHAR(100),

    CONSTRAINT fk_transactions_account
    FOREIGN KEY (account_id) REFERENCES accounts(id)
    ON DELETE CASCADE
);

CREATE TABLE stocks (
	id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    stock_price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    total_value DECIMAL(10,2)
		GENERATED ALWAYS AS (quantity * stock_price) STORED,
	dividend DECIMAL(4,2) NOT NULL DEFAULT 0.00,
    dividend_date DATE,
    listed CHAR(3) NOT NULL DEFAULT 'US',
    
    UNIQUE KEY unique_stock(symbol, listed)
);

CREATE TABLE goals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(25),
    target_amount DECIMAL(10,2) NOT NULL,
    deadline DATE NOT NULL,
    scope ENUM("portfolio", "account") NOT NULL,
    period ENUM("total", "annual") NOT NULL,
    account_id INT NULL,

    CONSTRAINT fk_goals_account
    FOREIGN KEY (account_id) REFERENCES accounts(id)
    ON DELETE CASCADE
);