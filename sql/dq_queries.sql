-- Example DQ queries
-- Completeness
SELECT
  SUM(CASE WHEN income IS NULL THEN 1 ELSE 0 END) AS missing_income,
  SUM(CASE WHEN ltv IS NULL THEN 1 ELSE 0 END) AS missing_ltv
FROM loans_raw;

-- Uniqueness
SELECT loan_id, COUNT(*) c
FROM loans_raw
GROUP BY loan_id
HAVING COUNT(*) > 1;

-- Domain validity
SELECT product_type, COUNT(*) c
FROM loans_raw
GROUP BY product_type;

-- Outliers (simple)
SELECT
  MIN(balance) AS min_balance,
  MAX(balance) AS max_balance,
  AVG(balance) AS avg_balance
FROM loans_raw;
