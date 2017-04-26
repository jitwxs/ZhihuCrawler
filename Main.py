#encoding:utf-8

from Login import *
from GetContent import *

  
if __name__ == '__main__':
    lg = Login()
    while(lg.isLogin() == False):
        lg.login()

    key_word = input('请输入你要爬取的关键词: ')
    ga = GetContent(key_word)
