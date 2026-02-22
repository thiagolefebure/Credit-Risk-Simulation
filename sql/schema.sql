-- DuckDB schema for synthetic credit portfolio
CREATE TABLE IF NOT EXISTS loans_raw (
  loan_id VARCHAR,
  customer_id VARCHAR,
  country VARCHAR,
  product_type VARCHAR,         -- TERM / REVOLVING
  secured INTEGER,              -- 1/0
  origination_date DATE,
  maturity_date DATE,
  balance DOUBLE,
  limit_amount DOUBLE,          -- for revolving
  undrawn_limit DOUBLE,
  interest_rate DOUBLE,
  income DOUBLE,
  age INTEGER,
  ltv DOUBLE,                   -- loan-to-value (0-1)
  dti DOUBLE,                   -- debt-to-income (0-1.5)
  delinq_12m INTEGER,           -- count
  default_flag INTEGER          -- 1 if default within horizon
);
