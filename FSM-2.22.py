# import pandas as pd
# from datetime import datetime

# # 定义状态类
# class State:
#     def __init__(self, name, description):
#         self.name = name
#         self.description = description

#     def execute(self):
#         print(f" 当前状态: {self.name} - {self.description}")

# # 状态管理器
# class StateManager:
#     def __init__(self):
#         self.completed_states = set()  # 已完成的状态集合
#         self.last_triggered_time = {}  # 记录每个状态最后触发的时间戳
#         self.last_triggered_time_per_point = {}  # 记录每个检测点最后触发的时间戳
#         self.partial_conditions = {}  # 缓存部分满足的条件
#         self.state_triggers = {
#             "S1": {"point_name": "灭火器把手", "condition": lambda d, t: d < t},
#             "S2": {"point_name": "油箱顶部", "condition": lambda d, t: d < t},
#             "S3": {
#                 "logic": "AND",  # 和关系
#                 "conditions": [
#                     {"point_name": "焊机电源", "condition": lambda d, t: d < t},
#                     {"point_name": "电压电流旋钮", "condition": lambda d, t: d < t}
#                 ]
#             },
#             "S4": {
#                 "logic": "AND",  # 和关系
#                 "conditions": [
#                     {"point_name": "焊把钳下端", "condition": lambda d, t: d < t},
#                     {"point_name": "接地夹下端", "condition": lambda d, t: d < t}
#                 ],
#                 "pre_conditions": ["S3"]
#             },
#             "S5": {"point_name": "墙壁电源", "condition": lambda d, t: d < t,"pre_conditions": ["S4"]},
#             "S6": {"point_name": "焊机电源", "condition": lambda d, t: d < t,"pre_conditions": ["S4","S5"]},
#             "S7": {"point_name": "电压电流旋钮", "condition": lambda d, t: d < t,"pre_conditions":["S4"] },
#             "S8": {
#                 "logic": "AND",  # 和关系
#                 "conditions": [
#                     {"point_name": "焊把钳下端", "condition": lambda d, t: d < t},
#                     {"point_name": "接地夹下端", "condition": lambda d, t: d < t}
#                 ],
#                 "pre_conditions": ["S4","S7"]
#             },
#             "S9": {
#                 "logic": "AND",  # 和关系
#                 "conditions": [
#                     {"point_name": "待焊钢板", "condition": lambda d, t: d < t},
#                     {"point_name": "面罩把手", "condition": lambda d, t: d < t},
#                     # {"point_name": "钢刷", "condition": lambda d, t: d < t}
#                 ]
#             },
#             "S10": {"point_name": "焊机电源", "condition": lambda d, t: d < t,"pre_conditions": ["S9"]},
#             "S11": {"point_name": "墙壁电源", "condition": lambda d, t: d < t,"pre_conditions": ["S9"]},
#             "S12": {
#                 "logic": "AND",  # 和关系
#                 "conditions": [
#                     {"point_name": "焊把钳下端", "condition": lambda d, t: d < t},
#                     {"point_name": "接地夹下端", "condition": lambda d, t: d < t}
#                 ],
#                 "pre_conditions": ["S11","S4"]
#             },
#             "S13": {"point_name": "锤子", "condition": lambda d, t: d < t,"pre_conditions": ["S9","S10"]},  
#             # "S14": {"auto_transition_to": "S14" },  #自动转移到 S14终止状态
#         }
    
#     ##########判断是否满足多点规则，超出时间限制判断为不满足
#     def clear_expired_cache(self, current_time, timeout=30):
#         """
#         清除超过指定时间（timeout）的缓存
#         :param current_time: 当前时间戳
#         :param timeout: 超时时间（秒）
#         """
#         expired_states = []
#         for state_key, cache_info in self.partial_conditions.items():
#             timestamp = cache_info["timestamp"]
#             if (current_time - timestamp).total_seconds() >= timeout:
#                 expired_states.append(state_key)
        
#         # 清除超时缓存
#         for state_key in expired_states:
#             print(f"[INFO] Clearing expired cache for state {state_key}")
#             del self.partial_conditions[state_key]
#     def check_and_trigger(self, row, current_state_name):
#         triggered_states = []

#         # 使用文件中的时间戳
#         current_time = row["contact_time"]
#         point_name = row["point_name"]
#         self.clear_expired_cache(current_time, timeout=30)  # 清除超时缓存

#         for state_key, rule in self.state_triggers.items():
#             logic = rule.get("logic", "AND")
#             conditions = rule.get("conditions", [])
#             pre_conditions = rule.get("pre_conditions", [])  # 获取前置条件列表

#             # 单点规则处理
#             if "point_name" in rule:
#                 if (
#                     row["point_name"] == rule["point_name"]
#                     and rule["condition"](row["distance"], row["threshold_value"])
#                 ):
#                     # 检查前置条件是否满足
#                     if pre_conditions:
#                         # 检查所有前置条件是否都已完成
#                         unsatisfied = [pc for pc in pre_conditions if pc not in self.completed_states]
#                         if unsatisfied:
#                             print(f"[WARNING] 前置条件 {unsatisfied} 未满足，跳过状态 {state_key}")
#                             continue  # 跳过触发

#                     # 更新状态的最后触发时间
#                     self.last_triggered_time[state_key] = current_time
#                     triggered_states.append(state_key)
#                 continue

#             # 多点规则处理
#             if conditions:
#                 # 初始化缓存
#                 if state_key not in self.partial_conditions:
#                     self.partial_conditions[state_key] = {
#                         "points": set(),
#                         "timestamp": current_time
#                     }

#                 # 检查当前检测点是否满足某个条件
#                 for condition_rule in conditions:
#                     if (
#                         row["point_name"] == condition_rule["point_name"]
#                         and condition_rule["condition"](row["distance"], row["threshold_value"])
#                     ):
#                         self.partial_conditions[state_key]["points"].add(condition_rule["point_name"])

#                 # 判断是否所有条件都满足
#                 if len(self.partial_conditions[state_key]["points"]) == len(conditions):
#                     # 检查前置条件
#                     if pre_conditions:
#                         # 检查所有前置条件是否都已完成
#                         unsatisfied = [pc for pc in pre_conditions if pc not in self.completed_states]
#                         if unsatisfied:
#                             print(f"[WARNING] 前置条件 {unsatisfied} 未满足，跳过状态 {state_key}")
#                             continue  # 跳过触发

#                     # 前置条件满足，正常触发状态
#                     self.last_triggered_time[state_key] = current_time
#                     triggered_states.append(state_key)
#                     del self.partial_conditions[state_key]  # 清除缓存

#         return triggered_states
    
# # 定义有限状态机
# class FSM:
#     def __init__(self):
#         self.states = {
#             "S0": State("S0", "初始状态"),
#             "S1": State("S1", "检查灭火器"),
#             "S2": State("S2", "排除隐患"),
#             "S3": State("S3", "检查焊机"),
#             "S4": State("S4", "检查焊枪、接地夹"),
#             "S5": State("S5", "打开墙壁电源"),
#             "S6": State("S6", "打开焊机电源"),
#             "S7": State("S7", "调节焊机电压"),
#             "S8": State("S8", "接地夹接地"),
#             "S9": State("S9", "清理焊道、防护作业、焊接作业"),
#             "S10": State("S10", "关闭焊机电源"),
#             "S11": State("S11", "关闭墙壁电源"),
#             "S12": State("S12", "复位焊枪、接地夹"),
#             "S13": State("S13", "清理焊线"),
#             "S14": State("S14", "完成状态"),
#             "S15": State("S15", "错误状态")
#         }
#         self.current_state = self.states["S0"]
#         self.transition_log = []
#         self.state_manager = StateManager()
#         self.state_entry_times = {state: pd.Timestamp(0) for state in self.states}
#     def transition_to(self, next_state_key, trigger_data=None):
#     # 检查目标状态是否已经被触发过
#         if next_state_key in self.state_manager.completed_states:
#             print(f"[INFO] 状态 {next_state_key} 已被触发，跳过该状态")
#             return  # 跳过已触发的状态

#         if next_state_key in self.states:
#             current_time = trigger_data.get("contact_time", pd.Timestamp(0)) if trigger_data else pd.Timestamp(0)

#             # 获取当前状态的进入时间
#             last_entry_time = self.state_entry_times.get(self.current_state.name, pd.Timestamp(0))
#             # 判断是否满足最少停留1秒的要求
#             if (current_time - last_entry_time).total_seconds() < 1:
#                 return  # 不满足条件，跳过转移

#             # 执行状态转移
#             log_entry = {
#                 "from_state": self.current_state.name,
#                 "to_state": next_state_key,
#                 "description": self.states[next_state_key].description
#             }
#             if trigger_data:
#                 log_entry.update(trigger_data)
#             self.transition_log.append(log_entry)
#             self.current_state = self.states[next_state_key]
#             self.current_state.execute()

#             # 更新状态进入时间和 completed_states
#             self.state_entry_times[self.current_state.name] = current_time
#             self.state_manager.completed_states.add(next_state_key)  # 真正完成转移后再标记为已完成

#             # 检查是否有自动转移规则
#             auto_transition_to = self.state_manager.state_triggers.get(next_state_key, {}).get("auto_transition_to")
#             if auto_transition_to:
#                 self.transition_to(auto_transition_to, trigger_data={"auto_triggered": True})
#         else:
#             raise ValueError(f"无效状态: {next_state_key}")

#     def process_data(self, csv_file_path):
#         df = pd.read_csv(csv_file_path)

#         if not pd.api.types.is_datetime64_any_dtype(df["contact_time"]):
#             df["contact_time"] = pd.to_datetime(df["contact_time"])

#         for _, row in df.iterrows():
#             current_time = row["contact_time"]
#             point_name = row["point_name"]

#             # 检测点级别的去重
#             last_point_time = self.state_manager.last_triggered_time_per_point.get(point_name, pd.Timestamp(0))
#             if (current_time - last_point_time).total_seconds() < 20:
#                 continue

#             # 传递当前状态名称
#             triggered_states = self.state_manager.check_and_trigger(row, self.current_state.name)
#             for state_key in triggered_states:
#                 self.transition_to(state_key, trigger_data={
#                     "contact_time": current_time,
#                     "point_name": point_name,
#                     "distance": row["distance"],
#                     "threshold_value": row["threshold_value"]
#                 })
#             self.state_manager.last_triggered_time_per_point[point_name] = current_time

#     def save_log_to_csv(self, file_path):
#     # 将日志数据转换为 DataFrame
#         df = pd.DataFrame(self.transition_log)

#         # 确保 contact_time 列存在且为 datetime 类型
#         if "contact_time" in df.columns:
#             df["contact_time"] = pd.to_datetime(df["contact_time"])  # 确保是 datetime 类型
#             df["contact_time"] = df["contact_time"].dt.strftime("%Y-%m-%d %H:%M:%S.%f")  # 格式化为字符串

#         # 保存到 CSV 文件
#         df.to_csv(file_path, index=False, encoding='utf-8-sig')
#         print(f"状态转移日志已保存至: {file_path}")

# # 主程序入口
# if __name__ == "__main__":
#     fsm = FSM()
#     input_file = r"D:\QTproject\hr_rtls_pc-master\Logs\1.21交职UWB报警实验2.22\双手1，阈值0.5\\接触检测结果1.1.csv"
#     output_file = r"D:\QTproject\hr_rtls_pc-master\Logs\1.21交职UWB报警实验2.22\双手1，阈值0.5\\状态转移日志1.csv"

#     # 加载数据并运行FSM
#     fsm.process_data(input_file)

#     # 保存状态转移日志
#     fsm.save_log_to_csv(output_file)

import pandas as pd
from datetime import datetime
from enum import Enum

# ============== 超状态定义 ==============
class SuperState(Enum):
    INITIAL = "INITIAL"
    MOVING = "MOVING"
    OPERATION = "OPERATION"
    ERROR = "ERROR"
    END = "END"

# ============== 状态类 ==============
class State:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def execute(self):
        print(f" 当前状态：{self.name} - {self.description}")

# ============== 状态管理器 ==============
class StateManager:
    def __init__(self):
        self.completed_states = set()
        self.last_triggered_time = {}
        self.last_triggered_time_per_point = {}
        self.partial_conditions = {}
        self.state_triggers = {
            "S1": {"point_name": "灭火器把手", "condition": lambda d, t: d < t},
            "S2": {"point_name": "油箱顶部", "condition": lambda d, t: d < t},
            "S3": {
                "logic": "AND",
                "conditions": [
                    {"point_name": "焊机电源", "condition": lambda d, t: d < t},
                    {"point_name": "电压电流旋钮", "condition": lambda d, t: d < t}
                ]
            },
            "S4": {
                "logic": "AND",
                "conditions": [
                    {"point_name": "焊把钳下端", "condition": lambda d, t: d < t},
                    {"point_name": "接地夹下端", "condition": lambda d, t: d < t}
                ],
                "pre_conditions": ["S3"]
            },
            "S5": {"point_name": "墙壁电源", "condition": lambda d, t: d < t, "pre_conditions": ["S4"]},
            "S6": {"point_name": "焊机电源", "condition": lambda d, t: d < t, "pre_conditions": ["S4", "S5"]},
            "S7": {"point_name": "电压电流旋钮", "condition": lambda d, t: d < t, "pre_conditions": ["S4"]},
            "S8": {
                "logic": "AND",
                "conditions": [
                    {"point_name": "焊把钳下端", "condition": lambda d, t: d < t},
                    {"point_name": "接地夹下端", "condition": lambda d, t: d < t}
                ],
                "pre_conditions": ["S4", "S7"]
            },
            "S9": {
                "logic": "AND",
                "conditions": [
                    {"point_name": "待焊钢板", "condition": lambda d, t: d < t},
                    {"point_name": "面罩把手", "condition": lambda d, t: d < t}
                ]
            },
            "S10": {"point_name": "焊机电源", "condition": lambda d, t: d < t, "pre_conditions": ["S9"]},
            "S11": {"point_name": "墙壁电源", "condition": lambda d, t: d < t, "pre_conditions": ["S9"]},
            "S12": {
                "logic": "AND",
                "conditions": [
                    {"point_name": "焊把钳下端", "condition": lambda d, t: d < t},
                    {"point_name": "接地夹下端", "condition": lambda d, t: d < t}
                ],
                "pre_conditions": ["S11", "S4"]
            },
            "S13": {"point_name": "锤子", "condition": lambda d, t: d < t, "pre_conditions": ["S9", "S10"]},
        }
    
    def clear_expired_cache(self, current_time, timeout=30):
        expired_states = []
        for state_key, cache_info in self.partial_conditions.items():
            timestamp = cache_info["timestamp"]
            if (current_time - timestamp).total_seconds() >= timeout:
                expired_states.append(state_key)
        
        for state_key in expired_states:
            print(f"[INFO] Clearing expired cache for state {state_key}")
            del self.partial_conditions[state_key]
    
    def check_and_trigger(self, row, current_state_name, super_state):
        """
        增加 super_state 参数，仅在 OPERATION 状态下触发子状态
        """
        # 非操作状态下不触发子状态
        if super_state != SuperState.OPERATION:
            return []
        
        triggered_states = []
        current_time = row["contact_time"]
        point_name = row["point_name"]
        self.clear_expired_cache(current_time, timeout=30)

        for state_key, rule in self.state_triggers.items():
            logic = rule.get("logic", "AND")
            conditions = rule.get("conditions", [])
            pre_conditions = rule.get("pre_conditions", [])

            if "point_name" in rule:
                if (
                    row["point_name"] == rule["point_name"]
                    and rule["condition"](row["distance"], row["threshold_value"])
                ):
                    if pre_conditions:
                        unsatisfied = [pc for pc in pre_conditions if pc not in self.completed_states]
                        if unsatisfied:
                            print(f"[WARNING] 前置条件 {unsatisfied} 未满足，跳过状态 {state_key}")
                            continue

                    self.last_triggered_time[state_key] = current_time
                    triggered_states.append(state_key)
                continue

            if conditions:
                if state_key not in self.partial_conditions:
                    self.partial_conditions[state_key] = {
                        "points": set(),
                        "timestamp": current_time
                    }

                for condition_rule in conditions:
                    if (
                        row["point_name"] == condition_rule["point_name"]
                        and condition_rule["condition"](row["distance"], row["threshold_value"])
                    ):
                        self.partial_conditions[state_key]["points"].add(condition_rule["point_name"])

                if len(self.partial_conditions[state_key]["points"]) == len(conditions):
                    if pre_conditions:
                        unsatisfied = [pc for pc in pre_conditions if pc not in self.completed_states]
                        if unsatisfied:
                            print(f"[WARNING] 前置条件 {unsatisfied} 未满足，跳过状态 {state_key}")
                            continue

                    self.last_triggered_time[state_key] = current_time
                    triggered_states.append(state_key)
                    del self.partial_conditions[state_key]

        return triggered_states
    
    def reset(self):
        """复位状态管理器"""
        self.completed_states.clear()
        self.last_triggered_time.clear()
        self.partial_conditions.clear()

# ============== 有限状态机 ==============
class FSM:
    def __init__(self):
        # 子状态定义（S0-S15）
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
        
        # 超状态管理
        self.super_state = SuperState.INITIAL
        self.super_state_entry_time = pd.Timestamp(0)
        
        # 子状态管理
        self.current_state = self.states["S0"]
        self.state_entry_times = {state: pd.Timestamp(0) for state in self.states}
        
        # 日志记录
        self.transition_log = []
        self.state_manager = StateManager()
        
        # 超状态超时配置（秒）
        self.super_state_timeout = {
            SuperState.MOVING: 300,      # 移动状态最多 5 分钟
            SuperState.OPERATION: 600,   # 操作状态最多 10 分钟
        }
    
    def _log_transition(self, from_super, to_super, from_sub, to_sub, trigger_data=None):
        """记录状态转移日志"""
        log_entry = {
            "from_super_state": from_super.value if from_super else None,
            "to_super_state": to_super.value if to_super else None,
            "from_sub_state": from_sub.name if from_sub else None,
            "to_sub_state": to_sub.name if to_sub else None,
        }
        if trigger_data:
            log_entry.update(trigger_data)
        self.transition_log.append(log_entry)
    
    def _check_super_state_timeout(self, current_time):
        """检查超状态是否超时"""
        if self.super_state in self.super_state_timeout:
            timeout = self.super_state_timeout[self.super_state]
            if (current_time - self.super_state_entry_time).total_seconds() >= timeout:
                print(f"[WARNING] 超状态 {self.super_state.value} 超时，转入 ERROR 状态")
                return True
        return False
    
    def transition_super_state(self, next_super_state, trigger_data=None):
        """超状态转移"""
        if next_super_state == self.super_state:
            return
        
        current_time = trigger_data.get("contact_time", pd.Timestamp(0)) if trigger_data else pd.Timestamp(0)
        
        # 记录转移日志
        self._log_transition(
            from_super=self.super_state,
            to_super=next_super_state,
            from_sub=self.current_state,
            to_sub=self.current_state,
            trigger_data=trigger_data
        )
        
        print(f"[SUPER] 超状态转移：{self.super_state.value} -> {next_super_state.value}")
        
        # 更新超状态
        self.super_state = next_super_state
        self.super_state_entry_time = current_time
        
        # 超状态转移时的特殊处理
        if next_super_state == SuperState.INITIAL:
            self.reset()
        elif next_super_state == SuperState.ERROR:
            self.current_state = self.states["S15"]
            self.current_state.execute()
        elif next_super_state == SuperState.END:
            self.current_state = self.states["S14"]
            self.current_state.execute()
        elif next_super_state == SuperState.OPERATION:
            # 进入操作状态，从 S0 开始
            self.current_state = self.states["S0"]
            self.current_state.execute()
    
    def transition_to(self, next_state_key, trigger_data=None):
        """子状态转移（仅在 OPERATION 超状态下有效）"""
        # 检查是否在操作状态下
        if self.super_state != SuperState.OPERATION:
            print(f"[WARNING] 当前超状态为 {self.super_state.value}，无法进行子状态转移")
            return
        
        # 检查目标状态是否已经被触发过
        if next_state_key in self.state_manager.completed_states:
            print(f"[INFO] 状态 {next_state_key} 已被触发，跳过该状态")
            return

        if next_state_key in self.states:
            current_time = trigger_data.get("contact_time", pd.Timestamp(0)) if trigger_data else pd.Timestamp(0)

            # 获取当前状态的进入时间
            last_entry_time = self.state_entry_times.get(self.current_state.name, pd.Timestamp(0))
            # 判断是否满足最少停留 1 秒的要求
            if (current_time - last_entry_time).total_seconds() < 1:
                return

            # 记录转移日志
            self._log_transition(
                from_super=self.super_state,
                to_super=self.super_state,
                from_sub=self.current_state,
                to_sub=self.states[next_state_key],
                trigger_data=trigger_data
            )
            
            # 执行状态转移
            self.current_state = self.states[next_state_key]
            self.current_state.execute()

            # 更新状态进入时间和 completed_states
            self.state_entry_times[self.current_state.name] = current_time
            self.state_manager.completed_states.add(next_state_key)
        else:
            raise ValueError(f"无效状态：{next_state_key}")
    
    def reset(self):
        """复位整个状态机"""
        print("[INFO] 复位状态机")
        self.super_state = SuperState.INITIAL
        self.super_state_entry_time = pd.Timestamp(0)
        self.current_state = self.states["S0"]
        self.state_manager.reset()
        self.state_entry_times = {state: pd.Timestamp(0) for state in self.states}
    
    def process_data(self, csv_file_path):
        df = pd.read_csv(csv_file_path)

        if not pd.api.types.is_datetime64_any_dtype(df["contact_time"]):
            df["contact_time"] = pd.to_datetime(df["contact_time"])

        for _, row in df.iterrows():
            current_time = row["contact_time"]
            point_name = row["point_name"]

            # 检查超状态超时
            if self._check_super_state_timeout(current_time):
                self.transition_super_state(SuperState.ERROR, trigger_data={
                    "contact_time": current_time,
                    "reason": "super_state_timeout"
                })
                continue
            
            # 如果处于 ERROR 或 END 状态，跳过处理
            if self.super_state in [SuperState.ERROR, SuperState.END]:
                continue

            # 超状态流转逻辑
            if self.super_state == SuperState.INITIAL:
                # 检测到首个有效信号，转入 MOVING
                self.transition_super_state(SuperState.MOVING, trigger_data={
                    "contact_time": current_time,
                    "point_name": point_name
                })
            
            elif self.super_state == SuperState.MOVING:
                # 检测到任意有效接触信号，转入 OPERATION
                if row["distance"] < row["threshold_value"]:
                    print(f"[INFO] 检测到有效信号 {point_name}，转入 OPERATION 状态")
                    self.transition_super_state(SuperState.OPERATION, trigger_data={
                        "contact_time": current_time,
                        "point_name": point_name
                    })
            
            # 检测点级别的去重
            last_point_time = self.state_manager.last_triggered_time_per_point.get(point_name, pd.Timestamp(0))
            if (current_time - last_point_time).total_seconds() < 20:
                continue
            
            # 子状态触发（仅在 OPERATION 状态下）
            triggered_states = self.state_manager.check_and_trigger(
                row, 
                self.current_state.name,
                self.super_state
            )
            
            for state_key in triggered_states:
                self.transition_to(state_key, trigger_data={
                    "contact_time": current_time,
                    "point_name": point_name,
                    "distance": row["distance"],
                    "threshold_value": row["threshold_value"]
                })
            
            self.state_manager.last_triggered_time_per_point[point_name] = current_time
            # 在 process_data 方法末尾添加
        self._check_state()

    # 新增方法（放在 process_data 方法之后）
    def _check_state(self):
        if self.super_state in [SuperState.ERROR, SuperState.END]:
            return
        
        if self.super_state == SuperState.OPERATION:
            # 定义需要完成的所有子状态（S1-S13）
            required_states = [f"S{i}" for i in range(1, 14)]
            
            # 检查哪些状态未完成
            completed = self.state_manager.completed_states
            missing_states = [s for s in required_states if s not in completed]
            
            if missing_states:
                # 流程未完成，输出缺少的步骤并记录
                print(f"[WARNING] 流程未完成，缺少以下步骤：{missing_states}")
                self.transition_log.append({
                    "from_super_state": self.super_state.value,
                    "to_super_state": SuperState.ERROR.value,
                    "from_sub_state": self.current_state.name,
                    "to_sub_state": "S15",
                    "reason": "incomplete_workflow",
                    "missing_states": missing_states,
                    "completed_states": list(completed)
                })
                self.transition_super_state(SuperState.ERROR, trigger_data={
                    "reason": "incomplete_workflow",
                    "missing_states": missing_states,
                    "last_sub_state": self.current_state.name
                })
            else:
                # 所有步骤完成，转入 END 状态
                print(f"[INFO] 所有步骤 S1-S13 已完成，转入 END 状态")
                self.transition_super_state(SuperState.END, trigger_data={
                    "reason": "workflow_completed",
                    "completed_states": list(completed)
                })

    def save_log_to_csv(self, file_path):
        df = pd.DataFrame(self.transition_log)

        if "contact_time" in df.columns:
            df["contact_time"] = pd.to_datetime(df["contact_time"])
            df["contact_time"] = df["contact_time"].dt.strftime("%Y-%m-%d %H:%M:%S.%f")

        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"状态转移日志已保存至：{file_path}")
        

# ============== 主程序入口 ==============
if __name__ == "__main__":
    fsm = FSM()
    input_file = r"D:\QTproject\hr_rtls_pc-master\Logs\1.21交职UWB报警实验2.22\双手2，阈值0.5\\接触检测结果2.1 - 副本.csv"
    output_file = r"D:\QTproject\hr_rtls_pc-master\Logs\1.21交职UWB报警实验2.22\双手2，阈值0.5\\状态转移日志2.csv"

    fsm.process_data(input_file)
    fsm.save_log_to_csv(output_file)