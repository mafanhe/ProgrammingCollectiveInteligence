# -*- coding:utf-8 -*-
import feedparser
import re

# 返回一个RSS订阅源的标题和包含单词的技术情况的字典
def getwordcounts(url):
    # 解析订阅源
    d=feedparser.parse(url)
    wc={}
    # 循环遍历所有的文章条目
    for e in d.entries:
        if 'summary' in e: summary=e.summary
        else: summary=e.description
        # 提取一个单词列表
        words=getwords(e.title+' '+summary)
        for word in words:
            wc.setdefault(word,0)
            wc[word]+=1
    return d.feed.title, wc

if __name__ == '__main__':
    # 将其中所有的HTML标记去掉，并以非字母字符作为分隔符拆分出单词，
    # 以列表形式返回
    def getwords(html):
        # 去除所有html标记
        txt=re.compile(r'<[^>]+>').sub('',html)
        #利用所有非字母字符拆分出单词
        words=re.compile(r'[A-Z^a-z]+').split(txt) 
        # 转化成小写形式
        return [word.lower() for word in words if word!='']

    # 出现这些单词的博客数目
    apcount={}
    wordcounts={}
    feedlist=[line for line in file('feedlist.txt')]
    for feedurl in feedlist:
        title,wc=getwordcounts(feedurl)
        wordcounts[title]=wc
        for word,count in wc.items():
            apcount.setdefault(word,0)
            if count>1:
                apcount[word]+=1

    #选定介于某个百分比范围内的单词
    wordlist=[]
    for w,bc in apcount.items():
        frac=float(bc)/len(feedlist)
        if frac>0.1 and frac<0.5: wordlist.append(w)

    # 写入文本文件
    out=file('blogdata.txt','w')
    out.write('Blog')
    for word in wordlist: out.write('\t%s' % word)
    out.write('\n')
    for blog,wc in wordcounts.items():
        out.write(blog)
        for word in wordlist:
            if word in wc: out.write('\t%d' % wc[word])
            else: out.write('\t0')
        out.write('\n')

