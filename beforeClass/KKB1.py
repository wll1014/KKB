#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 15 06:32:28 2019

@author: llwu
"""

import math

num_str = input("请输入整数：");


num = int(num_str)

num_n = math.sqrt(num)



n = math.floor(num_n)



left_min = n*n
mid_value = n*n + n+1
right_max = (n+1)*(n+1)




def getLeftRightSteps(input_num):
    letf_right_steps = math.ceil(input_num/2)-1
    up_down_steps = math.floor(input_num/2)
    return {
            "letf_right_steps":letf_right_steps,
            "up_down_steps":up_down_steps
            }
    

def getTotalSteps(num):
    if num==left_min:
        obj_steps = getLeftRightSteps(n)
        left_right_steps = obj_steps["letf_right_steps"]
        up_down_steps = obj_steps["up_down_steps"]
        
        return left_right_steps+up_down_steps
    else:
        if num<mid_value:
            obj_steps = getLeftRightSteps(n)
            left_right_steps = obj_steps["letf_right_steps"]
            up_down_steps = obj_steps["up_down_steps"]
            
            return left_right_steps + 1 +abs(up_down_steps-(num-left_min-1))
        else:
            obj_steps = getLeftRightSteps(n+1)
            left_right_steps = obj_steps["letf_right_steps"]
            up_down_steps = obj_steps["up_down_steps"]
            
            return abs(left_right_steps-(right_max-num)) + up_down_steps
            
            
total_steps = getTotalSteps(num)    
print("total_steps",total_steps)