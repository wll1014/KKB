#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 17 21:32:28 2019

@author: llwu
"""
import random
import copy


print(
    ''

)
# simple_grammar =
"""
sentence => noun_phrase verb_phrase 
noun_phrase => Article Adj* noun
Adj* => null | Adj Adj*
verb_phrase => verb noun_phrase
Article => 一个 | 这个
noun => 女人| 篮球|桌子|小猫
verb => 看着 | 听着 | 看见
Adj=> 蓝色的| 好看的|小小的|年轻的 
"""

# grammar = input()
grammar_dict_or={}
grammar_dict_and={}

grammars = [
'sentence => noun_phrase verb_phrase ',
'noun_phrase => Article Adj* noun',
'Adj* => null | Adj Adj*',
'verb_phrase => verb noun_phrase',
'Article => 一个 | 这个',
'noun => 女人| 篮球|桌子|小猫',
'verb => 看着 | 听着 | 看见',
'Adj=> 蓝色的| 好看的|小小的|年轻的'
]
print('simple_grammar="""')
print("\n".join(grammars),'"""')

for item in grammars:
    grammar_list = item.split("=>")
    grammar_name = grammar_list[0].strip()
    grammar_content = grammar_list[1].strip()
    if grammar_content.__contains__("|"):
        grammar_dict_or[grammar_name] = grammar_content.split("|")
        for i in range(len(grammar_dict_or[grammar_name])):
            grammar_dict_or[grammar_name][i] = grammar_dict_or[grammar_name][i].strip();
            if grammar_dict_or[grammar_name][i].__contains__(" "):
                grammar_dict_and[grammar_dict_or[grammar_name][i]] = grammar_dict_or[grammar_name][i].split(" ")
    else:
        if grammar_content.__contains__(" "):
            grammar_dict_and[grammar_name] = grammar_content.split(" ")




def generate(grammar_name):
    result = []
    generateBy(grammar_name,result)
    return "".join(result)

def generateBy(grammar_name,result):

    if (not grammar_dict_or.__contains__(grammar_name)) and (not grammar_dict_and.__contains__(grammar_name)):
        if grammar_name == "null":
            return result
        else:
            result += [grammar_name]
            return grammar_name
    else:
        if grammar_dict_or.__contains__(grammar_name):
            randomGrammarIndex = random.randint(0, len(grammar_dict_or[grammar_name]) - 1)
            generateBy(grammar_dict_or[grammar_name][randomGrammarIndex],result)
        else:
            if grammar_dict_and.__contains__(grammar_name):
                for item in grammar_dict_and[grammar_name]:
                    generateBy(item,result)


s = generate("sentence")
print()
print("Output:",s)
