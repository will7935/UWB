import pandas as pd
from io import StringIO

def clean_csv_content(content):
    """
    清理CSV内容，移除多余的逗号和空格
    """
    lines = content.strip().split('\n')
    cleaned_lines = []
    
    for line in lines:
        # 移除行末尾的多余逗号
        cleaned_line = line.rstrip(',')  # 移除行尾的逗号
        cleaned_line = ','.join(cleaned_line.split(','))  # 确保逗号之间没有多余空格
        cleaned_lines.append(cleaned_line)
    
    return '\n'.join(cleaned_lines)

def merge_and_sort_csv_files_cleaned(file1_path, file2_path, output_path):
    """
    清理CSV格式后合并文件
    """
    # 读取文件的原始文本内容
    with open(file1_path, 'r', encoding='utf-8') as f:
        content1 = f.read()
    
    with open(file2_path, 'r', encoding='utf-8') as f:
        content2 = f.read()
    
    # 清理CSV内容，移除多余的逗号
    cleaned_content1 = clean_csv_content(content1)
    cleaned_content2 = clean_csv_content(content2)
    
    # 分离标题和数据行
    lines1 = cleaned_content1.strip().split('\n')
    lines2 = cleaned_content2.strip().split('\n')
    
    header = lines1[0]  # 表头应该是一样的
    data_lines1 = lines1[1:]  # 去掉表头，剩下的都是数据
    data_lines2 = lines2[1:]  # 去掉表头，剩下的都是数据
    
    # 构建完整的数据行
    all_data_lines = data_lines1 + data_lines2
    
    # 将数据行连接成一个字符串，加上表头
    complete_content = header + '\n' + '\n'.join(all_data_lines)
    
    # 使用StringIO创建一个类似文件的对象
    df_combined = pd.read_csv(StringIO(complete_content))
    
    print(f"组合后DataFrame形状: {df_combined.shape}")
    print(f"列名: {list(df_combined.columns)}")
    print(f"前几行数据:")
    print(df_combined.head())
    
    # 检查时间列
    print(f"时间列前几个值: {df_combined['rangetime(ms)'].head().tolist()}")
    
    # 将时间列转换为datetime类型
    df_combined['rangetime(ms)'] = pd.to_datetime(df_combined['rangetime(ms)'], 
                                                 format='%Y-%m-%d %H:%M:%S.%f', 
                                                 errors='coerce')
    
    # 过滤掉转换失败的行（即NaT）
    valid_data = df_combined[df_combined['rangetime(ms)'].notna()].copy()
    
    print(f"有效数据条数: {len(valid_data)}")
    
    # 按时间列升序排序
    sorted_df = valid_data.sort_values(by='rangetime(ms)')
    
    # 重置索引
    sorted_df.reset_index(drop=True, inplace=True)
    
    # 保存合并后排序的结果
    sorted_df.to_csv(output_path, index=False)
    
    print(f"成功合并文件并按时间排序！")
    print(f"最终数据条数: {len(sorted_df)}")
    print(f"时间范围: {sorted_df['rangetime(ms)'].min()} 到 {sorted_df['rangetime(ms)'].max()}")
    
    return sorted_df

# 使用清理后的函数
if __name__ == "__main__":
    tag1_file = r"D:\QTproject\hr_rtls_pc-master\Logs\1.21交职UWB报警实验\双手5，阈值0.3\20260121_161108_RTLS1_Tag1_log.csv"
    tag0_file = r"D:\QTproject\hr_rtls_pc-master\Logs\1.21交职UWB报警实验\双手5，阈值0.3\20260121_161108_RTLS1_Tag2_log.csv"
    output_file = r"D:\QTproject\hr_rtls_pc-master\Logs\1.21交职UWB报警实验\双手5，阈值0.3\双手轨迹5.csv"
    
    result_df = merge_and_sort_csv_files_cleaned(tag1_file, tag0_file, output_file)
    
    # 显示前几行数据以验证结果
    print("\n合并后前5行数据:")
    print(result_df.head())
    
    print(f"\n时间范围: {result_df['rangetime(ms)'].min()} 到 {result_df['rangetime(ms)'].max()}")


