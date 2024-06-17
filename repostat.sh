#!/bin/bash

# 设置起始和结束时间
case "$#" in
    0)
        # 如果没有日期输入，取最近30天
        if [[ "$(uname)" == "Darwin" ]]; then
            # macOS系统
            start_date=$(date -v-30d +%Y-%m-%d)
        else
            # 假设是Linux系统
            start_date=$(date --date='30 days ago' +%Y-%m-%d)
        fi
        end_date=$(date +%Y-%m-%d)
        ;;
    1)
        # 如果只有一个日期输入，从该日期到最新
        start_date=$1
        end_date=$(date +%Y-%m-%d)
        ;;
    2)
        # 如果输入了两个日期
        start_date=$1
        end_date=$2
        ;;
    *)
        # 如果输入的参数多于两个，显示用法并退出
        echo "Usage: $0 [start_date [end_date]]"
        echo "Example: $0 2022-01-01 2022-02-01"
        exit 1
        ;;
esac

## 进入Git仓库目录
#cd /path/to/myrepo

# Step1: 获取所有分支的提交ID，并存储到临时文件中，确保每个提交只出现一次
# 确保临时文件不存在
rm -f commit.temp.log

# 获取所有本地分支列表
branches=$(git branch | sed 's/^\*?\s*//')

# 第一个循环：遍历所有分支，收集所有的commit ID
for branch in $branches
do
    git checkout $branch > /dev/null 2>&1
    # 记录每个分支的提交ID到文件，去重复
    git log --since="$start_date" --until="$end_date" --format="%H" >> commit.temp.log
done

# 切换回主分支
git checkout main > /dev/null 2>&1

# 对commit.temp.log中的提交ID去重
sort -u commit.temp.log -o commit.temp.log


# Step2: 遍历所有提交，统计代码行变动数

# 总变动行数初始化
total_additions=0
total_deletions=0

# 从commit.temp.log中读取每个唯一的commit ID
while read commit
do
    # 获取该提交的代码行变动数
    stats=$(git diff $commit^! --shortstat | sed -E 's/[[:space:]]*([0-9]+) file(s)? changed(, ([0-9]+) insertion(s)?\(\+\))?((, )?([0-9]+) deletion(s)?\(-\))?/\1 \4 \8/')
    if [[ $stats =~ ^([0-9]*)\ ([0-9]*)\ ([0-9]*)$ ]]; then
        files_changed=${BASH_REMATCH[1]:-0}
        insertions=${BASH_REMATCH[2]:-0}
        deletions=${BASH_REMATCH[3]:-0}
    fi

    echo "Commit $commit: Files changed: $files_changed, Insertions: $insertions, Deletions: $deletions"

    # 累加到总数
    total_additions=$(($total_additions + $insertions))
    total_deletions=$(($total_deletions + $deletions))
done < commit.temp.log

echo "Total additions: $total_additions"
echo "Total deletions: $total_deletions"
