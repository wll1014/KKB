import random
booking_room_gram = '''
booking_room = please verb time location room
please = null| 请| 麻烦 | 烦请
verb = 预定 | 查找 | 预约 | 查一下 | 定一下
time = 周一|周二|周三 | 周四 | 周五 | 周六 | 周天
location = 上海 | 北京 | 深圳 | 广州 | 武汉
room = 会议室room1 | 会议室room2 | 会议室room3
'''

answer_gram = '''
answer = sorry_no | hello_yes
sorry_no = sorry no 
hello_yes = hello yes
sorry = 很抱歉 | 非常抱歉 | sorry | 对不起
hello = 你好 | 您好 
yes = 已帮您预定好会议室|会议室存在且已帮您预定
no = 会议室不存在 | 会议室已被预定完
'''

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


def generate_n(grams,targets):
    result = [generate_by_gram(grams[i],targets[i]) for i in range(len(grams))]
    return result


grams = [booking_room_gram,answer_gram]
targets = ["booking_room","answer"]

r = generate_n(grams, targets)

print(r)

#执行10次genrate_n

r_10 = [generate_n(grams, targets) for i in range(10)]

print(r_10)