from selenium import webdriver # さっきpip install seleniumで入れたseleniumのwebdriverというやつを使う
import time
import lxml.html
import requests
import re
import os
from os import path
import glob
import shutil
import subprocess
#import shlex
#from ftplib import FTP
from logging import getLogger,StreamHandler,DEBUG
from datetime import datetime
import sys


#logファイル作成 https://qiita.com/amedama/items/b856b2f30c2f38665701
from logging import getLogger, StreamHandler, FileHandler, DEBUG, Formatter
logger = getLogger(__name__)
stream_handler = StreamHandler()
stream_handler.setLevel(DEBUG)
stream_handler.setFormatter(Formatter("%(asctime)s %(levelname)8s %(message)s)"))
file_handler = FileHandler(filename=os.path.dirname(__file__)+'\\log\\'+os.path.splitext(os.path.basename(__file__))[0]+datetime.strftime(datetime.today(),'%Y%m%d') +'_'+datetime.now().strftime('%H%M%S')+'.log') 
file_handler.setLevel(DEBUG)
file_handler.setFormatter(Formatter("%(asctime)s %(levelname)8s %(message)s)"))

logger.setLevel(DEBUG)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
logger.propagate = False

#variables
todayJPGFileName = ""

#methods
def get_today_JPGFile_name():

    print('JPGFileName is JPG_20180XX')
    i = input("Please input today's Number (20180XX)")
    return i


def confirm_file_name(arg_filename):
    print('Is it OK todayJPGFileName is ' + arg_filename + '?')
    input_confirm_todayJPGFileName = input('（y/n）>>')
    print(input_confirm_todayJPGFileName+'input(">>")')
    if(input_confirm_todayJPGFileName[0] == 'y'):
        return True
    else:
        return False

def main():
    try:
        #コンソール画面で対話
        baseJPGFileName = 'JPG_'
        todayJPGFileName = baseJPGFileName + get_today_JPGFile_name()
        
        confirm_file_name(todayJPGFileName)
        #input_confirm_todayJPGFileName = sys.stdin.readline()
        #print(input_confirm_todayJPGFileName+'sys.stdin.readline()')

        #input_confirm_todayJPGFileName = sys.stdin.read()
        #print(input_confirm_todayJPGFileName+'sys.stdin.read()')

        if(confirm_file_name()):
            pass
        else:
            logger.debug('y以外が入力されたので中止します')
            sys.exit()


        user_id = input('Please input user_id')
        pass_word = input('Please input password')

        #*********実行時に毎回変える*********

        #todayJPGFileName = 'JPG_2018029'
        #todayJPGFileName = sys.argv[1]
        #*********変数*********
        # filenum = 5
        # filenum_padded = '{0:03d}'.format(filenum)
        # todayJPGFileName = 'JPG_'+ datetime.now().strftime('%Y')+str(filenum_padded)

        todayJPHFileName = todayJPGFileName.replace("JPG","JPH")#JPH_
        isDownloadJPG = True
        isDownloadJPH = True
        isDoCopy = True #コピーまでやるかどうか　True：やる
        myDowmloadDir = 'C:\\Users\\常重　友佑\\Downloads'
        dowmloadJpgFoldername = todayJPGFileName + "_downfiles"
        dowmloadJphFoldername = todayJPHFileName + "_downfiles"
        myJPGWorkDir = 'D:\\workDdrive\\作業系\\特許DBインポート\\1jpg'
        myJPHWorkDir = 'D:\\workDdrive\\作業系\\特許DBインポート\\2jph'
        thisFileDir = os.path.dirname(os.path.abspath(__file__))
        batJPGDecompressionDir = myJPGWorkDir + "\\" + dowmloadJpgFoldername
        batJPHDecompressionDir = myJPHWorkDir + "\\" + dowmloadJphFoldername
        #**********************

        driver = webdriver.Chrome("./chromedriver.exe")
        driver.get("https://bulkdl.j-platpat.inpit.go.jp/BD2Service/bd2/general/ListServlet")#特許データダウンロードサイト ログイン画面へ
        useridBox = driver.find_element_by_name("txtUserid")#User ID
        useridBox.send_keys(user_id)
        useridBox = driver.find_element_by_name("txtPassword")#Password
        useridBox.send_keys(pass_word)
        loginBotan = driver.find_element_by_name("btnLogin")#Loginボタン
        loginBotan.click()

        try:
            #time.sleep(5)
            driver.implicitly_wait(5)
            douiBotan = driver.find_element_by_name("btnAgree")
            logger.debug('[login成功]')
            douiBotan.click()

            driver.implicitly_wait(10)

            #Downloadボタンを押す処理
            targetDownloadBotans = []
            dowmloadBotans = driver.find_elements_by_css_selector('table.table-result > tbody > tr > td > a.btn')
            for i in dowmloadBotans:
                temptext1 = i.get_attribute("onclick")
                if(temptext1):
                    temptext2 = temptext1.replace('clearMessage()','').replace('fileDownload(','')
                    #temptext3 = re.match(r"'.+'",temptext2) #正規表現が’’内の文字列をうまく取得できない
                    if(isDownloadJPG):
                        if todayJPGFileName in temptext2:
                            targetDownloadBotans.append(i) #JPGのダウンロードボタンをtargetDownloadBotanリストに追加
                    if(isDownloadJPH):
                        if todayJPHFileName in temptext2:
                            targetDownloadBotans.append(i) #JHGのダウンロードボタンをtargetDownloadBotanリストに追加
        
            #logger.debug('[Download対象]'+','.join(str(targetDownloadBotans)))
            for i in targetDownloadBotans:
                i.click()
                logger.debug(str(i)+'clicked')
                time.sleep(100)
        finally:
            #ログアウト処理　ログアウトしないと他の端末でログインしている状態になってしまうので注意
            logoutBotan2 = driver.find_element_by_css_selector('ul.list-horizontal-right > li > a.btn')
            logoutBotan2.click()
            logger.debug('[logout完了]')
            time.sleep(3)
            driver.quit()

        #Downloadファルダでフォルダにまとめてworkフォルダへ移動させる
        isExistDownloadDir = os.path.exists(myDowmloadDir)
        if(isExistDownloadDir):
            # dowmloadDirList = os.listder(myDowmloadDir)
            # for i in dowmloadDirList:
            os.chdir(myDowmloadDir)
            jpgFiles = glob.glob(todayJPGFileName + "*.tar.gz") #DowmloadフォルダのJPGファイルをリストで取得
            logger.debug('[コピー対象（JPG）]'+ ','.join(jpgFiles))
            jphFiles = glob.glob(todayJPHFileName + "*.tar.gz") #DowmloadフォルダのJPHファイルをリストで取得
            logger.debug('[コピー対象（JPH）]'+ ','.join(jphFiles))
            os.mkdir(myDowmloadDir + "\\" + dowmloadJpgFoldername) #DowmloadフォルダにJPGフォルダを作成
            os.mkdir(myDowmloadDir + "\\" + dowmloadJphFoldername) #DowmloadフォルダにJPHフォルダを作成
            for i in jpgFiles:
                shutil.move(i,myDowmloadDir + "\\" + dowmloadJpgFoldername + "\\") #DownloadフォルダのJPGファイルを上で作ったフォルダに移動させる
            logger.debug('['+myDowmloadDir + "\\" + dowmloadJpgFoldername + "\\ へ移動完了"+']')
            for i in jphFiles:
                shutil.move(i,myDowmloadDir + "\\" + dowmloadJphFoldername + "\\") #DownloadフォルダのJPHファイルを上で作ったフォルダに移動させる
            logger.debug('['+myDowmloadDir + "\\" + dowmloadJphFoldername + "\\ へ移動完了"+']')

            # os.mkdir(myJPGWorkDir + "\\" + todayJPGFileName) #自分のworkフォルダに対象フォルダを作成
            # os.mkdir(myJPHWorkDir + "\\" + todayJPHFileName) #自分のworkフォルダに対象フォルダを作成
            shutil.move(myDowmloadDir + "\\" + dowmloadJpgFoldername,myJPGWorkDir + "\\")
            logger.debug('['+myDowmloadDir + "\\" + dowmloadJpgFoldername,myJPGWorkDir + "\\ を作成"+']')
            shutil.move(myDowmloadDir + "\\" + dowmloadJphFoldername,myJPHWorkDir + "\\")
            logger.debug('['+myDowmloadDir + "\\" + dowmloadJphFoldername,myJPHWorkDir + "\\ を作成"+']')

            #ファイル連結処理
            if(isDoCopy):
                cmdjpgcopy = "copy /b " + dowmloadJpgFoldername + "\\*.tar.gz " + todayJPGFileName + ".tar.gz"
                logger.debug(cmdjpgcopy+'コピー処理開始')
                process1 = subprocess.Popen(cmdjpgcopy,cwd=myJPGWorkDir,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

                cmdjphcopy = "copy /b " + dowmloadJphFoldername + "\\*.tar.gz " + todayJPHFileName + ".tar.gz"
                logger.debug(cmdjphcopy+'コピー処理開始')
                process2 = subprocess.Popen(cmdjphcopy,cwd=myJPHWorkDir,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

                process1.wait()
                process2.wait()

                # bash→回答コマンドをコマンドプロンプトで行う上で、以下のフォルダが存在しないとエラーが発生するためここで作っておく
                if(os.path.exists(myJPGWorkDir+"\\"+todayJPGFileName)): #JPG
                    os.rmdir(myJPGWorkDir+"\\"+todayJPGFileName)

                os.mkdir(myJPGWorkDir+"\\"+todayJPGFileName)
                logger.debug(myJPGWorkDir+"\\"+todayJPGFileName+'作成')

                if(os.path.exists(myJPHWorkDir+"\\"+todayJPHFileName)):  #JPH
                    os.rmdir(myJPHWorkDir+"\\"+todayJPHFileName)
    
                os.mkdir(myJPHWorkDir+"\\"+todayJPHFileName)
                logger.debug(myJPHWorkDir+"\\"+todayJPHFileName+'作成')
    except Exception as e:
        logger.error('Traceback',stack_info = True)
        logger.error(e)

if __name__ == '__main__':
    main()

        

'''
以下コメント
#コピー処理　別パターン

    #渡されたファイルリストの順序で１つのファイルに結合する
    def join_file(fileList, filePath):
        with open(filePath, 'wb') as saveFile:
            for f in fileList:
                data = open(f,'rb').read()
                saveFile.write(data)
                saveFile.flush()
    # os.chdir(myJPGWorkDir)
    # #↓テスト用files
    # jpgFiles = glob.glob("*.tar.gz") #WorkフォルダのJPGファイルをリストで取得
    # join_file(jpgFiles,todayJPGFileName+".tar.gz")

    # #↓テスト用files
    # os.chdir(myJPHWorkDir)
    # jphFiles = glob.glob("*.tar.gz") #DowmloadフォルダのJPHファイルをリストで取得
    # join_file(jphFiles,todayJPHFileName+".tar.gz")

#解凍処理
中途半端にしかできない　容量制限？
# cmdbash = "bash"
# subprocess.Popen(cmdbash,cwd=myJPGWorkDir,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
cmdjpgtar = "bash -c \'tar xvfz " + todayJPGFileName + ".tar.gz -C " + todayJPGFileName +"\';"
#cmdjpgtarbash = ''+cmdjpgtar+''
process3 = subprocess.Popen(cmdjpgtar,cwd=myJPGWorkDir,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

#subprocess.Popen(cmdbash,cwd=myJPHWorkDir,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
cmdjphtar = "bash -c \'tar xvfz " + todayJPHFileName + ".tar.gz -C " + todayJPHFileName +"\';"
#cmdjphtarbash = ''+cmdjpgtar+''
process4 = subprocess.Popen(cmdjphtar,cwd=myJPHWorkDir,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

process3.wait()
process4.wait()

#解凍処理（バッチファイルを作ってから実行するバージョン）
こっちもうまくいかず...
#JPGの解凍バッチ作成→実行
if(os.path.exists(myJPGWorkDir+"\\"+todayJPGFileName)):
    os.rmdir(myJPGWorkDir+"\\"+todayJPGFileName)

os.mkdir(myJPGWorkDir+"\\"+todayJPGFileName)

if(os.path.exists(batJPGDecompressionDir + "\\" + todayJPGFileName+"_decompression.bat")):
    os.remove(batJPGDecompressionDir + "\\" + todayJPGFileName+"_decompression.bat")
f = open(batJPGDecompressionDir + "\\" + todayJPGFileName+"_decompression.bat",'w',encoding='shift_jis')
f.write("cd "+myJPGWorkDir+"\n")
f.write("bash"+"\n")
f.write("sleep 10"+"\n")
cmdjpgDecomp = "tar xvfz " + todayJPGFileName + ".tar.gz -C " + todayJPGFileName
f.write(cmdjpgDecomp+"\n")
f.close()

cmdjpgBat = todayJPGFileName + "_decompression.bat"
process3 = subprocess.Popen(cmdjpgBat,cwd=batJPGDecompressionDir)

#JPHの解凍バッチ作成→実行
if(os.path.exists(myJPHWorkDir+"\\"+todayJPHFileName)):
    os.rmdir(myJPHWorkDir+"\\"+todayJPHFileName)
    
os.mkdir(myJPHWorkDir+"\\"+todayJPHFileName)

if(os.path.exists(batJPHDecompressionDir + "\\" + todayJPHFileName+"_decompression.bat")):
    os.remove(batJPHDecompressionDir + "\\" + todayJPHFileName+"_decompression.bat")
f = open(batJPHDecompressionDir + "\\" + todayJPHFileName+"_decompression.bat",'w',encoding='shift_jis')
f.write("cd "+myJPHWorkDir+"\n")
f.write("bash"+"\n")
f.write("sleep 10"+"\n")
cmdjphDecomp = "tar xvfz " + todayJPHFileName + ".tar.gz -C " + todayJPHFileName
f.write(cmdjphDecomp+"\n")
f.close()

cmdjphBat = todayJPHFileName + "_decompression.bat"
process4 = subprocess.Popen(cmdjphBat,cwd=batJPHDecompressionDir)

process3.wait()
process4.wait()
'''


#参考
''' driver = webdriver.Chrome("./chromedriver.exe") # さっきDLしたchromedriver.exeを使う
driver.get("http://www.yahoo.co.jp/") #chrome起動してyahooに移動
searchBox = driver.find_element_by_css_selector("#srchtxt") #検索入力ボックスのhtmlを探す
searchBox.send_keys("世の中 憎い") #その検索ボックスで　「世の中 憎い」と打つ
kensakuBotan = driver.find_element_by_css_selector("#srchbtn") #htmlから検索ボタンを探す
kensakuBotan.click() #検索ボタンをクリック

#actionChains = ActionChains(driver)

# target_url = driver.current_url
# target_html = requests.get(target_url).text
# root = lxml.html.fromstring(target_html)
# driver = webdriver.pha

#if(i.get_attribute("onclick"))

#logoutBotan = driver.find_element_by_css_selector('ul')
#logoutBotan3 = driver.find_element_by_css_selector('ul > li > a')
#logoutBotan4 = driver.find_element_by_css_selector('ul > li > a').get_attribute("onclick")
#logoutBotan5 = driver.find_element_by_css_selector('ul > li > a').text

yieldを使う
def res_cmd_lfeed(cmd): #戻り値はリストではなく各行
    for line in subprocess.Popen(cmd, stdout=subprocess.PIPE,shell=True).stdout:
        yield line

def res_cmd_no_lfeed(cmd):
    return [str(x).rstrip("\n") for x in res_cmd_lfeed(cmd)]

cmd = "dir"
print(res_cmd_no_lfeed(cmd))

cmd = "copy /b " + todayJPHFileName + "\\*.tar.gz " + todayJPHFileName + ".tar.gz"
subprocess.Popen(cmd, stdout=subprocess.PIPE,shell=True) 
subprocess.call(cmd, shell=True)

p = subprocess.Popen(cmd, stdout=subprocess.PIPE,shell=True).communicate()[0]
print(os.getcwd())
os.chdir(myJPGWorkDir)
print(os.getcwd())
#f = open()


command1 = 'ls /'
command2 = 'sed s/opt/aaa/g'
process1 = subprocess.Popen(shlex.split(command1),stdout=subprocess.PIPE)
process2 = subprocess.Popen(shlex.split(command2),stdin=process1.stdout)

 '''
