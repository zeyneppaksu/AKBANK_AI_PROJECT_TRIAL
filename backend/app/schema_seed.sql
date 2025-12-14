CREATE TABLE customers (
  customer_id SERIAL PRIMARY KEY,
  full_name TEXT NOT NULL,
  city TEXT NOT NULL
);

CREATE TABLE accounts (
  account_id SERIAL PRIMARY KEY,
  customer_id INT NOT NULL REFERENCES customers(customer_id),
  account_type TEXT NOT NULL,
  balance NUMERIC(12,2) NOT NULL
);

CREATE TABLE transactions (
  tx_id SERIAL PRIMARY KEY,
  account_id INT NOT NULL REFERENCES accounts(account_id),
  tx_type TEXT NOT NULL,
  amount NUMERIC(12,2) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO customers(full_name, city) VALUES
('Ada Yılmaz', 'Istanbul'),
('Deniz Kaya', 'Ankara'),
('Ece Demir', 'Izmir');

INSERT INTO accounts(customer_id, account_type, balance) VALUES
(1, 'checking', 1200.50),
(1, 'savings', 35000.00),
(2, 'checking', 800.00),
(3, 'checking', 500.25);

INSERT INTO transactions(account_id, tx_type, amount, created_at) VALUES
(1, 'deposit', 500.00, NOW() - interval '10 days'),
(1, 'withdrawal', 120.00, NOW() - interval '5 days'),
(2, 'deposit', 10000.00, NOW() - interval '30 days'),
(3, 'withdrawal', 50.00, NOW() - interval '2 days'),
(4, 'deposit', 200.00, NOW() - interval '1 days');
