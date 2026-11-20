-- 2-5 第①圈：本月（2026 年 11 月）各分類的合計，金額空白的不算
-- 換你寫（寫在下面）：SELECT … FROM entries WHERE … GROUP BY …;
SELECT category, SUM(amount) FROM entries
WHERE date LIKE '2026-11%' AND amount IS NOT NULL
GROUP BY category;
