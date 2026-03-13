import pandas as pd
from datetime import datetime

# 定义状态类
class State:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def execute(self):
        print(f" 当前状态: {self.name} - {self.description}")

# 状态管理器
class StateManager:
    def __init__(self):
        self.completed_states = set()  # 已完成的状态集合
        self.last_triggered_time = {}  # 记录每个状态最后触发的时间戳
        self.last_triggered_time_per_point = {}  # 记录每个检测点最后触发的时间戳
        self.partial_conditions = {}  # 缓存部分满足的条件
        self.state_triggers = {
            "S1": {"point_name": "灭火器把手", "condition": lambda d, t: d < t},
            "S2": {"point_name": "油箱顶部", "condition": lambda d, t: d < t},
            "S3": {
                "logic": "AND",  # 和关系
                "conditions": [
                    {"point_name": "焊机电源", "condition": lambda d, t: d < t},
                    {"point_name": "电压电流旋钮", "condition": lambda d, t: d < t}
                ]
            },
            "S4": {
                "logic": "AND",  # 和关系
                "conditions": [
                    {"point_name": "焊把钳下端", "condition": lambda d, t: d < t},
                    {"point_name": "接地夹下端", "condition": lambda d, t: d < t}
                ],
                "pre_condition": "S3"
            },
            "S5": {"point_name": "墙壁电源", "condition": lambda d, t: d < t,"pre_condition": "S4"},
            "S6": {"point_name": "焊机电源", "condition": lambda d, t: d < t,"pre_condition": "S4"},
            "S7": {"point_name": "电压电流旋钮", "condition": lambda d, t: d < t,"pre_condition": "S4"},
            "S8": {
                "logic": "AND",  # 和关系
                "conditions": [
                    {"point_name": "焊把钳下端", "condition": lambda d, t: d < t},
                    {"point_name": "接地夹下端", "condition": lambda d, t: d < t}
                ],
                "pre_condition": "S4"
            },
            "S9": {
                "logic": "AND",  # 和关系
                "conditions": [
                    {"point_name": "待焊钢板", "condition": lambda d, t: d < t},
                    {"point_name": "面罩把手", "condition": lambda d, t: d < t},
                    # {"point_name": "钢刷", "condition": lambda d, t: d < t}
                ]
            },
            "S10": {"point_name": "焊机电源", "condition": lambda d, t: d < t,"pre_condition": "S9"},
            "S11": {"point_name": "墙壁电源", "condition": lambda d, t: d < t,"pre_condition": "S9"},
            "S12": {
                "logic": "AND",  # 和关系
                "conditions": [
                    {"point_name": "焊把钳下端", "condition": lambda d, t: d < t},
                    {"point_name": "接地夹下端", "condition": lambda d, t: d < t}
                ],
                "pre_condition": "S11"
            },
            "S13": {"point_name": "锤子", "condition": lambda d, t: d < t,"pre_condition": "S9"},  
            # "S14": {"auto_transition_to": "S14" },  #自动转移到 S14终止状态
        }
    
    ##########判断是否满足多点规则，超出时间限制判断为不满足
    def clear_expired_cache(self, current_time, timeout=25):
        """
        清除超过指定时间（timeout）的缓存
        :param current_time: 当前时间戳
        :param timeout: 超时时间（秒）
        """
        expired_states = []
        for state_key, cache_info in self.partial_conditions.items():
            timestamp = cache_info["timestamp"]
            if (current_time - timestamp).total_seconds() >= timeout:
                expired_states.append(state_key)
        
        # 清除超时缓存
        for state_key in expired_states:
            print(f"[INFO] Clearing expired cache for state {state_key}")
            del self.partial_conditions[state_key]
    def check_and_trigger(self, row, current_state_name):
        triggered_states = []

        # 使用文件中的时间戳
        current_time = row["contact_time"]
        point_name = row["point_name"]
        self.clear_expired_cache(current_time, timeout=25)  # 清除超时缓存

        for state_key, rule in self.state_triggers.items():
            logic = rule.get("logic", "AND")
            conditions = rule.get("conditions", [])
            pre_condition = rule.get("pre_condition")

            # 单点规则处理
            if "point_name" in rule:
                # 检查S3的判断是否结束
                # if state_key == "S7" and "S3" in self.partial_conditions and self.partial_conditions["S3"]["points"]:
                #     print(f"[INFO] S3 缓存未清空，跳过状态 S7 的触发")
                #     continue
                # if state_key == "S6" and "S3" in self.partial_conditions and self.partial_conditions["S3"]["points"]:
                #     print(f"[INFO] S3 缓存未清空，跳过状态 S6 的触发")
                #     continue
                if (
                    row["point_name"] == rule["point_name"]
                    and rule["condition"](row["distance"], row["threshold_value"])
                ):
                    # 检查前置条件是否满足
                    if pre_condition and pre_condition not in self.completed_states:
                        print(f"[WARNING] 前置条件 {pre_condition} 未满足，跳过状态 {state_key}")
                        continue  # 跳过触发
                    # 更新状态的最后触发时间
                    self.last_triggered_time[state_key] = current_time
                    triggered_states.append(state_key)
                continue

            # 多点规则处理
            if conditions:
                # 初始化缓存
                if state_key not in self.partial_conditions:
                    self.partial_conditions[state_key] = {
                        "points": set(),
                        "timestamp": current_time
                    }

                # 检查当前检测点是否满足某个条件
                for condition_rule in conditions:
                    if (
                        row["point_name"] == condition_rule["point_name"]
                        and condition_rule["condition"](row["distance"], row["threshold_value"])
                    ):
                        self.partial_conditions[state_key]["points"].add(condition_rule["point_name"])

                # 判断是否所有条件都满足
                if len(self.partial_conditions[state_key]["points"]) == len(conditions):
                    # 检查前置条件
                    if pre_condition and pre_condition not in self.completed_states:
                        print(f"[WARNING] 前置条件 {pre_condition} 未满足，跳过状态 {state_key}")
                        continue  # 跳过触发

                    # 前置条件满足，正常触发状态
                    self.last_triggered_time[state_key] = current_time
                    triggered_states.append(state_key)
                    del self.partial_conditions[state_key]  # 清除缓存

        return triggered_states
    
# 定义有限状态机
class FSM:
    def __init__(self):
        self.states = {
            "S0": State("S0", "初始状态"),
            "S1": State("S1", "检查灭火器"),
            "S2": State("S2", "排除隐患"),
            "S3": State("S3", "检查焊机"),
            "S4": State("S4", "检查焊枪、接地夹"),
            "S5": State("S5", "打开墙壁电源"),
            "S6": State("S6", "打开焊机电源"),
            "S7": State("S7", "调节焊机电压"),
            "S8": State("S8", "接地夹接地"),
            "S9": State("S9", "清理焊道、防护作业、焊接作业"),
            "S10": State("S10", "关闭焊机电源"),
            "S11": State("S11", "关闭墙壁电源"),
            "S12": State("S12", "复位焊枪、接地夹"),
            "S13": State("S13", "清理焊线"),
            "S14": State("S14", "完成状态"),
            "S15": State("S15", "错误状态")
        }
        self.current_state = self.states["S0"]
        self.transition_log = []
        self.state_manager = StateManager()
        self.state_entry_times = {state: pd.Timestamp(0) for state in self.states}
    def transition_to(self, next_state_key, trigger_data=None):
    # 检查目标状态是否已经被触发过
        if next_state_key in self.state_manager.completed_states:
            print(f"[INFO] 状态 {next_state_key} 已被触发，跳过该状态")
            return  # 跳过已触发的状态

        if next_state_key in self.states:
            current_time = trigger_data.get("contact_time", pd.Timestamp(0)) if trigger_data else pd.Timestamp(0)

            # 获取当前状态的进入时间
            last_entry_time = self.state_entry_times.get(self.current_state.name, pd.Timestamp(0))
            # 判断是否满足最少停留1秒的要求
            if (current_time - last_entry_time).total_seconds() < 1:
                return  # 不满足条件，跳过转移

            # 执行状态转移
            log_entry = {
                "from_state": self.current_state.name,
                "to_state": next_state_key,
                "description": self.states[next_state_key].description
            }
            if trigger_data:
                log_entry.update(trigger_data)
            self.transition_log.append(log_entry)
            self.current_state = self.states[next_state_key]
            self.current_state.execute()

            # 更新状态进入时间和 completed_states
            self.state_entry_times[self.current_state.name] = current_time
            self.state_manager.completed_states.add(next_state_key)  # 真正完成转移后再标记为已完成

            # 检查是否有自动转移规则
            auto_transition_to = self.state_manager.state_triggers.get(next_state_key, {}).get("auto_transition_to")
            if auto_transition_to:
                self.transition_to(auto_transition_to, trigger_data={"auto_triggered": True})
        else:
            raise ValueError(f"无效状态: {next_state_key}")

    # def process_data(self, csv_file_path):
    # # 读取 CSV 文件
    #     df = pd.read_csv(csv_file_path)
    #     if not pd.api.types.is_numeric_dtype(df["contact_time"]):
    #         df["contact_time"] = pd.to_datetime(df["contact_time"]).astype(int) / 10**9  # 转换为秒级时间戳
    #     for _, row in df.iterrows():
    #         current_time = row["contact_time"]
    #         point_name = row["point_name"]

    #         # 检测点级别的去重：跳过1秒内重复的点
    #         last_point_time = self.state_manager.last_triggered_time_per_point.get(point_name, 0)
    #         # print(f"[DEBUG] Point: {point_name}, Last Time: {last_point_time}, Current Time: {current_time}")
    #         if current_time - last_point_time < 0.1:
    #             # print(f"[SKIP] Skipping duplicate point: {point_name}")
    #             continue  # 如果距离上次触发不足1秒，跳过此检测点
    #         triggered_states = self.state_manager.check_and_trigger(row)
    #         for state_key in triggered_states:
    #             self.transition_to(state_key, trigger_data={
    #                 "contact_time": current_time,
    #                 "point_name": point_name,
    #                 "distance": row["distance"],
    #                 "threshold_value": row["threshold_value"]
    #             })
    #         self.state_manager.last_triggered_time_per_point[point_name] = current_time

    def process_data(self, csv_file_path):
        df = pd.read_csv(csv_file_path)

        if not pd.api.types.is_datetime64_any_dtype(df["contact_time"]):
            df["contact_time"] = pd.to_datetime(df["contact_time"])

        for _, row in df.iterrows():
            current_time = row["contact_time"]
            point_name = row["point_name"]

            # 检测点级别的去重
            last_point_time = self.state_manager.last_triggered_time_per_point.get(point_name, pd.Timestamp(0))
            if (current_time - last_point_time).total_seconds() < 20:
                continue

            # 传递当前状态名称
            triggered_states = self.state_manager.check_and_trigger(row, self.current_state.name)
            for state_key in triggered_states:
                self.transition_to(state_key, trigger_data={
                    "contact_time": current_time,
                    "point_name": point_name,
                    "distance": row["distance"],
                    "threshold_value": row["threshold_value"]
                })
            self.state_manager.last_triggered_time_per_point[point_name] = current_time

    def save_log_to_csv(self, file_path):
    # 将日志数据转换为 DataFrame
        df = pd.DataFrame(self.transition_log)

        # 确保 contact_time 列存在且为 datetime 类型
        if "contact_time" in df.columns:
            df["contact_time"] = pd.to_datetime(df["contact_time"])  # 确保是 datetime 类型
            df["contact_time"] = df["contact_time"].dt.strftime("%Y-%m-%d %H:%M:%S.%f")  # 格式化为字符串

        # 保存到 CSV 文件
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"状态转移日志已保存至: {file_path}")

# 主程序入口
if __name__ == "__main__":
    fsm = FSM()
    input_file = r"D:\实验\1.21交职UWB报警实验\双手5，阈值0.3\\接触检测结果5.1.csv"
    output_file = r"D:\实验\1.21交职UWB报警实验\双手5，阈值0.3\\状态转移日志5.csv"

    # 加载数据并运行FSM
    fsm.process_data(input_file)

    # 保存状态转移日志
    fsm.save_log_to_csv(output_file)