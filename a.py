import re

if __name__ == '__main__':
    with open("./yuan.txt") as f:
        lines = []
        for line in f.readlines():
            if not line.strip().startswith("--"):
                lines.append(line)
        print(lines)