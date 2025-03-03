from datetime import datetime, timedelta

import pandas as pd

holidays = [
    '2025-01-01', '2025-01-28', '2025-01-29', '2025-01-29', '2025-01-30',
    '2025-01-31', '2025-02-01', '2025-02-02', '2025-02-03', '2025-02-04']  # 这是休假日期
workdays = ['2025-01-26', '2025-02-08']  # 这是调休上班的日期
holidays = [pd.to_datetime(date) for date in holidays]
workdays = [pd.to_datetime(date) for date in workdays]
# day0 = datetime.strptime('2024-09-01', '%Y-%m-%d')


def get_raw_data(filename: str = 'time_stat.xlsx', sheet_name: str = '原始数据-all'):
    # 读取Excel文件
    df = pd.read_excel(filename, sheet_name=sheet_name)
    df['date'] = pd.to_datetime(df['date'])
    # 将start_time和end_time转换为时间类型
    df['start'] = pd.to_datetime(df['start'], format='%H:%M:%S')
    df['end'] = pd.to_datetime(df['end'], format='%H:%M:%S')
    # 过滤掉周末（星期六和星期天）并排除 holidays，但保留 workdays
    is_weekend = df['date'].dt.weekday >= 5
    is_holiday = df['date'].isin(holidays)
    is_workday_weekend = df['date'].isin(workdays)
    df_filtered = df[~((is_weekend & ~is_workday_weekend) | is_holiday)]
    # 过滤过长的 duration
    df_filtered = df_filtered[(df_filtered['end'] - df_filtered['start']) <= timedelta(hours=13)]
    # 过滤掉 start_time 在上午6点前的行
    morning_7_am = pd.to_datetime('07:00:00', format='%H:%M:%S').time()
    night_23_pm = pd.to_datetime('23:00:00', format='%H:%M:%S').time()
    return df_filtered[(df_filtered['start'].dt.time >= morning_7_am) & (df_filtered['end'].dt.time <= night_23_pm)]


def calculate_status(row):
    duration_hours = row['duration'] / 3600  # 将秒转换为小时
    if duration_hours < 6:
        return "half"
    # elif row['date'] < day0:
    #     if duration_hours < 8.5:
    #         return "lack"
    #     elif duration_hours < 9:
    #         return "near"
    #     elif duration_hours >= 10:
    #         return "over"
    #     else:
    #         return "full"
    # else:
    if duration_hours < 9:
        return "lack"
    elif duration_hours < 10:
        return "near"
    elif duration_hours >= 11:
        return "over"
    else:
        return "full"


def write_single_day_summary(
        df: pd.DataFrame,
        filename: str = 'day_stat.xlsx', sheet_name: str = 'Summary'):
    # 按name和date分组，获取最早的start_time和最晚的end_time
    grouped = df.groupby(['name', 'date']).agg(
        work_start=('start', 'min'),
        work_end=('end', 'max')
    ).reset_index()
    # 计算duration，单位为秒
    grouped['duration'] = (grouped['work_end'] - grouped['work_start']).dt.total_seconds()
    grouped['hms'] = grouped['duration'].apply(lambda x: str(timedelta(seconds=x)))
    # 计算status列
    grouped['status'] = grouped.apply(calculate_status, axis=1)
    # format
    grouped['date'] = grouped['date'].dt.strftime('%Y-%m-%d')
    grouped['work_start'] = grouped['work_start'].dt.strftime('%H:%M:%S')
    grouped['work_end'] = grouped['work_end'].dt.strftime('%H:%M:%S')
    # 将结果写入另一个sheet
    if isinstance(filename, str) and filename.endswith('.xlsx'):
        with pd.ExcelWriter(filename, mode='w') as writer:  # 这里用mode='a'表示追加
            grouped.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"过滤后的日期汇总统计已生成在{filename}的{sheet_name}中。")
    return grouped


def write_total_summary(grouped: pd.DataFrame, filename: str = 'total_stat.xlsx', sheet_name: str = 'Workdays'):
    # 创建一个新的DataFrame用于存储统计结果
    result = grouped.groupby('name').agg(
        total_days=('date', 'nunique'),  # 每个name的唯一工作日数
        half_days=('status', lambda x: (x == 'half').sum()),  # half的天数
        valid_days=('status', lambda x: (x != 'half').sum()),  # valid_days
        lack_days=('status', lambda x: (x == 'lack').sum()),  # lack的天数
        near_days=('status', lambda x: (x == 'near').sum()),  # lack的天数
        full_days=('status', lambda x: (x == 'full').sum()),  # full的天数
        over_days=('status', lambda x: (x == 'over').sum()),  # over的天数
    )
    # 过滤掉 half_days 以外的状态来计算 lack、full、over 的平均时长
    filtered = grouped[grouped['status'].isin(['lack', 'full', 'over'])]
    # 计算每个name的lack、full、over的平均工作时长（秒）
    avg_duration = filtered.groupby('name')['duration'].mean().round()
    result['avg_dur'] = avg_duration
    # 将秒数转化为 时:分:秒
    result['avg_hms'] = avg_duration.apply(lambda x: str(timedelta(seconds=x)))
    # 计算 lack_ratio 和 ok_ratio
    result['lack_ratio'] = (result['lack_days'] / (result['total_days'] - result['half_days']))  # lack天数占比%
    result['near_ratio'] = (result['near_days'] / (result['total_days'] - result['half_days']))  # near天数占比%
    result['ok_ratio'] = ((result['full_days'] + result['over_days']) / (
            result['total_days'] - result['half_days']))  # full+over天数占比%
    # 将统计结果写入新的 Excel 文件
    if isinstance(filename, str) and filename.endswith('.xlsx'):
        with pd.ExcelWriter(filename, mode='w') as writer:
            result.to_excel(writer, sheet_name=sheet_name, index=True)
        print(f"最终统计结果已生成并保存到{filename}的{sheet_name}中。")
    return result
