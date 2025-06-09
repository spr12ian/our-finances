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
