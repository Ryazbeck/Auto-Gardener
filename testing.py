def mergeStrings(s1, s2, out=[]):
    if s1 is None or s2 is None:
        return ''
    if len(s1) == 0:
        out.extend(s2)
        return ''.join(out)
    elif len(s2) == 0:
        out.extend(s1)
        return ''.join(out)
    else:
        if s1.count(s1[0]) < s2.count(s2[0]):
            _out = [s1[0]]
            s1 = s1[1::]
        elif s1.count(s1[0]) == s2.count(s2[0]):
            if s1[0] <= s2[0]:
                _out = [s1[0]]
                s1 = s1[1::]
            elif s1[0] > s2[0]:
                _out = [s2[0]]
                s2 = s2[1::]
        else:
            _out = [s2[0]]
            s2 = s2[1::]
        out = out + sorted(_out)
        return mergeStrings(s1, s2, out)

j = mergeStrings("super", "tower")
k = mergeStrings("suuper", "tower")
l = mergeStrings("acb", "cccbd")
m = mergeStrings(None, None)
print([x for x in [j, k, l, m]])
