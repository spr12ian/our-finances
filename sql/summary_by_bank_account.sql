-- Summary by bank account
SELECT t.key, SUM(credit) as money_in, SUM(debit) as money_out, SUM(credit - debit)
FROM bank_accounts b JOIN transactions t
ON b.key = t.key
WHERE "our_money"="TRUE"
AND t.date BETWEEN "2025-01-01" AND "2025-01-31"
AND t.description NOT LIKE "X%"
GROUP BY t.key
;
