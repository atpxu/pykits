DIGITS = '零一二三四五六七八九'
BIG_DIGITS = '零壹贰叁肆伍陆柒捌玖'
SMALL_UNITS = ['', '十', '百', '千']
SMALL_UNITS2 = ['', '拾', '佰', '仟']
LARGE_UNITS = ['', '万', '亿', '万']


def convert_four_digit(number, digits=BIG_DIGITS, units=SMALL_UNITS2):
    if number == 0:
        return ''
    out, need_zero = '', False
    for i in range(4):
        number, r = divmod(number, 10)
        if r > 0:
            if need_zero:
                out = '零' + out
                need_zero = False
            out = digits[r] + units[i] + out
        else:
            need_zero = True
    out = out.rstrip('零')
    if out.startswith('一十'):
        out = out[1:]
    return out


def convert_digit(number):
    if number == 0:
        return '零'
    out, need_zero = '', False
    for i in range(4):
        number, r = divmod(number, 10000)
        if r > 0:
            if need_zero:
                if not out.startswith('亿'):
                    out = '零' + out
                need_zero = False
            p = convert_four_digit(r)
            if p:
                out = convert_four_digit(r) + LARGE_UNITS[i] + out
        if r < 1000:
            need_zero = True
        if number == 0:
            break
        elif i == 2 and number > 0 and r == 0:
            out = '亿' + out
    out = out.rstrip('零')
    return out
