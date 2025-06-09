-- Query 1: Monthly summary
SELECT strftime('%Y-%m', t.date) as month, 
SUM(credit) as money_in, 
SUM(debit) as money_out, 
SUM(credit - debit) as net_amount
FROM bank_accounts b 
JOIN transactions t ON b.key = t.key
WHERE b."our_money" = "TRUE"
AND t.description NOT LIKE "X%"
GROUP BY month
ORDER BY month
;
-- Query 2: 2025-01 by bank account
SELECT t.key, SUM(credit) as money_in, SUM(debit) as money_out, SUM(credit - debit)
FROM bank_accounts b JOIN transactions t
ON b.key = t.key
WHERE "our_money"="TRUE"
AND t.date BETWEEN "2025-01-01" AND "2025-01-31"
AND t.description NOT LIKE "X%"
GROUP BY t.key
;-- Query 3: xfers by key
SELECT key, category, COUNT(key) as how_many
FROM transactions
WHERE description = "XFER"
AND tax_year = "2024 to 2025"
GROUP BY key
ORDER BY how_many DESC
;-- Query 4: Summary (interest)
SELECT full_account_name, balance, interest_rate, annual_interest__aer_, date_fixed_until
FROM bank_accounts
WHERE annual_interest__aer_ > 1 
AND our_money = "TRUE"
ORDER BY interest_rate DESC, owner
;
