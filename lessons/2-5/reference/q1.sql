-- 2-5 第①圈：列出「餐飲」這一類的每一筆（日期、項目、金額、備註四欄）
-- 換你寫（寫在下面）：SELECT 哪幾欄 FROM entries WHERE 哪幾筆;
SELECT date, item, amount, note FROM entries WHERE category = '餐飲';
