import jieba
fail = [True,None]

def is_variable(pat):
    return pat.startswith('X')

def is_pattern_segment(pattern):
    return pattern.startswith('XZ')


def segment_match(pattern, saying):
    seg_pat, rest = pattern[0], pattern[1:]
    seg_pat = seg_pat.replace('XZ', 'X')

    if not rest: return (seg_pat, saying), len(saying)

    for i, token in enumerate(saying):
        if rest[0] == token and is_match(rest[1:], saying[(i + 1):]):
            return (seg_pat, saying[:i]), i

    return (seg_pat, saying), len(saying)


def is_match(rest, saying):
    if not rest and not saying:
        return True
    if not all(a.isalpha() for a in rest[0]):
        return True
    if rest[0] != saying[0]:
        return False
    return is_match(rest[1:], saying[1:])


def pat_match_with_seg(pattern, saying):
    if not pattern or not saying: return []

    pat = pattern[0]
    if is_pattern_segment(pat):
        match, index = segment_match(pattern, saying)
        return [match] + pat_match_with_seg(pattern[1:], saying[index:])
    elif pat == saying[0]:
        return pat_match_with_seg(pattern[1:], saying[1:])
    else:
        return fail
    # if is_variable(pat):
    #     return [(pat, saying[0])] + pat_match_with_seg(pattern[1:], saying[1:])
    # elif is_pattern_segment(pat):
    #     match, index = segment_match(pattern, saying)
    #     print("pat_segment:", pat)
    #     return [match] + pat_match_with_seg(pattern[1:], saying[index:])
    # elif pat == saying[0]:
    #     return pat_match_with_seg(pattern[1:], saying[1:])
    # else:
    #     return fail


def pat_to_dict(patterns):
    return {k: ''.join(v) if isinstance(v, list) else v for k, v in patterns}



def subsitite(rule, parsed_rules):
    if not rule: return []
    return [parsed_rules.get(rule[0], rule[0])] + subsitite(rule[1:], parsed_rules)

def get_my_response(saying, response_rules):
    response = ""
    for rule in response_rules:
        got_patterns = pat_match_with_seg(list(jieba.cut(rule)),list(jieba.cut(saying)))
        if (not got_patterns==fail):
            response_pattern = response_rules[rule]
            for response_item in response_pattern:
                response += ''.join(subsitite(list(jieba.cut(response_item)),pat_to_dict(got_patterns)))
            break
    return saying,response

my_rules = {
    "我有个XZY":["什么XY"],
    "我想让你XZY我":["我不想XY你"],
    "话别说的那么绝,我很好XZY的":["我没时间XY你"],
    "既然我们是XZY,我就不隐瞒你了":["说吧,XY"]
}
jieba.add_word("XZY")


saying,response = get_my_response("我有个想法哈",my_rules)
print("A:",saying)
print("B:",response)

saying,response = get_my_response("我想让你爱上我",my_rules)
print("A:",saying)
print("B:",response)

saying,response = get_my_response("话别说的那么绝,我很好喜欢的",my_rules)
print("A:",saying)
print("B:",response)

saying,response = get_my_response("既然我们是非常好的朋友,我就不隐瞒你了",my_rules)
print("A:",saying)
print("B:",response)