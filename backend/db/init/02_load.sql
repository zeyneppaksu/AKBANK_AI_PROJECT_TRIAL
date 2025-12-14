-- 02_load.sql
-- Data files are mounted into the container at /data/

COPY branches(branch_code, branch_name, city, region)
FROM '/data/subeler.csv'
WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

COPY customers(customer_no, first_name, last_name, gender, birth_date, residence_city, job, segment, first_register_date, address, phone)
FROM '/data/musteri.csv'
WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

COPY accounts(account_no, customer_no, account_type, balance, balance_try, balance_usd, balance_eur, branch_code, opened_at, status)
FROM '/data/hesaplar.csv'
WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

COPY transactions(transaction_no, account_no, transaction_type, amount, currency, transaction_time, channel, category, fraud_suspected)
FROM '/data/islemler.csv'
WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

COPY credit_applications(application_no, customer_no, dependents, education, self_employed, annual_income, requested_amount, term_months, credit_score, house_asset, commercial_asset, luxury_asset, bank_asset, decision, application_date)
FROM '/data/kredi_basvurulari.csv'
WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
