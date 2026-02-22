-- Basic transformations and feature engineering in SQL (optional)
-- Example: rating bands based on PD later; here we just create a cleaned view.
CREATE OR REPLACE VIEW loans_clean AS
SELECT
  loan_id,
  customer_id,
  country,
  product_type,
  secured,
  origination_date,
  maturity_date,
  balance,
  limit_amount,
  undrawn_limit,
  interest_rate,
  income,
  age,
  ltv,
  dti,
  delinq_12m,
  default_flag
FROM loans_raw
WHERE balance >= 0
  AND age BETWEEN 18 AND 90;
