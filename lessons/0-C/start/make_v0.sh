# 0-C 第三關：AI 給你的「建出帳本 v0 資料夾」腳本。
# 先讀，不要先跑！裡面有一行危險的指令：找到它、刪掉那一行、存檔，然後才跑：
#   cd ~/code/ledger/lessons/0-C
#   bash make_v0.sh
mkdir -p v0/data
mkdir -p v0/notes
touch v0/notes/budget.txt
rm -rf ../0-C-保險箱
cp ../../main.py v0/main_backup.py
echo "帳本 v0 的資料夾建好了"
