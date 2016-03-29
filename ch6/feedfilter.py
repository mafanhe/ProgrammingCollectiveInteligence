# -*-coding:utf-8 -*-
import feedparser
import re


# 接受一个博客订阅源的url文件名并对内容项进行分类
def read(feed, classifier):
    # 得到订阅源的内容项并遍历循环
    f = feedparser.parse(feed)
    for entry in f['entries']:
        print
        print '-----'
        # 讲内容项打印输出
        print 'Title: '+entry['title'].encode('utf-8')
        print 'publisher: '+entry['publisher'].encode('utf-8')
        print
        print entry['summary'].encode('utf-8')

        # 江苏有文本组合在一起，为分类器构造见一个内容项
        fulltext = '%s\n%s\n%s' % (entry['title'], entry['publisher'], entry['summary'])

        # 将当前分类的最佳推测结果打印输出
        print 'Guess: '+str(classifier.classify(fulltext))

        # 请求用户给出正确分类，并以据此进行训练
        cl = raw_input('Enter category:')
        classifier.train(fulltext, cl)


def entryfeatures(entry):
    splitter = re.compile(('\\w*'))
    f = {}

    # 提取标题中的单词并进行标示
    titlewords=[s.lower() for s in splitter.split(entry['title']) if 2 < len(s) > 20]
