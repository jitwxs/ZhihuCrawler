#encoding : utf-8

import requests,json,time,re,os
from bs4 import BeautifulSoup
from urllib import request

agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36'
headers = {'User-Agent':agent}

def getHTMLText(url):
    try:
        r = requests.get(url,headers=headers)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return None

def getSoupObj(url):
    try:
        html = getHTMLText(url)
        soup = BeautifulSoup(html,'html.parser')
        return soup
    except:
        return None

#爬取回答类
class GetContent:
    def __init__(self,key_word):
        self.url = 'https://www.zhihu.com/search?type=content&q={}&offset'.format(key_word)
        self.keywd_path = os.getcwd() + r'\{}'.format(key_word)
        try:
            os.mkdir(key_word)
            os.chdir(self.keywd_path)
        except:
            pass
        self.parserList()

    #处理该关键字下所有问题
    def parserList(self):
        try:
            k = 0
            while(True):
                soup = getSoupObj(self.url + str(k*10))
                que_hrefs = soup('a',{'target':'_blank','class':'js-title-link'})
                for i in que_hrefs:
                    self.parserQuestion(i['href'].split('/')[-1])
                k += 1
        except:
            pass

    #将回答中文字和H5分离，并下载图片，返回处理后的纯文本
    def parserText(self,temp,locate):
        text_re = re.compile(r'<[^>]+>',re.S)
        text = text_re.sub('',temp)
        reslists = re.findall('src="(.*?)"', temp, re.M)
        for x in reslists:
            try:
                print('开始下载图片 : ',x)
                request.urlretrieve(x,'{}/{}.jpg'.format(locate,x.split('/')[-1]))
            except:
                pass
        return text

    #处理问题下所有回答，参数为问题链接
    def parserQuestion(self,link):
        os.chdir(self.keywd_path)
        json_url = 'https://www.zhihu.com/api/v4/questions/{}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.author.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit=20&offset=0'.format(link)
        url = 'https://www.zhihu.com/question/{}'.format(link)

        soup = getSoupObj(url)
        que_title = soup('h1',class_='QuestionHeader-title')[0].text
        print('开始爬取问题:',que_title)
        que_path = ''
        try:
            os.mkdir(que_title)
            que_path = self.keywd_path + r'\{}'.format(que_title)
            os.chdir(que_path)
        except:
            pass
        
        try:
            headers['Referer'] = url
            headers['x-udid'] = 'ACCCpPoypQuPTrXK3GIdYKswXY6sYVAUQcY='
            headers['authorization'] = 'Bearer Mi4wQUFBQV9KdUJ0Z2tBSUlLay1qS2xDeGNBQUFCaEFsVk5Yd1FvV1FCdlVhZWxVMnpyTUgyU0Nmc005Q3VOVVRjMGpB|1493203806|7f0f19f6ef3886ff39aa0c17aff8a5324f31a2b6'

            k = 1
            while True:
                #更多JSON返回信息，见JSON.json文件
                text = getHTMLText(json_url)
                text = json.loads(text)

                #得到下次访问的回答连链接
                json_url = text["paging"]["next"]

                datas = text["data"]
                for i in datas:
                    author = i["author"]["name"]

                    #为匿名用户增加唯一标识
                    if author == '匿名用户':
                        author = '匿名用户' + str(k)
                        k += 1

                    print('开始爬取用户: {} 的回答'.format(author))
                    os.mkdir(author)

                    #保存格式为cvs格式
                    data_path = que_path+r'\{}'.format(author)+r'\data.cvs'
                    with open(data_path,'w') as f:
                        try:
                            f.write('用户名 : {},\n'.format(author))
                            f.write('性别 : {},\n'.format("女" if i["author"]["gender"] == '0' else "男"))
                            f.write('签名 : {},\n'.format(i["author"]["headline"]))
                            f.write('主页 : {},\n'.format('https://www.zhihu.com/people/'+i["author"]["url_token"]))
                            f.write('建立时间 : {},\n'.format(time.ctime(i["created_time"])))
                            f.write('更新时间 : {},\n'.format(time.ctime(i["updated_time"])))
                            f.write('字数统计 : {},\n'.format(i["voteup_count"]))
                            f.write('编辑次数 : {},\n'.format(i["comment_count"]))
                            content = self.parserText(i["content"],que_path+r'\{}'.format(author))
                            f.write('正文 : {},\n'.format(content))
                        except:
                            pass

                #当没有回答时，退出方法
                if json_url == '':
                    break;
        except:
            pass
