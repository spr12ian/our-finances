I have two tables that both represent the same undelying data

SELECT sql FROM sqlite_master WHERE type='table' AND name='bmonzo';
SELECT sql FROM sqlite_master WHERE type='table' AND name='_bmonzo';

CREATE TABLE "bmonzo" (
"id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "transaction_id" TEXT,
  "date" TEXT,
  "time" TEXT,
  "type" TEXT,
  "name" TEXT,
  "emoji" TEXT,
  "category" TEXT,
  "amount" TEXT,
  "currency" TEXT,
  "local_amount" TEXT,
  "local_currency" TEXT,
  "notes_and__tags" TEXT,
  "address" TEXT,
  "receipt" TEXT,
  "description" TEXT,
  "category_split" TEXT,
  "money_out" TEXT,
  "money_in" TEXT
);

CREATE TABLE "_bmonzo" (
"id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "date" TEXT,
  "description__39488204__bmonzo" TEXT,
  "credit" TEXT,
  "debit" TEXT,
  "note" TEXT,
  "cpty" TEXT,
  "date_cpty" TEXT,
  "balance" TEXT
);


SELECT o.id, o.date, o.description, o.name, b.id, b.date, b.description__39488204__bmonzo, b.cpty, b.note
FROM bmonzo as o join _bmonzo as b
WHERE o.id = b.id
and o.date <> b.date;

SELECT b.id, b.date, description__39488204__bmonzo, credit, debit, note, cpty, o.name, o.money_in
FROM bmonzo as o join _bmonzo as b
WHERE b.date = o.date
AND b.id=1319
;

UPDATE bmonzo
SET money_in = money_in || '.00'
WHERE money_in NOT LIKE '%.%';
UPDATE bmonzo
SET money_out = money_out || '.00'
WHERE money_out NOT LIKE '%.%';


-- first create a backup
create table bmonzo_backup as
select *
from bmonzo
;

-- restore from backup
BEGIN TRANSACTION;
DELETE FROM bmonzo;
INSERT INTO bmonzo SELECT * FROM bmonzo_backup;
COMMIT;

