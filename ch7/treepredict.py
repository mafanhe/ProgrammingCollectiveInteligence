# -*-coding:utf-8 -*-


from PIL import Image, ImageDraw

my_data=[['slashdot','USA','yes',18,'None'],
        ['google','France','yes',23,'Premium'],
        ['digg','USA','yes',24,'Basic'],
        ['kiwitobes','France','yes',23,'Basic'],
        ['google','UK','no',21,'Premium'],
        ['(direct)','New Zealand','no',12,'None'],
        ['(direct)','UK','no',21,'Basic'],
        ['google','USA','no',24,'Premium'],
        ['slashdot','France','yes',19,'None'],
        ['digg','USA','no',18,'None'],
        ['google','UK','no',18,'None'],
        ['kiwitobes','UK','no',19,'None'],
        ['digg','New Zealand','yes',12,'Basic'],
        ['slashdot','UK','no',21,'None'],
        ['google','UK','yes',18,'Basic'],
        ['kiwitobes','France','yes',19,'Basic']]


class decisionnode:
    def __init__(self, col=-1, value=None, results=None, tb=None, fb=None):
        self.col = col
        self.value = value
        self.results = results
        self.tb = tb
        self.fb = fb


# 在某一列对数据集合进行拆分，能够处理数值型数据和名词性数据。
def divideset(rows,column,value):
    # 定义一个函数，令其告诉我们数据行属于第一组（返回值为true)还是第二组（返回值为false)
    split_function = None
    if isinstance(value, int) or isinstance(value, float):
        split_function = lambda row: row[column] >= value
    else:
        split_function = lambda row: row[column] == value

    # 将数据集拆分成两个集合，并返回
    set1 = [row for row in rows if split_function(row)]
    set2 = [row for row in rows if not split_function(row)]
    return set1, set2


# 对各种可能的结果进行计数（每一行数据的最后一列记录了这一计数结果）
def uniquecounts(rows):
    """
    对各种可能的结果进行计数（每一行数据的最后一列记录了这一计数结果）
    :param rows:
    :return:
    """
    results = {}
    for row in rows:
        # 计数结果在最后一列
        r = row[-1]
        if r not in results:
            results[r] = 0
        results[r] += 1
    return results


def giniimpurity(rows):
    """
    基尼不纯度，是指将来自集合中的某种结果随机应用于集合中某一数据项的预期误差率。
    :param rows: 列表
    :return: 不纯度
    """
    total = len(rows)
    counts = uniquecounts(rows)
    imp = 0
    for k1 in counts:
        p1 = float(counts[k1])/total
        for k2 in counts:
            if k1 == k2:
                continue
            p2 = float(counts[k2])/total
            imp += p1 * p2
    return imp


# 熵是便利所有可能的结果之后所得到的p(x)log(p(x))之和
def entropy(rows):
    """
    熵
    :param rows:
    :return:
    """
    from math import log
    log2 = lambda x: log(x)/log(2)
    results = uniquecounts(rows)
    # 此处开始计算熵的值
    ent = 0.0
    for r in results.keys():
        p = float(results[r])/len(rows)
        ent -= p * log2(p)
    return ent


def buildtree(rows, scoref=entropy):
    """
    建立决策树
    :param rows:
    :param scoref: 计算混乱度函数
    :return:
    """
    if len(rows) == 0:
        return decisionnode()
    current_score = scoref(rows)

    # 定义一些变量以记录最佳拆分条件
    best_gain = 0.0
    best_criteria = None
    best_sets = None

    column_count = len(rows[0]) - 1
    for col in range(column_count):
        # 在当前列中生成一个由不同值构成的序列
        column_values = {}
        for row in rows:
            column_values[row[col]] = 1
        # 接下来根据这一列中的每个值，尝试对数据集进行拆分
        for value in column_values.keys():
            (set1, set2) = divideset(rows, col, value)

            # 信息增益，加权平均熵
            p = float(len(set1))/len(rows)
            gain = current_score - p * scoref(set1) - (1-p) * scoref(set2)
            if gain > best_gain and len(set1) > 0 and len(set2) > 0:
                best_gain = gain
                best_criteria = (col, value)
                best_sets = (set1, set2)

    # 创建子分支
    if best_gain > 0:
        trueBranch = buildtree(best_sets[0])
        falseBranch = buildtree(best_sets[1])
        return decisionnode(col=best_criteria[0], value=best_criteria[1], tb=trueBranch, fb=falseBranch)
    else:
        return decisionnode(results=uniquecounts(rows))

def printtree(tree, indent=''):
    """
    打印树
    :param tree:
    :param indent:
    :return:
    """
    # 这是一个叶节点吗？
    if tree.results is not None:
        print str(tree.results)
    else:
        # 打印判断条件
        print str(tree.col)+":"+str(tree.value)+'?'

        # 打印分支
        print indent+'T->',
        printtree(tree.tb, indent+' ')
        print indent+'F->',
        printtree(tree.fb, indent+' ')


def getwidth(tree):
    """
    计算分支宽度
    :param tree:
    :return:
    """
    if tree.tb is None and tree.fb is None:
        return 1
    return getwidth(tree.tb)+getwidth(tree.fb)


def getdepth(tree):
    """
    计算分值高度
    :param tree:
    :return:
    """
    if tree.tb is None and tree.fb is None:
        return 0
    return max(getdepth(tree.tb), getdepth(tree.fb))+1


def drawtree(tree, jpeg='tree.jpg'):
    """
    把树画到图片上
    :param tree:
    :param jpeg: 图片名称
    :return:
    """
    w = getwidth(tree)*100
    h = getdepth(tree)*100+120

    img = Image.new('RGB', (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    drawnode(draw, tree, w/2, 20)
    img.save(jpeg, 'JPEG')

def drawnode(draw, tree, x, y):
    """
    绘制决策树的结点
    :param draw:
    :param tree:
    :param x:
    :param y:
    :return:
    """
    if tree.results is None:
        # 得到每个分支的宽度
        w1 = getwidth(tree.fb)*100
        w2 = getwidth(tree.tb)*100

        # 确定此节点所要占据的总空间
        left = x - (w1+w2)/2
        right = x + (w1+w2)/2

        # 绘制判断条件字符串
        draw.text((x-20, y-10), str(tree.col)+":"+str(tree.value), (0, 0, 0))

        # 绘制到分支的连线
        draw.line((x, y, left+w1/2, y+100), fill=(255, 0, 0))
        draw.line((x, y, right-w2/2, y+100), fill=(255, 0, 0))

        # 绘制分支的节点
        drawnode(draw, tree.fb, left+w1/2, y+100)
        drawnode(draw, tree.tb, right-w2/2, y+100)
    else:
        txt = '\n'.join(['%s:%d' % v for v in tree.results.items()])
        draw.text((x-20, y), txt, (0, 0, 0))
