#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 17 06:32:28 2019

@author: llwu
"""

num_str = input("Input：")


num = int(num_str)

dict_facotr = {
    "2":0,
    "3":0,
    "5":0
}


def f(num):
    if num==1 or num<0:
        return num
    if num%30==0:
        dict_facotr['2'] += 1
        dict_facotr['3'] += 1
        dict_facotr['5'] += 1
        return f(int(num/30))
    if num%15==0:
        dict_facotr['3'] += 1
        dict_facotr['5'] += 1
        return f(int(num/15))
    if num%10==0:
        dict_facotr['2'] += 1
        dict_facotr['5'] += 1
        return f(int(num/10))
    if num%6==0:
        dict_facotr['3'] += 1
        dict_facotr['2'] += 1
        return f(int(num/6))
    if num%5==0:
        dict_facotr['5'] += 1
        return f(int(num / 5))
    if num%3==0:
        dict_facotr['3'] += 1
        return f(int(num / 3))
    if num%2==0:
        dict_facotr['2'] += 1
        return f(int(num / 2))
    return num*-1


def out_put():
    r = (f(num))
    if r==1:
        tmp = []
        for item in dict_facotr:
            tmp += [item for i in range(dict_facotr[item])]
        print("Output:(",",".join(tmp),")")
        print("Explanation:",num,"=","x".join(tmp))
    else:
        print("Output:None")
        print("Explanation:", num, "is not amazing since it includes another prime factor",r*-1)


out_put()