import sys
import re


def add(d, n):
    # d {"n": 0}
    d["n"] += n


def update_str(s):
    s += "abc"


if __name__ == '__main__':
    # b = {
    #     "n": 1
    # }
    # add(b, 10)
    # print(b["n"])
    a = "abc"
    update_str(a)
    print(a)
    # html_text = "abc-cba-dbd-cba-cba"
    # # 正则表达式是一个字符串，在字符串里面，\也是一个转义符号
    # # 在正则表达式里面，\也是一个转义符号
    # # 1. 先是字符串，2 轮到正则引擎去解析
    # # raw string 所见即所得
    # m = re.search(r"(\w{3})-(\w{3})-\1", html_text)
    # if m is None:
    #     print("m is none")
    # else:
    #     print(m.group())
#     text = """abc\
# abc
# abc"""
#     ## 我们希望打印出三个abc
#     m = re.findall(r"abc", text)
#     if m is None:
#         print("m is none")
#     else:
#         print(m)

#     text = """cbd\
# abc
# abc"""
#     # 我们希望匹配第二行开始的abc
#     m = re.search(r"bc", text, re.M)
#     if m is None:
#         print("m is none")
#     else:
#         print(m.pos)
#     text = "abbcd"
#     m = re.match(r"ab(\w+)", text)
#     print(m.start(1))
#     a = "1"
#     print(id(a))
#     a = "2"
#     print(id(a))

    b = {
        "n": 1
    }
    # print(id(b))
    # b["n"] = 2
    # print(id(b))
    # b = {
    #     "n": 3
    # }
    # print(id(b))