
import pandas as pd
import re
import jieba
from collections import Counter
from zhon.hanzi import punctuation as ch_punctuation
from string import punctuation as en_punctuation


# #begin:数据预处理
# comments_path = "/Users/llwu/E盘/KKB/KKB_NLP_LESSON_TEACHER/datasource/datasource.git/trunk/movie_comments.csv"
# pure_text_file = open("pure_text.txt","w",encoding='utf-8')
# data = pd.read_csv(comments_path)
# for i in range(len(data['comment'])):
#     if not type(data['comment'][i])==type(0.0):
#         try:
#             comments = data['comment'][i]
#             comments = "".join(comments.replace(" ", ""))
#             comments = "".join(comments.split("\n"))
#
#             comments = re.sub("[{}]+".format(ch_punctuation), "", comments)#去除中文标点
#             comments = re.sub("[{}]+".format(en_punctuation), "", comments)#去除英文标点
#             pure_text_file.write(comments)
#         except:
#             print("error")
#
# pure_text_file.close()
#end:数据预处理结束



pure_text_file = open("pure_text.txt","r")
pure_text = pure_text_file.read()
def get_tokens(str):
    return list(jieba.cut(str))

# pure_text = "我爱中华哈我爱中华"


tokens = get_tokens(pure_text)


one_gram_counts = Counter(tokens)


two_tokens = [tokens[i]+tokens[i+1] for i in range(len(tokens)-1)]

two_gram_counts = Counter(two_tokens)

def get_gram_count(gram_counts,word):
    if word in gram_counts:
        return gram_counts[word]
    else:
        return gram_counts.most_common()[-1][-1]


def two_gram_model(sentence):
    tokens_s = get_tokens(sentence)
    probility = 1
    for i in range(len(tokens_s)-1):
        current_word = tokens_s[i]
        next_word = tokens_s[i+1]

        two_gram_count = get_gram_count(two_gram_counts,current_word+next_word)
        one_gram_count = get_gram_count(one_gram_counts,next_word)

        prob = two_gram_count/one_gram_count
        probility *= prob

    return probility
pure_text_file.close()


print(two_gram_model("你是谁"))
