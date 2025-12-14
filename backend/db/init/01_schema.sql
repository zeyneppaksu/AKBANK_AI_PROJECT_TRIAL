-- 01_schema.sql
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS accounts CASCADE;
DROP TABLE IF EXISTS credit_applications CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS branches CASCADE;

CREATE TABLE branches (
  branch_code   INT PRIMARY KEY,
  branch_name   TEXT,
  city          TEXT,
  region        TEXT
);

CREATE TABLE customers (
  customer_no        INT PRIMARY KEY,
  first_name         TEXT,
  last_name          TEXT,
  gender             TEXT,
  birth_date         DATE,
  residence_city     TEXT,
  job                TEXT,
  segment            TEXT,
  first_register_date DATE,
  address            TEXT,
  phone              TEXT
);

CREATE TABLE accounts (
  account_no   INT PRIMARY KEY,
  customer_no  INT REFERENCES customers(customer_no),
  account_type TEXT,
  balance      NUMERIC,
  balance_try  NUMERIC,
  balance_usd  NUMERIC,
  balance_eur  NUMERIC,
  branch_code  INT REFERENCES branches(branch_code),
  opened_at    DATE,
  status       TEXT
);

CREATE TABLE transactions (
  transaction_no   INT PRIMARY KEY,
  account_no       INT REFERENCES accounts(account_no),
  transaction_type TEXT,
  amount           NUMERIC,
  currency         TEXT,
  transaction_time TIMESTAMP,
  channel          TEXT,
  category         TEXT,
  fraud_suspected  INT
);

CREATE TABLE credit_applications (
  application_no      INT PRIMARY KEY,
  customer_no         INT REFERENCES customers(customer_no),
  dependents          INT,
  education           TEXT,
  self_employed       TEXT,
  annual_income       NUMERIC,
  requested_amount    NUMERIC,
  term_months         INT,
  credit_score        INT,
  house_asset         NUMERIC,
  commercial_asset    NUMERIC,
  luxury_asset        NUMERIC,
  bank_asset          NUMERIC,
  decision            TEXT,
  application_date    DATE
);
