# 1-20 第②圈：請家教考你 key 每次收到的是什麼（自評，check 只看四個標籤都寫了）

在家教專案裡貼上 AI 寫的這兩行，打：
「這是 AI 寫的，依金額從大排到小。我想確認自己真的看懂了。請你出一題，考我 key 的部分，先不要解釋。」

```python
entries = [("11/03", 120), ("11/01", 450), ("11/02", 30)]
top = sorted(entries, key=lambda e: e[1], reverse=True)
```

先用自己的話回答。家教說不對的地方，自己跑一次確定：把 lambda 改回 def，在函式裡加一行 print，看 key 每次收到的是什麼、一共收到幾次。

```python
def key_of(e):
    print("收到", e)
    return e[1]

top = sorted(entries, key=key_of, reverse=True)
```

在下面四個標籤後面寫字（寫了就算交了，內容不改對錯）：

家教問我的：
我一開始的回答：
家教怎麼說：
我加 print 跑出來的：

自評（打勾）：

- [ ] 我說得出 key 每次收到的是什麼（一筆，還是整個 list），一共收到幾次
- [ ] 我說得出 lambda 冒號前面、後面各是什麼
- [ ] 家教說的，我自己跑過一次，確定它說得對不對
