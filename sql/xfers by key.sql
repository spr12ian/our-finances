-- Query 3: xfers by key
SELECT key, category, COUNT(key) as how_many
FROM transactions
WHERE description = "XFER"
AND tax_year = "2024 to 2025"
GROUP BY key
ORDER BY how_many DESC
;
