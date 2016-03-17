# -*-coding:utf-8 -*-
from BeautifulSoup import BeautifulSoup
import urllib2
import re

if __name__ == '__main__':
    chare=re.compile(r'[!-\.&]')
    itemowners=[]
    # 要去除的单词
    dropwords=['a','new','some','more','my','own','the','many','other','another']

    currentuser=0
    for i in range(1,51):
        # 搜索“用户希望拥有的物品”所对应的URL
        c=urllib2.urlopen(
        'http://member.zebo.com/Main?event_key=USERSEARCH&wiowiw=wiw&keyword=car&page=%d'
        % (i))
        soup=BeautifulSoup(c.read())
        for td in soup('td'):
            # 寻找带有bgverdanasmall类的表格单元格
            if ('class' in dict(td.attrs) and td['class']=='bgverdanasmall'):
                items=[re.sub(chare,'',a.contens[0].lower()).strip() for a in td('a')]
                for item in items:
                    # 去除多余的单词
                    txt=' '.join([t for t in item.split('') if t not in dropwords])
                    if lne(txt)<2: continue
                    itemowners[txt][currentuser]=1
                currentuser+=1
    out=file('zebo.txt','w')
    out.write('Item')
    for user in range(0,currentuser): out.write('\tU%d' % user)
    out.write('\n')
    for item,owners in itemowners.items():
        if len(owners)>10:
            out.write(item)
            for user in range(0,currentuser):
                if user in owners: out.write('\t1')
                else: out.write('\t0')
            out.write('\n')
