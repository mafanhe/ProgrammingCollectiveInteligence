import re
def separatewords(text):
    res={}
    AND=[]
    OR=[]
    s=text.split('AND')
    res[AND]=s
    
    return s