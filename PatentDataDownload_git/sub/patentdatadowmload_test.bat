cd /d %~dp0
echo PatentData DowmloadAndCopy Start
C:\anaconda30\python.exe C:\work\バッチ\PatentDataDownload\hello.py %* 2018009
rem .pyファイル中でsys.argv[1]で2018009（二つ目の引数）を取得
cd
pause