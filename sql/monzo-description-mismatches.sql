-- I have two tables (bmonzo and _bmonzo) in an sqlite databas
-- bmonzo is true data
-- _bmonzo has fewer columns than bmonzo

-- first create a backup after every download
DROP TABLE IF EXISTS bmonzo_backup;

CREATE TABLE bmonzo_backup AS
SELECT *
FROM bmonzo;

-- SELECT sql FROM sqlite_master WHERE type='table' AND name='bmonzo';

SELECT
  id,
  transaction_id,
  date,
  time,
  type,
  name,
  emoji,
  category,
  amount,
  currency,
  local_amount,
  local_currency,
  notes_and__tags,
  address,
  receipt,
  description,
  category_split,
  money_out,
  money_in
FROM bmonzo
WHERE id = 1;

-- SELECT sql FROM sqlite_master WHERE type='table' AND name='_bmonzo';

SELECT
  id,
  date,
  description__39488204__bmonzo,
  credit,
  debit,
  note,
  cpty,
  date_cpty,
  balance
FROM _bmonzo
WHERE id = 1;

SELECT 
  o.id, 
  o.date, 
  UPPER(o.description), 
  UPPER(o.name),
  amount,
  b.id, 
  b.date, 
  description__39488204__bmonzo, 
  cpty, 
  note
FROM bmonzo as o join _bmonzo as b
WHERE o.id = b.id
AND UPPER(o.description) <> description__39488204__bmonzo
AND o.date <> b.date;

SELECT 
  o.id, 
  o.date, 
  UPPER(o.description), 
  UPPER(o.name),
  money_in,
  b.id, 
  b.date, 
  description__39488204__bmonzo, 
  cpty, 
  note,
  credit
FROM bmonzo as o join _bmonzo as b
WHERE o.id = b.id
AND UPPER(o.description) <> description__39488204__bmonzo
AND money_in <> credit;

SELECT b.id, b.date, description__39488204__bmonzo, credit, debit, note, cpty, o.name, o.money_in
FROM bmonzo as o join _bmonzo as b
WHERE b.date = o.date
AND b.id=1319
;

-- UPDATE bmonzo
-- SET money_in = money_in || '.00'
-- WHERE money_in NOT LIKE '%.%';
-- UPDATE bmonzo
-- SET money_out = money_out || '.00'
-- WHERE money_out NOT LIKE '%.%';


-- restore from backup
-- BEGIN TRANSACTION;
-- DELETE FROM bmonzo;
-- INSERT INTO bmonzo SELECT * FROM bmonzo_backup;
-- COMMIT;

