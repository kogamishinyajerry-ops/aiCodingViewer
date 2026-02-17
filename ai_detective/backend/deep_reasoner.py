"""
深度推理引擎 - 整合版
Deep Reasoner - Integrated Version
整合时间序列分析、因果推理、矛盾检测等深度推理能力
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .time_series_analyzer import TimeSeriesAnalyzer, Timestamp, Timeline
from .causal_reasoner import CausalReasoner, CausalRelation, CausalChain
from .evidence import Evidence, EvidenceType


@dataclass
class DeepReasoningResult:
    """深度推理结果"""
    timestamp: datetime
    time_analysis: Dict[str, Any] = field(default_factory=dict)
    causal_analysis: Dict[str, Any] = field(default_factory=dict)
    conflict_analysis: Dict[str, Any] = field(default_factory=dict)
    logical_analysis: Dict[str, Any] = field(default_factory=dict)
    premeditation_analysis: Dict[str, Any] = field(default_factory=dict)
    evidence_chain: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    confidence: float = 0.0


class DeepReasoner:
    """深度推理引擎"""
    
    def __init__(self):
        self.time_analyzer = TimeSeriesAnalyzer()
        self.causal_reasoner = CausalReasoner()
    
    def reason(self, text: str, evidences: List[Evidence] = None,
               context: Dict[str, Any] = None) -> DeepReasoningResult:
        """
        执行深度推理
        
        Args:
            text: 案件描述文本
            evidences: 证据列表
            context: 上下文信息
        
        Returns:
            深度推理结果
        """
        if evidences is None:
            evidences = []
        if context is None:
            context = {}
        
        result = DeepReasoningResult(timestamp=datetime.now())
        
        # 1. 时间序列分析
        result.time_analysis = self._analyze_time_series(text)
        
        # 2. 因果关系分析
        result.causal_analysis = self._analyze_causality(text)
        
        # 3. 矛盾检测
        result.conflict_analysis = self._detect_conflicts(text, evidences)
        
        # 4. 逻辑分析
        result.logical_analysis = self._analyze_logic(text, evidences)
        
        # 5. 预谋性分析
        result.premeditation_analysis = self._analyze_premeditation(
            text, result.time_analysis, result.causal_analysis
        )
        
        # 6. 证据链分析
        result.evidence_chain = self._analyze_evidence_chain(evidences)
        
        # 7. 生成建议
        result.recommendations = self._generate_recommendations(result)
        
        # 8. 计算整体置信度
        result.confidence = self._calculate_confidence(result)
        
        return result
    
    def _analyze_time_series(self, text: str) -> Dict[str, Any]:
        """分析时间序列"""
        # 提取时间戳
        timestamps = self.time_analyzer.extract_timestamps(text)
        
        # 构建时间线
        timeline = self.time_analyzer.build_timeline(timestamps)
        
        # 检测时间冲突
        self.time_analyzer.detect_time_conflicts(timeline)
        
        # 分析时间逻辑
        analysis = self.time_analyzer.analyze_time_logic(timeline)
        
        return {
            "timestamps_count": len(timestamps),
            "timeline": analysis["timeline_summary"],
            "time_patterns": analysis["time_patterns"],
            "time_gaps": analysis["time_gaps"],
            "critical_timestamps": analysis["critical_timestamps"],
            "time_conflicts": [
                {
                    "type": c.type,
                    "description": c.description,
                    "severity": c.severity
                }
                for c in analysis["time_conflicts"]
            ],
            "logic_valid": analysis["logic_analysis"]["logic_valid"],
            "logic_issues": analysis["logic_analysis"]["logic_issues"]
        }
    
    def _analyze_causality(self, text: str) -> Dict[str, Any]:
        """分析因果关系"""
        analysis = self.causal_reasoner.analyze_causality(text)
        
        return {
            "relations_count": len(analysis.causal_relations),
            "chains_count": len(analysis.causal_chains),
            "gaps_count": len(analysis.causal_gaps),
            "root_cause": analysis.root_cause_analysis.get("root_cause", ""),
            "root_cause_confidence": analysis.root_cause_analysis.get("confidence", 0.0),
            "key_causes": analysis.key_causes,
            "key_effects": analysis.key_effects,
            "alternative_explanations": analysis.alternative_explanations
        }
    
    def _detect_conflicts(self, text: str, 
                        evidences: List[Evidence]) -> Dict[str, Any]:
        """检测矛盾"""
        conflicts = []
        
        # 1. 检测事实矛盾
        fact_conflicts = self._detect_fact_conflicts(text)
        conflicts.extend(fact_conflicts)
        
        # 2. 检测证据矛盾
        if evidences:
            evidence_conflicts = self._detect_evidence_conflicts(evidences)
            conflicts.extend(evidence_conflicts)
        
        # 3. 检测时间矛盾
        # (已在时间分析中完成,这里跳过)
        
        return {
            "total_conflicts": len(conflicts),
            "fact_conflicts": fact_conflicts,
            "evidence_conflicts": [
                c for c in conflicts if c.get("type") == "evidence"
            ]
        }
    
    def _detect_fact_conflicts(self, text: str) -> List[Dict[str, Any]]:
        """检测事实矛盾"""
        conflicts = []
        
        # 分句
        sentences = [s.strip() for s in text.split('。') if s.strip()]
        
        for i in range(len(sentences)):
            for j in range(i + 1, len(sentences)):
                sentence1 = sentences[i]
                sentence2 = sentences[j]
                
                # 检查是否有明显的矛盾
                if self._has_obvious_conflict(sentence1, sentence2):
                    conflicts.append({
                        "type": "fact",
                        "description": f"事实矛盾: '{sentence1}' 与 '{sentence2}' 可能存在矛盾",
                        "severity": "medium",
                        "sentences": [i, j]
                    })
        
        return conflicts
    
    def _detect_evidence_conflicts(self, evidences: List[Evidence]) -> List[Dict[str, Any]]:
        """检测证据矛盾"""
        conflicts = []
        
        # 检查证据描述之间的矛盾
        for i in range(len(evidences)):
            for j in range(i + 1, len(evidences)):
                ev1 = evidences[i]
                ev2 = evidences[j]
                
                if self._has_evidence_conflict(ev1, ev2):
                    conflicts.append({
                        "type": "evidence",
                        "description": f"证据矛盾: {ev1.name} 与 {ev2.name} 可能存在矛盾",
                        "severity": "high",
                        "evidences": [i, j]
                    })
        
        return conflicts
    
    def _has_obvious_conflict(self, sentence1: str, sentence2: str) -> bool:
        """判断是否有明显矛盾"""
        # 简化版: 检查矛盾词汇
        conflict_pairs = [
            ("是", "不是"),
            ("有", "没有"),
            ("同意", "不同意"),
            ("认可", "不认可"),
            ("支付", "未支付"),
            ("收到", "未收到")
        ]
        
        for kw1, kw2 in conflict_pairs:
            if kw1 in sentence1 and kw2 in sentence2:
                return True
            if kw2 in sentence1 and kw1 in sentence2:
                return True
        
        return False
    
    def _has_evidence_conflict(self, ev1: Evidence, ev2: Evidence) -> bool:
        """判断证据是否有矛盾"""
        # 简化版: 检查证据类型和描述
        # 如果两个证据描述了相反的事实,则存在矛盾
        
        # 这里仅做简化判断
        desc1 = ev1.description.lower()
        desc2 = ev2.description.lower()
        
        conflict_keywords = [
            ("是", "不是"),
            ("存在", "不存在"),
            ("真实", "虚假"),
            ("正确", "错误")
        ]
        
        for kw1, kw2 in conflict_keywords:
            if kw1 in desc1 and kw2 in desc2:
                return True
        
        return False
    
    def _analyze_logic(self, text: str, 
                      evidences: List[Evidence]) -> Dict[str, Any]:
        """分析逻辑"""
        logic = {
            "logic_valid": True,
            "logic_issues": [],
            "logical_consistency": 0.0,
            "logical_completeness": 0.0
        }
        
        # 1. 时间逻辑有效性
        if not self._check_time_logic_valid(text):
            logic["logic_valid"] = False
            logic["logic_issues"].append("时间逻辑存在问题")
        
        # 2. 因果逻辑有效性
        if not self._check_causal_logic_valid(text):
            logic["logic_valid"] = False
            logic["logic_issues"].append("因果逻辑存在问题")
        
        # 3. 计算逻辑一致性
        logic["logical_consistency"] = self._calculate_logical_consistency(text, evidences)
        
        # 4. 计算逻辑完整性
        logic["logical_completeness"] = self._calculate_logical_completeness(text)
        
        return logic
    
    def _check_time_logic_valid(self, text: str) -> bool:
        """检查时间逻辑有效性"""
        # 简化版: 使用时间序列分析
        analysis = self._analyze_time_series(text)
        return analysis.get("logic_valid", True)
    
    def _check_causal_logic_valid(self, text: str) -> bool:
        """检查因果逻辑有效性"""
        # 简化版: 检查是否有因果链缺口
        analysis = self._analyze_causality(text)
        return analysis.get("gaps_count", 0) == 0
    
    def _calculate_logical_consistency(self, text: str, 
                                       evidences: List[Evidence]) -> float:
        """计算逻辑一致性"""
        # 简化版: 基于矛盾数量
        conflicts = self._detect_conflicts(text, evidences)
        total_conflicts = conflicts["total_conflicts"]
        
        # 矛盾越少,一致性越高
        consistency = max(0.0, 1.0 - total_conflicts * 0.1)
        return consistency
    
    def _calculate_logical_completeness(self, text: str) -> float:
        """计算逻辑完整性"""
        # 简化版: 基于因果链完整度
        analysis = self._analyze_causality(text)
        
        if not analysis["chains_count"]:
            return 0.5
        
        # 简化版: 基于因果链数量和缺口数量
        completeness = min(1.0, analysis["chains_count"] * 0.3)
        if analysis["gaps_count"] > 0:
            completeness -= analysis["gaps_count"] * 0.1
        
        return max(0.0, completeness)
    
    def _analyze_premeditation(self, text: str, 
                             time_analysis: Dict[str, Any],
                             causal_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """分析预谋性"""
        premeditation = {
            "is_premeditated": False,
            "premeditation_score": 0.0,
            "indicators": [],
            "reasoning": ""
        }
        
        score = 0.0
        indicators = []
        
        # 1. 检查时间序列中的预谋迹象
        if time_analysis.get("timestamps_count", 0) > 0:
            # 检查是否有准备时间
            if any("之前" in ts.get("event", "") for ts in time_analysis.get("critical_timestamps", [])):
                score += 0.2
                indicators.append("存在准备时间")
        
        # 2. 检查因果链的完整性
        if causal_analysis.get("chains_count", 0) > 0:
            if causal_analysis.get("root_cause_confidence", 0.0) > 0.7:
                score += 0.2
                indicators.append("因果链清晰,有明确目标")
        
        # 3. 检查文本中的预谋关键词
        premeditation_keywords = ["准备", "计划", "安排", "设计", "预谋", "策划"]
        if any(kw in text for kw in premeditation_keywords):
            score += 0.3
            indicators.append("出现预谋性关键词")
        
        # 4. 检查行为的计划性
        planning_keywords = ["随即", "立刻", "立即", "马上", "紧接着"]
        if any(kw in text for kw in planning_keywords):
            score += 0.2
            indicators.append("行为连贯,显示出计划性")
        
        # 5. 检查是否冷静执行
        calm_keywords = ["冷静", "拍照", "录像", "取证", "报警"]
        if any(kw in text for kw in calm_keywords):
            score += 0.2
            indicators.append("冷静执行,显示出专业性")
        
        # 判断是否预谋
        premeditation["premeditation_score"] = min(1.0, score)
        premeditation["indicators"] = indicators
        premeditation["is_premeditated"] = score >= 0.5
        
        if score >= 0.7:
            premeditation["reasoning"] = f"高度预谋: 得分 {score:.2f}, 存在 {len(indicators)} 个预谋迹象"
        elif score >= 0.5:
            premeditation["reasoning"] = f"可能预谋: 得分 {score:.2f}, 存在 {len(indicators)} 个预谋迹象"
        elif score >= 0.3:
            premeditation["reasoning"] = f"不太像预谋: 得分 {score:.2f}, 仅存在 {len(indicators)} 个预谋迹象"
        else:
            premeditation["reasoning"] = f"不太可能是预谋: 得分 {score:.2f}"
        
        return premeditation
    
    def _analyze_evidence_chain(self, evidences: List[Evidence]) -> Dict[str, Any]:
        """分析证据链"""
        if not evidences:
            return {
                "completeness": 0.0,
                "consistency": 0.0,
                "strength": "weak",
                "gaps": ["缺少证据材料"],
                "suggestions": ["建议补充证据材料"]
            }
        
        # 计算完整度
        completeness = self._calculate_evidence_completeness(evidences)
        
        # 计算一致性
        consistency = self._calculate_evidence_consistency(evidences)
        
        # 确定强度
        if completeness >= 0.8 and consistency >= 0.8:
            strength = "strong"
        elif completeness >= 0.6 and consistency >= 0.6:
            strength = "moderate"
        else:
            strength = "weak"
        
        # 识别缺口
        gaps = self._identify_evidence_gaps(evidences)
        
        # 生成建议
        suggestions = self._generate_evidence_suggestions(evidences, gaps)
        
        return {
            "completeness": completeness,
            "consistency": consistency,
            "strength": strength,
            "gaps": gaps,
            "suggestions": suggestions
        }
    
    def _calculate_evidence_completeness(self, evidences: List[Evidence]) -> float:
        """计算证据完整度"""
        # 简化版: 基于证据类型数量
        type_counts = {}
        for ev in evidences:
            ev_type = ev.evidence_type.value
            type_counts[ev_type] = type_counts.get(ev_type, 0) + 1
        
        # 至少需要3种类型的证据
        required_types = 3
        present_types = len(type_counts)
        
        completeness = present_types / required_types
        return min(1.0, completeness)
    
    def _calculate_evidence_consistency(self, evidences: List[Evidence]) -> float:
        """计算证据一致性"""
        # 简化版: 基于证据权重
        if not evidences:
            return 0.0
        
        total_weight = sum(ev.weight for ev in evidences)
        avg_weight = total_weight / len(evidences)
        
        return avg_weight
    
    def _identify_evidence_gaps(self, evidences: List[Evidence]) -> List[str]:
        """识别证据缺口"""
        gaps = []
        
        # 检查证据类型
        present_types = set(ev.evidence_type for ev in evidences)
        
        required_types = [EvidenceType.DOCUMENT, EvidenceType.ELECTRONIC, EvidenceType.AUDIO_VIDEO]
        for req_type in required_types:
            if req_type not in present_types:
                type_name = {
                    EvidenceType.DOCUMENT: "书证",
                    EvidenceType.ELECTRONIC: "电子证据",
                    EvidenceType.AUDIO_VIDEO: "视听资料"
                }
                gaps.append(f"缺少{type_name[req_type]}")
        
        # 检查证据数量
        if len(evidences) < 3:
            gaps.append("证据数量不足")
        
        return gaps
    
    def _generate_evidence_suggestions(self, evidences: List[Evidence], 
                                       gaps: List[str]) -> List[str]:
        """生成证据建议"""
        suggestions = []
        
        if gaps:
            suggestions.append("建议补充以下证据:")
            for gap in gaps:
                suggestions.append(f"  • {gap}")
        else:
            suggestions.append("证据链较为完整")
        
        return suggestions
    
    def _generate_recommendations(self, result: DeepReasoningResult) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 1. 时间分析建议
        if result.time_analysis.get("logic_issues"):
            recommendations.append("⚠️ 时间逻辑存在问题,建议核实时间信息")
        
        # 2. 因果分析建议
        if result.causal_analysis.get("gaps_count", 0) > 0:
            recommendations.append(f"⚠️ 存在 {result.causal_analysis['gaps_count']} 个因果链缺口,建议补充中间环节")
        
        # 3. 矛盾检测建议
        if result.conflict_analysis.get("total_conflicts", 0) > 0:
            recommendations.append(f"⚠️ 发现 {result.conflict_analysis['total_conflicts']} 个矛盾,需要核实")
        
        # 4. 逻辑分析建议
        if not result.logical_analysis.get("logic_valid", True):
            recommendations.append("⚠️ 逻辑存在问题,需要重新梳理")
        
        # 5. 预谋性分析建议
        if result.premeditation_analysis.get("is_premeditated"):
            score = result.premeditation_analysis["premeditation_score"]
            if score >= 0.7:
                recommendations.append("⚠️ 高度预谋,建议深入调查对方背景")
        
        # 6. 证据链建议
        evidence_suggestions = result.evidence_chain.get("suggestions", [])
        recommendations.extend(evidence_suggestions)
        
        # 7. 总体建议
        if not recommendations:
            recommendations.append("✅ 深度推理未发现明显问题,逻辑清晰")
        else:
            recommendations.append("ℹ️ 建议基于以上发现进一步调查取证")
        
        return recommendations
    
    def _calculate_confidence(self, result: DeepReasoningResult) -> float:
        """计算整体置信度"""
        confidence = 0.0
        
        # 1. 时间分析置信度
        if result.time_analysis.get("logic_valid", True):
            confidence += 0.25
        else:
            confidence += 0.1
        
        # 2. 因果分析置信度
        confidence += 0.25 * result.causal_analysis.get("root_cause_confidence", 0.0)
        
        # 3. 逻辑一致性
        confidence += 0.25 * result.logical_analysis.get("logical_consistency", 0.0)
        
        # 4. 证据链强度
        evidence_strength = result.evidence_chain.get("strength", "weak")
        strength_weights = {"strong": 0.25, "moderate": 0.15, "weak": 0.05}
        confidence += strength_weights.get(evidence_strength, 0.05)
        
        return min(1.0, confidence)
    
    def generate_report(self, result: DeepReasoningResult) -> str:
        """生成推理报告"""
        lines = []
        
        lines.append("=" * 60)
        lines.append("深度推理分析报告")
        lines.append("=" * 60)
        
        # 时间分析
        lines.append("\n【时间序列分析】")
        time_summary = result.time_analysis.get("timeline", {})
        lines.append(f"  时间范围: {time_summary.get('time_range', '无')}")
        lines.append(f"  总持续时间: {time_summary.get('total_duration', '无')}")
        lines.append(f"  关键时间点: {len(result.time_analysis.get('critical_timestamps', []))} 个")
        lines.append(f"  时间冲突: {len(result.time_analysis.get('time_conflicts', []))} 个")
        lines.append(f"  逻辑有效性: {'✅' if result.time_analysis.get('logic_valid') else '❌'}")
        
        # 因果分析
        lines.append("\n【因果关系分析】")
        lines.append(f"  因果关系: {result.causal_analysis.get('relations_count', 0)} 个")
        lines.append(f"  因果链: {result.causal_analysis.get('chains_count', 0)} 条")
        lines.append(f"  因果缺口: {result.causal_analysis.get('gaps_count', 0)} 个")
        lines.append(f"  根本原因: {result.causal_analysis.get('root_cause', '无')}")
        
        # 矛盾检测
        lines.append("\n【矛盾检测】")
        lines.append(f"  总矛盾数: {result.conflict_analysis.get('total_conflicts', 0)} 个")
        fact_conflicts = result.conflict_analysis.get("fact_conflicts", [])
        if fact_conflicts:
            lines.append("  事实矛盾:")
            for conflict in fact_conflicts:
                lines.append(f"    • {conflict.get('description', '')}")
        
        # 逻辑分析
        lines.append("\n【逻辑分析】")
        lines.append(f"  逻辑有效性: {'✅' if result.logical_analysis.get('logic_valid') else '❌'}")
        lines.append(f"  逻辑一致性: {result.logical_analysis.get('logical_consistency', 0.0):.2f}")
        lines.append(f"  逻辑完整性: {result.logical_analysis.get('logical_completeness', 0.0):.2f}")
        
        # 预谋性分析
        lines.append("\n【预谋性分析】")
        premeditation = result.premeditation_analysis
        lines.append(f"  是否预谋: {'✅ 是' if premeditation.get('is_premeditated') else '❌ 否'}")
        lines.append(f"  预谋得分: {premeditation.get('premeditation_score', 0.0):.2f}")
        lines.append(f"  预谋迹象: {len(premeditation.get('indicators', []))} 个")
        for indicator in premeditation.get('indicators', []):
            lines.append(f"    • {indicator}")
        lines.append(f"  推理: {premeditation.get('reasoning', '')}")
        
        # 证据链分析
        lines.append("\n【证据链分析】")
        lines.append(f"  完整度: {result.evidence_chain.get('completeness', 0.0):.2f}")
        lines.append(f"  一致性: {result.evidence_chain.get('consistency', 0.0):.2f}")
        lines.append(f"  强度: {result.evidence_chain.get('strength', 'weak')}")
        
        # 建议
        lines.append("\n【建议】")
        for rec in result.recommendations:
            lines.append(f"  {rec}")
        
        # 整体置信度
        lines.append(f"\n【整体置信度】: {result.confidence:.2f}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)


# 便捷函数
def deep_reason(text: str, evidences: List[Evidence] = None,
               context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    便捷函数: 执行深度推理
    
    Args:
        text: 案件描述文本
        evidences: 证据列表
        context: 上下文信息
    
    Returns:
        深度推理结果字典
    """
    reasoner = DeepReasoner()
    result = reasoner.reason(text, evidences, context)
    
    # 生成报告
    report = reasoner.generate_report(result)
    
    return {
        "reasoning_result": result,
        "report": report
    }


if __name__ == "__main__":
    # 测试
    test_text = """
    今年12月15日下午3点左右,一个女生来到我的店铺。
    她在店里待了大约1个小时,大概4点左右支付了400余元。
    支付后她立刻要求退款,双方发生争执。
    对方现场报警并拍照取证。
    晚上6点47分,她在小红书发布了一篇笔记,称店铺诈骗。
    第二天,我收到了行政处罚。
    """
    
    result = deep_reason(test_text)
    print(result["report"])
