# 1-22 用到的概念

這課的示範、起點檔、正確版（`reference/`）和壞版本（`mutants/`），只能用到下面這些概念。
老師端的 `tools/validate_lesson.py` 會用 Python 的 ast 模組粗略檢查；比 1-22 晚才教的概念，一定要標成「例外」並寫理由，validate 會把例外列出來。

## 可以用的概念

- 註解
- print
- 變數
- 資料型別
- 數字運算
- 字串操作（1-5 教過：replace、f-string）
- input
- 函式呼叫（int、str）
- 比較與邏輯（含 assert、not、in）
- if
- while（1-10 教過：while True 加 break）
- for
- list
- 函式定義（1-18 教過：def、參數、return）
- 模組與 import（1-21 教過：from money import to_yuan、if __name__ == "__main__":）
- 例外處理（這課教：try、except ValueError、except ValueError as e、else、finally、raise ValueError(訊息)；光禿禿的 except: 只出現在壞版本 m1 和第②圈的範例）

`predict.txt`、`bare.txt`、`tutor.md` 是文字檔，不是程式，不在檢查範圍。
`ai_bare.py` 是第②圈 AI 的建議（範例示意，光禿禿的 except:），讓學員自己跑跑看按 Control C 會怎樣，check 不檢查。
