from array import array

'''
'b'	signed char	int	1字节有符号整型
'B'	unsigned char	int	1字节无符号整型
'h'	signed short	int	2字节有符号整型
'H'	unsigned short	int	2字节无符号整型
'i'	signed int	int	通常 4 字节
'I'	unsigned int	int	通常 4 字节
'l'	signed long	int	4/8 字节
'L'	unsigned long	int	4/8 字节
'q'	signed long long	int	8 字节
'Q'	unsigned long long	int	8 字节
'f'	float	float	4 字节
'd'	double	float	8 字节
'''

arr = array('i')
arr.append(1)
print(len(arr))
