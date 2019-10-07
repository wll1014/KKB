import jieba
from collections import Counter
import random


booking_room_gram = '''
booking_room = please verb time location room
please = null| 请| 麻烦 | 烦请
verb = 预定 | 查找 | 预约 | 查一下 | 定一下
time = 周一|周二|周三 | 周四 | 周五 | 周六 | 周天
location = 上海 | 北京 | 深圳 | 广州 | 武汉
room = 会议室room1 | 会议室room2 | 会议室room3
'''

max_random_count = 10


pure_text_file = open("pure_text.txt","r")
pure_text = pure_text_file.read()
pure_text_file.close()




def generate(gram_rules,target):
    if target in gram_rules:
        candidates = gram_rules[target]
        candidate = random.choice(candidates)
        return "".join(generate(gram_rules,c.strip()) for c in candidate.split())
    else:
        return '' if target=='null'''else target


def generate_by_gram(gram,target,stmt_split = "=",or_split="|"):
    gram_rules = dict()
    for line in gram.split('\n'):
        if not line:
            continue
        stmt,exper = line.split(stmt_split)
        gram_rules[stmt.strip()] = exper.split(or_split)
    return generate(gram_rules,target)




def get_tokens(str):
    return list(jieba.cut(str))



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

def generate_best(gram,two_gram_model):
    sentence_pro = []
    for i in range(max_random_count):

        sentence = generate_by_gram(gram,"booking_room")
        probility = two_gram_model(sentence)
        sentence_pro.append((sentence,probility))
    sentence_sotred = sorted(sentence_pro, key=lambda x: x[1], reverse=True)
    sentence_best = sentence_sotred[1]
    return sentence_best




# pure_text = "我爱中华哈我爱中华"

tokens = get_tokens(pure_text)

one_gram_counts = Counter(tokens)

two_tokens = [tokens[i]+tokens[i+1] for i in range(len(tokens)-1)]

two_gram_counts = Counter(two_tokens)


sentence_best = generate_best(booking_room_gram,two_gram_model)

print(sentence_best)


'''
#模型缺陷
文本数据比较单一，可以丰富下文本数据集

'''

