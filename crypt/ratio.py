from datetime import datetime, timedelta


def last_friday_of_quarter(today=None):
    if today is None:
        today = datetime.today()
    # 确定当前季度的最后一个月
    quarter_end_month = (today.month - 1) // 3 * 3 + 3
    # 获取该月的第一天，然后退一天得到上个月最后一天
    first_day_next_month = datetime(today.year, quarter_end_month + 1, 1) if quarter_end_month < 12 else datetime(
        today.year + 1, 1, 1)
    last_day = first_day_next_month - timedelta(days=1)
    # 找最后一个星期五
    while last_day.weekday() != 4:  # 4 表示星期五
        last_day -= timedelta(days=1)
    return last_day

