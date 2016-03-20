# -*-coding:utf-8 -*-
import re
import math
from pysqlite2 import  dbapi2 as sqlite

def sampletrain(cl):
    cl.train('Nobody owns the water.', 'good')
    cl.train('the quick rabbit jumps fences', 'good')
    cl.train('buy pharmaceuticals now', 'bad')
    cl.train('make quick money at the online casino', 'bad')
    cl.train('the quick brown fox jumps', 'good')


def getwords(doc):
    splitter = re.compile('\\W*')
    # 根据非字母字符进行单词拆分
    words = [s.lower() for s in splitter.split(doc) if 20 > len(s) > 2]

    # 只返回一组不重复的单词
    return dict([(w, 1) for w in words])


class Classifier:
    def __init__(self, getfeatures, filename=None):
        # 统计特征/分类组合的数量，记录各分类中不同特征的数量
        self.fc = {}
        # 统计每个分类中的文档数量,记录各分类被使用次数
        self.cc = {}
        self.getfeatures = getfeatures

    # 增加对特征/分类组合的计数值
    def incf(self, f, cat):
        self.fc.setdefault(f, {})
        self.fc[f].setdefault(cat, 0)
        self.fc[f][cat] += 1

    # 增加对某一分类的计数值
    def incc(self, cat):
        self.cc.setdefault(cat, 0)
        self.cc[cat] += 1

    # 某一特征出现于某一分类中的计数值
    def fcount(self, f, cat):
        if f in self.fc and cat in self.fc[f]:
            return float(self.fc[f][cat])
        return 0.0

    # 属于某一分类的内容项数量
    def catcount(self, cat):
        if cat in self.cc:
            return float(self.cc[cat])
        return 0

    # 所有内容项的数量
    def totalcount(self):
        return sum(self.cc.values())

    # 所有分类的列表
    def categories(self):
        return self.cc.keys()

    def train(self, item, cat):
        features = self.getfeatures(item)
        # 针对该分类为每个特征增加计数值
        for f in features:
            self.incf(f, cat)

        # 增加针对该分类的计数值
        self.incc(cat)

    # 计算概率
    def fprob(self, f, cat):
        if self.catcount(cat) == 0:
            return 0
        # 特征在分类中出现的总次数，除以分类中包含内容项的总数
        return self.fcount(f, cat)/self.catcount(cat)

    # 假设概率加权平均
    def weightedprob(self, f, cat, prf, weight=1.0, ap=0.5):
        # 计算当前的概率值,prf=fprob
        basicprob = prf(f, cat)

        # 统计特征在所有分类中出现的次数
        totals = sum(self.fcount(f, c) for c in self.categories())

        # 计算加权平均
        bp = ((weight*ap)+(totals*basicprob))/(weight+totals)
        return bp


class NaiveBayes(Classifier):
    # 定义阈值
    def __init__(self, getfeatures):
        Classifier.__init__(self, getfeatures)
        self.thresholds = {}

    def setthreshold(self, cat, t):
        self.thresholds[cat] = t

    def getthreshold(self, cat):
        if cat not in self.thresholds:
            return 1.0
        return self.thresholds[cat]

    # 提取特征（单词）并将所有单词的概率值相乘以求出整体概率
    def docprob(self, item, cat):
        features = self.getfeatures(item)

        # 将所有特征的概率相乘
        p = 1
        for f in features:
            p *= self.weightedprob(f, cat, self.fprob)
        return p

    # Pr(Category|Document)=Pr(Document|Category)*Pr(Category)/Pr(Document)
    # 计算分类的概率，返回Pr(Document|Category)与Pr(Category)的乘积
    def prob(self, item, cat):
        catprob = self.catcount(cat)/self.totalcount()
        docprob = self.docprob(item, cat)
        return docprob*catprob

    # 该方法将计算每个分类的概率，从中得出最大值，并将其与次大概率值进行对比
    # 确定是否超过了规定的阈值。如果没有任何一个分类满足上述条件，返回默认值
    def classify(self, item, default=None):
        probs = {}
        # 寻找概率最大的分类
        max = 0.0
        for cat in self.categories():
            probs[cat] = self.prob(item, cat)
            if probs[cat] > max:
                max = probs[cat]
                best = cat
        # 确保概率值超出阈值*次大概率值
        for cat in probs:
            if cat == best:
                continue
            if probs[cat]*self.getthreshold(best) > probs[best]:
                return default
        return best


class FisherClassifier(Classifier):
    def __init__(self, getfeatures):
        Classifier.__init__(self, getfeatures)
        # 临界值
        self.minimums = {}

    def setminimun(self, cat, min):
        self.minimums[cat] = min

    def getmininum(self, cat):
        if cat not in self.minimums:
            return 0
        return self.minimums[cat]

    # 计算每个分类的概率，并找到超过指定下限值的最佳结果
    def classify(self, item, default=None):
        # 循环遍历并寻找最佳结果
        best = default
        max = 0.0
        for c in self.categories():
            p = self.fisherprob(item, c)
            if p >self.getmininum(c) and p>max:
                best = c
                max = p
        return best

    def cprob(self, f, cat):
        clf = self.fprob(f, cat)
        if clf == 0:
            return 0
        # 特征在所有分类中出现的频率
        freqsum = sum([self.fprob(f, c) for c in self.categories()])

        # 概率等于特征在该分类中出现的频率除以总体频率
        p = clf/freqsum

        return p

    def fisherprob(self, item, cat):
        # 将所有概率值相乘
        p = 1
        features = self.getfeatures(item)
        for f in features:
            p *= (self.weightedprob(f, cat, self.cprob))

        # 取自然对数， 并乘以-2
        fscore = -2*math.log(p)

        # 利用倒置对数卡方函数求得概率
        return self.invchi2(fscore, len(features)*2)

    # 对数卡方分布
    def invchi2(self, chi, df):
        m = chi / 2.0
        sum = term = math.exp(-m)
        for i in range(1, df//2):
            term *= m/i
            sum += term
        return min(sum, 1.0)
