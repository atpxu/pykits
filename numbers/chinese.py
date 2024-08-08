DIGITS = '零一二三四五六七八九'
CAP_DIGITS = '零壹贰叁肆伍陆柒捌玖'
SMALL_UNITS = ['', '十', '百', '千']
CAP_SMALL_UNITS = ['', '拾', '佰', '仟']
LARGE_UNITS = ['', '万', '亿', '万']
CAP_LARGE_UNITS = ['', '萬', '億', '萬']


def convert_four_digit(number: int, capitalize: bool = True):
    if not (0 < number < 10000):
        raise ValueError('number must be in range 0-9999')
    if number == 0:
        return ''
    if capitalize:
        digits = CAP_DIGITS
        units = CAP_SMALL_UNITS
        trimp = '壹拾'
    else:
        digits = DIGITS
        units = SMALL_UNITS
        trimp = '一十'
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
    if out.startswith(trimp):
        out = out[1:]
    return out


def convert_digit(number:int, capitalize=True):
    if not (0 <= number < 1000000000000):
        raise ValueError('number must be in range 0-999999999999')
    if number == 0:
        return '零'
    out, need_zero = '', False
    units = CAP_LARGE_UNITS if capitalize else LARGE_UNITS
    for i in range(4):
        number, r = divmod(number, 10000)
        if r > 0:
            if need_zero:
                if not out.startswith(units[2]):
                    out = '零' + out
                need_zero = False
            p = convert_four_digit(r)
            if p:
                out = convert_four_digit(r, capitalize=capitalize) + LARGE_UNITS[i] + out
        if r < 1000:
            need_zero = True
        if number == 0:
            break
        elif i == 2 and number > 0 and r == 0:
            out = units[2] + out
    out = out.rstrip('零')
    return out
