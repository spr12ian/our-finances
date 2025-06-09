-- Summary (interest)
SELECT full_account_name, balance, interest_rate, annual_interest__aer_, date_fixed_until
FROM bank_accounts
WHERE annual_interest__aer_ > 1 
AND our_money = "TRUE"
ORDER BY interest_rate DESC, owner
;
