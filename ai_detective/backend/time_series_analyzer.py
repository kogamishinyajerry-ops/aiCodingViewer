"""
时间序列分析引擎
Time Series Analyzer
用于分析案件中的时间信息和时间逻辑
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import re
from enum import Enum


class TimePrecision(Enum):
    """时间精度"""
    YEAR = "年"
    MONTH = "月"
    DAY = "日"
    HOUR = "时"
    MINUTE = "分"
    SECOND = "秒"


@dataclass
class Timestamp:
    """时间戳"""
    id: str
    text: str  # 原始文本
    datetime: Optional[datetime]  # 解析后的时间
    precision: TimePrecision  # 时间精度
    event: str  # 关联的事件
    confidence: float = 1.0  # 置信度
    is_estimate: bool = False  # 是否为估算


@dataclass
class TimeInterval:
    """时间间隔"""
    start: Timestamp
    end: Timestamp
    duration: Optional[timedelta] = None
    description: str = ""


@dataclass
class Conflict:
    """时间矛盾"""
    id: str
    type: str  # "order", "overlap", "duration", "precision"
    description: str
    timestamps: List[Timestamp]
    severity: str  # "critical", "high", "medium", "low"


@dataclass
class Timeline:
    """时间线"""
    id: str
    timestamps: List[Timestamp] = field(default_factory=list)
    intervals: List[TimeInterval] = field(default_factory=list)
    conflicts: List[Conflict] = field(default_factory=list)
    
    def add_timestamp(self, timestamp: Timestamp):
        """添加时间戳"""
        self.timestamps.append(timestamp)
        # 重新排序
        self.timestamps.sort(key=lambda t: t.datetime or datetime.max)
    
    def get_timestamps_before(self, dt: datetime) -> List[Timestamp]:
        """获取指定时间之前的时间戳"""
        return [t for t in self.timestamps if t.datetime and t.datetime < dt]
    
    def get_timestamps_after(self, dt: datetime) -> List[Timestamp]:
        """获取指定时间之后的时间戳"""
        return [t for t in self.timestamps if t.datetime and t.datetime > dt]
    
    def get_timestamps_between(self, start: datetime, end: datetime) -> List[Timestamp]:
        """获取指定时间范围内的时间戳"""
        return [t for t in self.timestamps 
                if t.datetime and start <= t.datetime <= end]


class TimeSeriesAnalyzer:
    """时间序列分析器"""
    
    def __init__(self):
        # 当前年份的基准
        self.current_year = datetime.now().year
        self.recent_date_reference = None  # 最近的时间参考点
    
    def extract_timestamps(self, text: str, event_context: str = "") -> List[Timestamp]:
        """
        从文本中提取时间戳
        
        Args:
            text: 包含时间信息的文本
            event_context: 事件上下文,用于帮助时间理解
        
        Returns:
            时间戳列表
        """
        timestamps = []
        fact_id = 1
        
        # 1. 精确时间格式: YYYY年MM月DD日
        patterns = [
            # 精确日期时间
            (r'(\d{4})年(\d{1,2})月(\d{1,2})日\s*(\d{1,2})[点时](\d{1,2})?分?', TimePrecision.MINUTE),
            (r'(\d{4})年(\d{1,2})月(\d{1,2})日\s*(\d{1,2}):(\d{2})', TimePrecision.MINUTE),
            (r'(\d{4})年(\d{1,2})月(\d{1,2})日', TimePrecision.DAY),
            
            # 月日 (无年份)
            (r'(\d{1,2})月(\d{1,2})日\s*(\d{1,2})[点时](\d{1,2})?分?', TimePrecision.MINUTE),
            (r'(\d{1,2})月(\d{1,2})日\s*(\d{1,2}):(\d{2})', TimePrecision.MINUTE),
            (r'(\d{1,2})月(\d{1,2})日', TimePrecision.DAY),
            
            # 相对时间
            (r'(今天|今日)', TimePrecision.DAY),
            (r'(昨天|昨日)', TimePrecision.DAY),
            (r'(前天)', TimePrecision.DAY),
            (r'(大前天)', TimePrecision.DAY),
            (r'(\d+)天前', TimePrecision.DAY),
            (r'(\d+)小时前', TimePrecision.HOUR),
            (r'(\d+)分钟前', TimePrecision.MINUTE),
            (r'上周', TimePrecision.WEEK if hasattr(TimePrecision, 'WEEK') else TimePrecision.DAY),
            (r'上周(\d)', TimePrecision.DAY),
            (r'上个月|上上月', TimePrecision.MONTH),
            (r'(今年|去年|前年)', TimePrecision.YEAR),
            
            # 口语时间
            (r'早上(\d{1,2})[点时](\d{1,2})?分?', TimePrecision.MINUTE),
            (r'下午(\d{1,2})[点时](\d{1,2})?分?', TimePrecision.MINUTE),
            (r'晚上(\d{1,2})[点时](\d{1,2})?分?', TimePrecision.MINUTE),
            (r'中午(\d{1,2})[点时](\d{1,2})?分?', TimePrecision.MINUTE),
            (r'(\d{1,2})点(\d{1,2})?分', TimePrecision.MINUTE),
            (r'(\d{1,2})点([半])', TimePrecision.MINUTE),
        ]
        
        # 使用相对参考时间
        reference_date = self._determine_reference_date(text, event_context)
        
        for pattern, precision in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                matched_text = match.group(0)
                
                # 解析时间
                dt = self._parse_datetime(matched_text, reference_date, precision)
                
                # 创建时间戳
                timestamp = Timestamp(
                    id=f"timestamp_{fact_id}",
                    text=matched_text,
                    datetime=dt,
                    precision=precision,
                    event=self._extract_event_context(matched_text, text),
                    confidence=0.9 if dt else 0.7,
                    is_estimate=(not dt)
                )
                timestamps.append(timestamp)
                fact_id += 1
        
        # 去重
        timestamps = self._deduplicate_timestamps(timestamps)
        
        return timestamps
    
    def _determine_reference_date(self, text: str, event_context: str) -> datetime:
        """确定参考时间"""
        # 检查文本中是否有明确的参考时间
        date_patterns = [
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'(\d{4})-(\d{1,2})-(\d{1,2})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                year, month, day = map(int, match.groups())
                return datetime(year, month, day)
        
        # 如果没有,使用当前时间
        return datetime.now()
    
    def _parse_datetime(self, text: str, reference: datetime, 
                        precision: TimePrecision) -> Optional[datetime]:
        """解析日期时间"""
        try:
            # 精确格式: YYYY年MM月DD日
            if re.match(r'\d{4}年\d{1,2}月\d{1,2}日', text):
                parts = re.findall(r'\d+', text)
                if len(parts) >= 3:
                    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                    hour, minute = 0, 0
                    if len(parts) >= 5:
                        hour, minute = int(parts[3]), int(parts[4])
                    elif len(parts) == 4:
                        hour = int(parts[3])
                    return datetime(year, month, day, hour, minute)
            
            # 月日格式
            elif re.match(r'\d{1,2}月\d{1,2}日', text):
                parts = re.findall(r'\d+', text)
                if len(parts) >= 2:
                    month, day = int(parts[0]), int(parts[1])
                    year = reference.year
                    hour, minute = 0, 0
                    if len(parts) >= 4:
                        hour, minute = int(parts[2]), int(parts[3])
                    elif len(parts) == 3:
                        hour = int(parts[2])
                    return datetime(year, month, day, hour, minute)
            
            # 相对时间: 今天/昨天/前天
            elif '今天' in text or '今日' in text:
                return reference.replace(hour=0, minute=0, second=0, microsecond=0)
            elif '昨天' in text or '昨日' in text:
                return (reference - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            elif '前天' in text:
                return (reference - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
            elif '大前天' in text:
                return (reference - timedelta(days=3)).replace(hour=0, minute=0, second=0, microsecond=0)
            
            # N天前/N小时前
            elif re.match(r'\d+天前', text):
                days = int(re.findall(r'\d+', text)[0])
                return reference - timedelta(days=days)
            elif re.match(r'\d+小时前', text):
                hours = int(re.findall(r'\d+', text)[0])
                return reference - timedelta(hours=hours)
            elif re.match(r'\d+分钟前', text):
                minutes = int(re.findall(r'\d+', text)[0])
                return reference - timedelta(minutes=minutes)
            
            # 口语时间
            elif re.match(r'[早中晚]上?\d+[点时]', text):
                # 提取数字
                hour = int(re.findall(r'\d+', text)[0])
                
                # 判断上午/下午/晚上
                if '下午' in text or '晚上' in text:
                    if hour != 12:
                        hour += 12
                elif '中午' in text:
                    hour = 12
                
                # 提取分钟
                minute = 0
                minute_match = re.search(r'(\d+)分', text)
                if minute_match:
                    minute = int(minute_match.group(1))
                elif '半' in text:
                    minute = 30
                
                return reference.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            elif re.match(r'\d+点\d?分?', text):
                hour = int(re.findall(r'\d+', text)[0])
                minute = 0
                minute_match = re.search(r'(\d+)分', text)
                if minute_match:
                    minute = int(minute_match.group(1))
                elif '半' in text:
                    minute = 30
                
                # 默认为下午
                if hour < 12:
                    hour += 12
                
                return reference.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
        except Exception as e:
            return None
        
        return None
    
    def _extract_event_context(self, time_text: str, full_text: str) -> str:
        """提取时间对应的事件上下文"""
        # 找到时间在文本中的位置
        idx = full_text.find(time_text)
        if idx == -1:
            return ""
        
        # 提取前后各50个字
        start = max(0, idx - 50)
        end = min(len(full_text), idx + len(time_text) + 50)
        context = full_text[start:end].strip()
        
        # 移除时间部分
        context = context.replace(time_text, "").strip()
        
        return context
    
    def _deduplicate_timestamps(self, timestamps: List[Timestamp]) -> List[Timestamp]:
        """去重时间戳"""
        # 按时间戳文本分组
        groups = {}
        for ts in timestamps:
            key = ts.text
            if key not in groups:
                groups[key] = []
            groups[key].append(ts)
        
        # 每组保留置信度最高的
        deduplicated = []
        for key, group in groups.items():
            best = max(group, key=lambda x: x.confidence)
            deduplicated.append(best)
        
        return deduplicated
    
    def build_timeline(self, timestamps: List[Timestamp], 
                      event_context: str = "") -> Timeline:
        """
        构建时间线
        
        Args:
            timestamps: 时间戳列表
            event_context: 事件上下文
        
        Returns:
            时间线对象
        """
        timeline = Timeline(id="timeline_1")
        
        # 过滤掉无效时间戳
        valid_timestamps = [t for t in timestamps if t.datetime]
        
        # 按时间排序
        valid_timestamps.sort(key=lambda t: t.datetime)
        
        # 添加到时间线
        for ts in valid_timestamps:
            timeline.add_timestamp(ts)
        
        # 计算时间间隔
        for i in range(len(timeline.timestamps) - 1):
            if timeline.timestamps[i].datetime and timeline.timestamps[i + 1].datetime:
                duration = timeline.timestamps[i + 1].datetime - timeline.timestamps[i].datetime
                interval = TimeInterval(
                    start=timeline.timestamps[i],
                    end=timeline.timestamps[i + 1],
                    duration=duration,
                    description=f"{timeline.timestamps[i].event} → {timeline.timestamps[i + 1].event}"
                )
                timeline.intervals.append(interval)
        
        return timeline
    
    def detect_time_conflicts(self, timeline: Timeline) -> List[Conflict]:
        """
        检测时间矛盾
        
        Args:
            timeline: 时间线对象
        
        Returns:
            矛盾列表
        """
        conflicts = []
        conflict_id = 1
        
        timestamps = timeline.timestamps
        
        # 1. 检测顺序矛盾 (后发生的事件时间早于先发生的事件)
        for i in range(len(timestamps)):
            for j in range(i + 1, len(timestamps)):
                ts1 = timestamps[i]
                ts2 = timestamps[j]
                
                if ts1.datetime and ts2.datetime:
                    # 检查是否有逻辑顺序矛盾
                    if self._has_logical_order_conflict(ts1, ts2):
                        conflicts.append(Conflict(
                            id=f"conflict_{conflict_id}",
                            type="order",
                            description=f"时间顺序矛盾: {ts1.event} ({ts1.text}) 发生于 {ts1.datetime}, 但应在 {ts2.event} ({ts2.text}) ({ts2.datetime}) 之后",
                            timestamps=[ts1, ts2],
                            severity="high"
                        ))
                        conflict_id += 1
        
        # 2. 检测持续时间不合理
        for interval in timeline.intervals:
            if interval.duration:
                # 如果间隔过长 (超过24小时) 但事件应该连续发生
                if interval.duration.total_seconds() > 24 * 3600:
                    if self._should_be_continuous(interval):
                        conflicts.append(Conflict(
                            id=f"conflict_{conflict_id}",
                            type="duration",
                            description=f"时间间隔异常: {interval.description} 间隔 {interval.duration}, 可能存在问题",
                            timestamps=[interval.start, interval.end],
                            severity="medium"
                        ))
                        conflict_id += 1
                
                # 如果间隔过短 (小于1分钟) 但事件之间需要时间
                if interval.duration.total_seconds() < 60:
                    if self._should_have_gap(interval):
                        conflicts.append(Conflict(
                            id=f"conflict_{conflict_id}",
                            type="duration",
                            description=f"时间间隔过短: {interval.description} 间隔仅 {interval.duration}, 可能不足以完成",
                            timestamps=[interval.start, interval.end],
                            severity="low"
                        ))
                        conflict_id += 1
        
        # 3. 检测精度矛盾
        precision_conflicts = self._detect_precision_conflicts(timestamps)
        for conflict in precision_conflicts:
            conflicts.append(Conflict(
                id=f"conflict_{conflict_id}",
                type="precision",
                description=conflict,
                timestamps=[],
                severity="low"
            ))
            conflict_id += 1
        
        timeline.conflicts = conflicts
        return conflicts
    
    def _has_logical_order_conflict(self, ts1: Timestamp, ts2: Timestamp) -> bool:
        """判断是否有逻辑顺序矛盾"""
        # 检查事件文本中是否有明确的先后关系
        # 例如: "支付后即刻" - 之后的动作应该紧接着支付
        
        # 简化版: 检查常见的时间关系词
        before_keywords = ["之前", "前", "先", "首先", "第一"]
        after_keywords = ["之后", "后", "后", "然后", "接着", "第二"]
        
        # 如果 ts1 的事件包含"之后/后",但 ts1 的时间早于 ts2
        for kw in after_keywords:
            if kw in ts1.event and ts1.datetime < ts2.datetime:
                return True
        
        return False
    
    def _should_be_continuous(self, interval: TimeInterval) -> bool:
        """判断事件是否应该连续"""
        # 简化版: 检查事件文本
        continuous_keywords = ["后", "立即", "马上", "随即", "接着"]
        
        event_text = interval.description.lower()
        return any(kw in event_text for kw in continuous_keywords)
    
    def _should_have_gap(self, interval: TimeInterval) -> bool:
        """判断事件之间是否应该有时间间隔"""
        # 简化版: 检查事件文本
        gap_keywords = ["后", "一段时间", "过了一会", "然后"]
        
        event_text = interval.description.lower()
        return any(kw in event_text for kw in gap_keywords)
    
    def _detect_precision_conflicts(self, timestamps: List[Timestamp]) -> List[str]:
        """检测精度矛盾"""
        conflicts = []
        
        # 检查是否有精度不一致
        precision_counts = {}
        for ts in timestamps:
            precision = ts.precision.value
            precision_counts[precision] = precision_counts.get(precision, 0) + 1
        
        # 如果既有精确时间又有模糊时间,可能存在矛盾
        if len(precision_counts) > 1:
            conflicts.append(f"时间精度不一致: {', '.join(f'{k}:{v}' for k, v in precision_counts.items())}")
        
        return conflicts
    
    def infer_hidden_timestamps(self, timeline: Timeline) -> List[Timestamp]:
        """
        推断隐藏的时间戳
        
        Args:
            timeline: 时间线对象
        
        Returns:
            推断出的时间戳列表
        """
        hidden_timestamps = []
        hidden_id = len(timeline.timestamps) + 1
        
        timestamps = timeline.timestamps
        
        # 1. 推断中间缺失的时间点
        for i in range(len(timestamps) - 1):
            ts1 = timestamps[i]
            ts2 = timestamps[i + 1]
            
            if ts1.datetime and ts2.datetime:
                duration = ts2.datetime - ts1.datetime
                
                # 如果间隔较长,推断中间可能有其他事件
                if duration.total_seconds() > 3600:  # 超过1小时
                    # 推断中间时刻
                    middle_time = ts1.datetime + duration / 2
                    hidden_ts = Timestamp(
                        id=f"inferred_{hidden_id}",
                        text=f"推断时间 (约{middle_time.strftime('%Y-%m-%d %H:%M')})",
                        datetime=middle_time,
                        precision=TimePrecision.HOUR,
                        event=f"推断: 在 {ts1.event} 和 {ts2.event} 之间",
                        confidence=0.5,
                        is_estimate=True
                    )
                    hidden_timestamps.append(hidden_ts)
                    hidden_id += 1
        
        # 2. 推断开始前的时间
        if timestamps and timestamps[0].datetime:
            # 推推断事件开始前的时间点
            start_time = timestamps[0].datetime - timedelta(hours=1)
            hidden_ts = Timestamp(
                id=f"inferred_{hidden_id}",
                text=f"推断时间 (约{start_time.strftime('%Y-%m-%d %H:%M')})",
                datetime=start_time,
                precision=TimePrecision.HOUR,
                event=f"推断: 在 {timestamps[0].event} 开始前",
                confidence=0.4,
                is_estimate=True
            )
            hidden_timestamps.append(hidden_ts)
        
        return hidden_timestamps
    
    def analyze_time_logic(self, timeline: Timeline) -> Dict[str, Any]:
        """
        分析时间逻辑
        
        Args:
            timeline: 时间线对象
        
        Returns:
            时间逻辑分析结果
        """
        analysis = {
            "timeline_summary": {
                "total_timestamps": len(timeline.timestamps),
                "time_range": self._get_time_range(timeline),
                "total_duration": self._calculate_total_duration(timeline),
            },
            "time_patterns": self._analyze_time_patterns(timeline),
            "time_gaps": self._analyze_time_gaps(timeline),
            "critical_timestamps": self._identify_critical_timestamps(timeline),
            "time_conflicts": timeline.conflicts,
            "logic_analysis": self._analyze_logic(timeline),
            "recommendations": self._generate_recommendations(timeline)
        }
        
        return analysis
    
    def _get_time_range(self, timeline: Timeline) -> str:
        """获取时间范围"""
        if not timeline.timestamps:
            return "无时间信息"
        
        valid_ts = [t for t in timeline.timestamps if t.datetime]
        if not valid_ts:
            return "无有效时间信息"
        
        start = min(valid_ts, key=lambda x: x.datetime).datetime
        end = max(valid_ts, key=lambda x: x.datetime).datetime
        
        return f"{start.strftime('%Y-%m-%d %H:%M')} → {end.strftime('%Y-%m-%d %H:%M')}"
    
    def _calculate_total_duration(self, timeline: Timeline) -> str:
        """计算总持续时间"""
        valid_ts = [t for t in timeline.timestamps if t.datetime]
        if len(valid_ts) < 2:
            return "无法计算"
        
        start = min(valid_ts, key=lambda x: x.datetime).datetime
        end = max(valid_ts, key=lambda x: x.datetime).datetime
        duration = end - start
        
        days = duration.days
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        
        if days > 0:
            return f"{days}天{hours}小时"
        elif hours > 0:
            return f"{hours}小时{minutes}分钟"
        else:
            return f"{minutes}分钟"
    
    def _analyze_time_patterns(self, timeline: Timeline) -> Dict[str, Any]:
        """分析时间模式"""
        patterns = {
            "time_distribution": [],
            "time_clustering": [],
            "time_intervals": []
        }
        
        # 分析时间分布
        if len(timeline.timestamps) >= 2:
            # 计算相邻时间间隔
            for interval in timeline.intervals:
                if interval.duration:
                    patterns["time_intervals"].append({
                        "start": interval.start.datetime.strftime('%H:%M') if interval.start.datetime else None,
                        "end": interval.end.datetime.strftime('%H:%M') if interval.end.datetime else None,
                        "duration_minutes": interval.duration.total_seconds() / 60,
                        "description": interval.description
                    })
        
        return patterns
    
    def _analyze_time_gaps(self, timeline: Timeline) -> List[Dict[str, Any]]:
        """分析时间空白"""
        gaps = []
        
        if len(timeline.timestamps) < 2:
            return gaps
        
        # 查找较大的时间间隔
        for interval in timeline.intervals:
            if interval.duration and interval.duration.total_seconds() > 3600:  # 超过1小时
                gaps.append({
                    "start": interval.start.datetime.strftime('%Y-%m-%d %H:%M') if interval.start.datetime else None,
                    "end": interval.end.datetime.strftime('%Y-%m-%d %H:%M') if interval.end.datetime else None,
                    "duration_hours": interval.duration.total_seconds() / 3600,
                    "description": interval.description,
                    "note": "此时间段较长,可能有其他事件未记录"
                })
        
        return gaps
    
    def _identify_critical_timestamps(self, timeline: Timeline) -> List[Dict[str, Any]]:
        """识别关键时间点"""
        critical_ts = []
        
        for ts in timeline.timestamps:
            # 根据事件文本判断是否关键
            is_critical = False
            reason = ""
            
            if any(kw in ts.event for kw in ["报警", "投诉", "发布", "支付", "退款", "冲突", "争执"]):
                is_critical = True
                reason = "涉及关键事件"
            
            if is_critical:
                critical_ts.append({
                    "time": ts.datetime.strftime('%Y-%m-%d %H:%M') if ts.datetime else ts.text,
                    "event": ts.event,
                    "precision": ts.precision.value,
                    "reason": reason,
                    "original_text": ts.text
                })
        
        return critical_ts
    
    def _analyze_logic(self, timeline: Timeline) -> Dict[str, Any]:
        """分析时间逻辑"""
        logic = {
            "logic_valid": True,
            "logic_issues": [],
            "time_sequence": "正常"
        }
        
        # 检查时间冲突
        if timeline.conflicts:
            logic["logic_valid"] = False
            logic["logic_issues"] = [c.description for c in timeline.conflicts if c.severity in ["critical", "high"]]
        
        # 判断时间序列
        if timeline.conflicts:
            high_severity_conflicts = [c for c in timeline.conflicts if c.severity in ["critical", "high"]]
            if high_severity_conflicts:
                logic["time_sequence"] = "存在矛盾"
        
        return logic
    
    def _generate_recommendations(self, timeline: Timeline) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 检查时间精度
        low_precision_count = sum(1 for ts in timeline.timestamps 
                                 if ts.precision in [TimePrecision.YEAR, TimePrecision.MONTH])
        if low_precision_count > 0:
            recommendations.append(
                f"⚠️ 有 {low_precision_count} 个时间点精度较低(年/月级),建议补充更精确的时间"
            )
        
        # 检查时间冲突
        high_conflicts = [c for c in timeline.conflicts if c.severity in ["critical", "high"]]
        if high_conflicts:
            recommendations.append(
                f"⚠️ 发现 {len(high_conflicts)} 个高严重性的时间冲突,需要核实"
            )
        
        # 检查时间空白
        if len(timeline.intervals) > 0:
            long_gaps = [i for i in timeline.intervals 
                        if i.duration and i.duration.total_seconds() > 3600]
            if long_gaps:
                recommendations.append(
                    f"ℹ️ 有 {len(long_gaps)} 个较长的时间间隔,确认是否有遗漏的事件"
                )
        
        if not recommendations:
            recommendations.append("✅ 时间线逻辑清晰,无明显问题")
        
        return recommendations


# 便捷函数
def analyze_time_series(text: str, event_context: str = "") -> Dict[str, Any]:
    """
    便捷函数: 分析文本中的时间序列
    
    Args:
        text: 包含时间信息的文本
        event_context: 事件上下文
    
    Returns:
        完整的时间序列分析结果
    """
    analyzer = TimeSeriesAnalyzer()
    
    # 提取时间戳
    timestamps = analyzer.extract_timestamps(text, event_context)
    
    # 构建时间线
    timeline = analyzer.build_timeline(timestamps, event_context)
    
    # 检测矛盾
    analyzer.detect_time_conflicts(timeline)
    
    # 分析逻辑
    analysis = analyzer.analyze_time_logic(timeline)
    
    return analysis


if __name__ == "__main__":
    # 测试
    test_text = """
    今年12月15日下午3点左右,一个女生来到我的店铺。
    她在店里待了大约1个小时,大概4点左右支付了400余元。
    支付后她立刻要求退款,双方发生争执。
    晚上6点47分,她在小红书发布了一篇笔记。
    第二天,我收到了行政处罚。
    """
    
    result = analyze_time_series(test_text)
    print("时间序列分析结果:")
    print(f"时间范围: {result['timeline_summary']['time_range']}")
    print(f"总持续时间: {result['timeline_summary']['total_duration']}")
    print(f"关键时间点: {len(result['critical_timestamps'])}")
    print(f"时间冲突: {len(result['time_conflicts'])}")
    print(f"逻辑有效性: {result['logic_analysis']['logic_valid']}")
    print(f"\n建议:")
    for rec in result['recommendations']:
        print(f"  {rec}")
