# 0 表示空格，1-9 表示数字 1-9
# 每一行用一个 32 位整数表示，每个整数的 9 位表示一行的 9 个格子
# 9 个数字组成一个字符串，9 行组成一个 81 位的字符串。4*9=36 个字节

# puzzle = '8.17..4..;...1...25;2...3..7.;3......52;....9....;69......3;.4..1...7;75...2...;..8..45.6'
puzzle = '801700400000100025200030070300000052000090000690000003040010007750002000008004506'
ints = []
i = 0
while i < len(puzzle):
    chunk = puzzle[i:i+9]
    ints.append(int(chunk))
    i += 9

print(puzzle)

print(len(ints))
int_str = '\r\n'.join(f"{num:09d}" for num in ints)
print(int_str)

# https://www.sudokuwiki.org/sudoku.htm
