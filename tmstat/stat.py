import argparse

import work_time


def main():
    parser = argparse.ArgumentParser(description='统计工时，原始数据表中需要包含name/date/start/end列')
    parser.add_argument(
        '-i', '--input', type=str, help='原始数据明细文件名称')
    parser.add_argument(
        '-s', '--sheet', type=str, help='原始文件中的sheet名称',
        required=False, default='原始数据-all')
    parser.add_argument(
        '-o', '--output', type=str, help='输出的最终文件名称',
        required=False, default='total_stat.xlsx')
    parser.add_argument(
        '-d', '--daily', type=str, help='日期明细汇总文件名称',
        required=False, default='day_stat.xlsx')

    args = parser.parse_args()
    dframe = work_time.get_raw_data(filename=args.input, sheet_name=args.sheet)
    daily = work_time.write_single_day_summary(dframe, filename=args.daily)
    work_time.write_total_summary(daily, filename=args.output)


if __name__ == '__main__':
    main()
