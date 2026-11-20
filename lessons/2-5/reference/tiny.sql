-- 2-5 第②圈：用 5 筆小資料，驗證 AI 對一條 SQL 的解釋（這個檔自己建一張小表，跑在用完就丟的空資料庫）
CREATE TABLE t (category TEXT, amount INTEGER);
-- 換你寫：放 5 筆，其中一筆的金額是空的（NULL），例如 ('交通', NULL)
INSERT INTO t VALUES ('餐飲', 100), ('餐飲', 200), ('交通', 50), ('交通', NULL), ('交通', 40);
SELECT category, COUNT(*), COUNT(amount), AVG(amount) FROM t GROUP BY category;
