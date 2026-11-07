# 0-C 壞版本 1（就是 start/make_v0.sh 那一版）
mkdir -p v0/data
mkdir -p v0/notes
touch v0/notes/budget.txt
rm -rf ../0-C-保險箱
cp ../../main.py v0/main_backup.py
echo "帳本 v0 的資料夾建好了"
