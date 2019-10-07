import pandas as pd
import re

from zhon.hanzi import punctuation as ch_punctuation

from string import punctuation as en_punctuation


comments_path = "/Users/llwu/E盘/KKB/KKB_NLP_LESSON_TEACHER/datasource/datasource.git/trunk/movie_comments.csv"
pure_text = open("pure_text.txt","w",encoding='utf-8')
data = pd.read_csv(comments_path)
for i in range(len(data['comment'])):
    if not type(data['comment'][i])==type(0.0):
        try:
            comments = data['comment'][i]
            comments = "".join(comments.replace(" ", ""))
            comments = "".join(comments.split("\n"))

            comments = re.sub("[{}]+".format(ch_punctuation), "", comments)#去除中文标点
            comments = re.sub("[{}]+".format(en_punctuation), "", comments)#去除英文标点
            pure_text.write(comments)
        except:
            print("error")
pure_text.close()