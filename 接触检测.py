import pandas as pd
import numpy as np
from math import sqrt
import csv
from datetime import datetime

class ProximityDetector:
    def __init__(self):
        # 固定点坐标和阈值设置
        self.fixed_points = {
            "灭火器把手": {"position": (2.84, 0.69, 0.5), "threshold": 0.25},
            "油箱顶部": {"position": (2.86, 0.42, 0.25), "threshold": 0.35},
            "墙壁电源": {"position": (2.44, 2.57, 0.97), "threshold": 0.25},
            "焊机电源": {"position": (1.45, 2.1, 0.39), "threshold": 0.5},
            "电压电流旋钮": {"position": (1.56, 1.5, 0.37), "threshold": 0.6},
            "接地夹下端": {"position": (3.02, 1.53, 1.61), "threshold": 0.63},
            "焊把钳下端": {"position": (3.02, 1.15, 1.56), "threshold": 0.75},
            "锤子": {"position": (0.24, 0.17, 0), "threshold": 0.6},
            "待焊钢板": {"position": (0.81, 0.46, 0), "threshold": 0.2},
            "面罩把手": {"position": (0.24, 0.83, 0), "threshold": 0.45},
            "钢刷": {"position": (0.24, 0.46, 0), "threshold": 0.4}
        }
    
    def calculate_distance(self, pos1, pos2):
        """计算三维空间中两点之间的距离"""
        return sqrt((pos1[0] - pos2[0])**2 + 
                   (pos1[1] - pos2[1])**2 + 
                   (pos1[2] - pos2[2])**2)
    
    def detect_proximity(self, tag_position, timestamp=None, tag_id=None):
        """
        检测标签与固定点的距离
        参数:
        - tag_position: 元组 (x, y, z)，标签当前位置
        - timestamp: 时间戳
        - tag_id: 标签ID
        返回:
        - alarms: 触发警报的点列表
        """
        ##############所有阈值内的点################
    #     alarms = []
        
    #     for point_name, point_info in self.fixed_points.items():
    #         fixed_pos = point_info["position"]
    #         threshold = point_info["threshold"]
            
    #         distance = self.calculate_distance(tag_position, fixed_pos)
            
    #         if distance <= threshold:
    #             alarm_info = {
    #                 "contact_time": timestamp,
    #                 "threshold_value": threshold,
    #                 "point_name": point_name,
    #                 "fixed_point_x": fixed_pos[0],
    #                 "fixed_point_y": fixed_pos[1],
    #                 "fixed_point_z": fixed_pos[2],
    #                 "tag_x": tag_position[0],
    #                 "tag_y": tag_position[1],
    #                 "tag_z": tag_position[2],
    #                 "tag_id": tag_id,
    #                 "distance": distance
    #             }
    #             alarms.append(alarm_info)
        
    #     return alarms
    # closest_alarm = None

        ##########阈值内的最近距离的点###########################
        closest_alarm = None  # 在循环外部初始化
        min_distance = float('inf')  # 初始化为无穷大
        
        for point_name, point_info in self.fixed_points.items():
            fixed_pos = point_info["position"]
            threshold = point_info["threshold"]
            
            distance = self.calculate_distance(tag_position, fixed_pos)
            
            # 检查距离是否在阈值内，并且比当前最小距离更小
            if distance <= threshold and distance < min_distance:
                min_distance = distance
                closest_alarm = {
                    "contact_time": timestamp,
                    "threshold_value": threshold,
                    "point_name": point_name,
                    "fixed_point_x": fixed_pos[0],
                    "fixed_point_y": fixed_pos[1],
                    "fixed_point_z": fixed_pos[2],
                    "tag_x": tag_position[0],
                    "tag_y": tag_position[1],
                    "tag_z": tag_position[2],
                    "tag_id": tag_id,
                    "distance": distance
                }
        
        # 如果找到了最近的点，返回包含该点的列表；否则返回空列表
        return [closest_alarm] if closest_alarm is not None else []

#######################使用距离与阈值的比值来判断最接近的点############
        # closest_alarm = None
        # min_ratio = float('inf')  # 初始化为无穷大
        
        # for point_name, point_info in self.fixed_points.items():
        #     fixed_pos = point_info["position"]
        #     threshold = point_info["threshold"]
            
        #     distance = self.calculate_distance(tag_position, fixed_pos)
            
        #     # 计算距离与阈值的比值
        #     ratio = distance / threshold
            
        #     # 只有当距离在阈值内（ratio <= 1）且比值最小的点才被记录
        #     if ratio <= 1.0 and ratio < min_ratio:
        #         min_ratio = ratio
        #         closest_alarm = {
        #             "contact_time": timestamp,
        #             "threshold_value": threshold,
        #             "point_name": point_name,
        #             "fixed_point_x": fixed_pos[0],
        #             "fixed_point_y": fixed_pos[1],
        #             "fixed_point_z": fixed_pos[2],
        #             "tag_x": tag_position[0],
        #             "tag_y": tag_position[1],
        #             "tag_z": tag_position[2],
        #             "tag_id": tag_id,
        #             "distance": distance,
        #             "distance_ratio": ratio,  # 添加比值信息
        #         }
        
        # # 如果找到了最近的点，返回包含该点的列表；否则返回空列表
        # return [closest_alarm] if closest_alarm is not None else []
    
    def process_trajectory_file(self, input_file_path, output_file_path):
        """
        处理轨迹CSV文件，检测接近事件并输出结果
        输入文件格式: rangetime(ms), tag_ID, x(m), y(m), z(m), range0-range7, rx_pwr, accel_x-accel_z, gyro_x-gyro_z, mag_x-mag_z, roll-pitch-yaw
        """
        # 读取输入CSV文件
        df = pd.read_csv(input_file_path, encoding='utf-8')
        
        print(f"输入文件列名: {list(df.columns)}")
        print(f"数据总行数: {len(df)}")
        
        # 根据实际列名进行映射
        column_mapping = {
            'rangetime(ms)': ['rangetime(ms)', 'rangetime', 'time', 'timestamp'],
            'tag_ID': ['tag_ID', 'tag', 'tag id', 'Tag ID'],
            'x(m)': ['x(m)', 'x', 'x_pos', 'pos_x'],
            'y(m)': ['y(m)', 'y', 'y_pos', 'pos_y'],
            'z(m)': ['z(m)', 'z', 'z_pos', 'pos_z']
        }
        
        # 自动识别并重命名列
        for target_col, possible_names in column_mapping.items():
            for possible_name in possible_names:
                if possible_name in df.columns and target_col != possible_name:
                    df.rename(columns={possible_name: target_col}, inplace=True)
                    print(f"已将列 '{possible_name}' 重命名为 '{target_col}'")
                    break
        
        # 检查必需的列
        required_cols = ['rangetime(ms)', 'tag_ID', 'x(m)', 'y(m)', 'z(m)']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"错误: 缺少必需的列: {missing_cols}")
            return []
        
        results = []
        total_rows = len(df)
        
        for index, row in df.iterrows():
            # 检查坐标值是否为有效数字（不是NaN）
            try:
                x_val = float(row['x(m)'])
                y_val = float(row['y(m)'])
                z_val = float(row['z(m)'])
                
                # 检查是否为有效数值
                if pd.isna(x_val) or pd.isna(y_val) or pd.isna(z_val):
                    continue
                    
                tag_pos = (x_val, y_val, z_val)
            except (ValueError, TypeError):
                print(f"跳过无效行 {index}: x={row['x(m)']}, y={row['y(m)']}, z={row['z(m)']}")
                continue
            
            timestamp = row['rangetime(ms)']
            tag_id = row['tag_ID']
            
            # 检测接近事件
            alarms = self.detect_proximity(tag_pos, timestamp, tag_id)
            
            # 添加到结果列表
            results.extend(alarms)
            
            # 输出检测到的警报
            if alarms:
                for alarm in alarms:
                    print(f"[警报] 时间: {alarm['contact_time']}, "
                          f"标签ID: {alarm['tag_id']}, "
                          f"接近点: {alarm['point_name']}, "
                          f"距离: {alarm['distance']:.3f}, "
                          f"阈值: {alarm['threshold_value']}")
            
            # 显示进度
            if (index + 1) % 1000 == 0:
                print(f"已处理 {index + 1}/{total_rows} 行")
        
        # 将结果保存到输出文件
        if results:
            output_df = pd.DataFrame(results)
            # 按时间和标签ID排序
            output_df = output_df.sort_values(['contact_time', 'tag_id'])
            output_df.to_csv(output_file_path, index=False, encoding='utf-8-sig')
            print(f"检测结果已保存到: {output_file_path}")
            print(f"共检测到 {len(results)} 次接近事件")
            
            # 统计信息
            if len(results) > 0:
                stats_df = pd.DataFrame(results)
                print("\n统计信息:")
                print(stats_df['point_name'].value_counts())
        else:
            print("未检测到任何接近事件")
        
        return results

# 使用示例
if __name__ == "__main__":
    # 创建接近检测器
    detector = ProximityDetector()

    # 处理输入文件并生成输出文件
    input_file = r"D:\实验\1.21交职UWB报警实验\双手1，阈值0.5\双手轨迹1.csv"
    output_file = r"D:\实验\1.21交职UWB报警实验\双手1，阈值0.5\接触检测结果1.1.csv"
    # input_file = r"d:\QTproject\hr_rtls_pc-master\Logs\1.21交职UWB报警实验\左手报警，阈值0.5\左手轨迹.csv"
    # output_file = r"d:\QTproject\hr_rtls_pc-master\Logs\1.21交职UWB报警实验\左手报警，阈值0.5\左手接触检测结果.csv"
    
    try:
        results = detector.process_trajectory_file(input_file, output_file)
        print(f"处理完成，检测到 {len(results)} 次接触事件")
    except Exception as e:
        print(f"处理文件时出错: {e}")
        
        # 如果编码有问题，尝试不同的编码方式
        try:
            df = pd.read_csv(input_file, encoding='gbk')
            print(f"使用GBK编码读取文件成功，列名: {list(df.columns)}")
            results = detector.process_trajectory_file(input_file, output_file)
        except Exception as e2:
            print(f"仍然无法处理文件: {e2}")