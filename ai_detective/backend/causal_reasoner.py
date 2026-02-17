"""
因果推理引擎
Causal Reasoner
用于分析案件中的因果关系
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re


class CausalType(Enum):
    """因果关系类型"""
    DIRECT = "直接因果"  # A 直接导致 B
    INDIRECT = "间接因果"  # A 通过中间环节导致 B
    NECESSARY = "必要条件"  # A 是 B 发生的必要条件
    SUFFICIENT = "充分条件"  # A 是 B 发生的充分条件
    CONTRIBUTORY = "促成因素"  # A 促成 B,但不是主要原因


class CausalStrength(Enum):
    """因果强度"""
    STRONG = "强"  # 因果关系明确且直接
    MODERATE = "中"  # 因果关系存在但不够直接
    WEAK = "弱"  # 因果关系较弱或可能存在


@dataclass
class CausalRelation:
    """因果关系"""
    id: str
    cause: str  # 原因
    effect: str  # 结果
    causal_type: CausalType  # 因果类型
    strength: CausalStrength  # 因果强度
    confidence: float  # 置信度 0-1
    evidence: List[str] = field(default_factory=list)  # 支持证据
    intermediate_factors: List[str] = field(default_factory=list)  # 中间因素
    description: str = ""  # 描述


@dataclass
class CausalChain:
    """因果链"""
    id: str
    relations: List[CausalRelation] = field(default_factory=list)
    root_cause: str = ""  # 根本原因
    final_effect: str = ""  # 最终结果
    completeness: float = 0.0  # 完整度 0-1
    gaps: List[str] = field(default_factory=list)  # 缺口
    
    def add_relation(self, relation: CausalRelation):
        """添加因果关系"""
        self.relations.append(relation)
        if not self.root_cause:
            self.root_cause = relation.cause
        self.final_effect = relation.effect
    
    def get_path(self) -> List[str]:
        """获取因果路径"""
        path = []
        for rel in self.relations:
            if rel.cause not in path:
                path.append(rel.cause)
            if rel.effect not in path:
                path.append(rel.effect)
        return path


@dataclass
class CausalGap:
    """因果缺口"""
    id: str
    from_event: str  # 从哪个事件
    to_event: str  # 到哪个事件
    gap_type: str  # "missing_cause", "missing_effect", "missing_intermediate"
    description: str  # 描述
    possible_causes: List[str] = field(default_factory=list)  # 可能的原因


@dataclass
class CausalAnalysis:
    """因果分析结果"""
    causal_relations: List[CausalRelation] = field(default_factory=list)
    causal_chains: List[CausalChain] = field(default_factory=list)
    causal_gaps: List[CausalGap] = field(default_factory=list)
    key_causes: List[str] = field(default_factory=list)  # 关键原因
    key_effects: List[str] = field(default_factory=list)  # 关键结果
    root_cause_analysis: Dict[str, Any] = field(default_factory=dict)  # 根本原因分析
    alternative_explanations: List[str] = field(default_factory=list)  # 替代解释


class CausalReasoner:
    """因果推理器"""
    
    def __init__(self):
        # 因果关系词汇库
        self.causal_keywords = {
            # 直接因果
            "direct": ["导致", "引起", "造成", "使", "使得", "致使", "让", "造成", "从而"],
            # 间接因果
            "indirect": ["因为", "由于", "基于", "考虑到", "鉴于"],
            # 结果
            "result": ["所以", "因此", "因而", "故而", "于是", "结果"],
            # 转折
            "contrast": ["但是", "然而", "可是", "不过"],
            # 条件
            "condition": ["如果", "若", "只要", "一旦"]
        }
        
        # 法律因果关系模式
        self.legal_causal_patterns = [
            # "因为...所以..."
            (r'因为(.{0,100}?)(所以|因此|因而|故而)', "direct"),
            # "由于...导致..."
            (r'由于(.{0,100}?)(导致|引起|造成)', "direct"),
            # "...造成..."
            (r'(.{0,30}?)(造成|引起|致使)(.{0,30}?)', "direct"),
            # "...所以..."
            (r'(.{0,100}?)(所以|因此|因而)(.{0,100}?)', "direct"),
            # "...进而..."
            (r'(.{0,100}?)(进而|从而)(.{0,100}?)', "indirect"),
        ]
    
    def extract_causal_relations(self, text: str) -> List[CausalRelation]:
        """
        从文本中提取因果关系
        
        Args:
            text: 文本内容
        
        Returns:
            因果关系列表
        """
        relations = []
        relation_id = 1
        
        # 1. 使用模式匹配提取显式因果关系
        for pattern, causal_type_str in self.legal_causal_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                if causal_type_str == "direct":
                    causal_type = CausalType.DIRECT
                else:
                    causal_type = CausalType.INDIRECT
                
                # 提取原因和结果
                groups = match.groups()
                if len(groups) >= 2:
                    cause = groups[0].strip()
                    effect = groups[1].strip()
                    
                    # 清理
                    cause = self._clean_cause_effect(cause)
                    effect = self._clean_cause_effect(effect)
                    
                    if len(cause) > 2 and len(effect) > 2:
                        relation = CausalRelation(
                            id=f"causal_{relation_id}",
                            cause=cause,
                            effect=effect,
                            causal_type=causal_type,
                            strength=CausalStrength.MODERATE,
                            confidence=0.85,
                            description=f"{cause} → {effect}"
                        )
                        relations.append(relation)
                        relation_id += 1
        
        # 2. 使用规则提取隐式因果关系
        implicit_relations = self._extract_implicit_relations(text)
        relations.extend(implicit_relations)
        
        # 去重
        relations = self._deduplicate_relations(relations)
        
        return relations
    
    def _clean_cause_effect(self, text: str) -> str:
        """清理原因/结果文本"""
        # 移除标点符号
        text = re.sub(r'[，。！？；：、,;:!?\n]', '', text)
        # 移除连接词
        text = re.sub(r'(因为|由于|所以|因此|因而|导致|引起|造成|使|使得|致使)', '', text)
        return text.strip()
    
    def _extract_implicit_relations(self, text: str) -> List[CausalRelation]:
        """提取隐式因果关系"""
        relations = []
        
        # 分句
        sentences = re.split(r'[。！？\n]', text)
        
        for i in range(len(sentences) - 1):
            sentence1 = sentences[i].strip()
            sentence2 = sentences[i + 1].strip()
            
            if len(sentence1) < 5 or len(sentence2) < 5:
                continue
            
            # 检查是否有因果关系
            if self._has_implicit_causality(sentence1, sentence2):
                relation = CausalRelation(
                    id=f"causal_implicit_{i}",
                    cause=sentence1,
                    effect=sentence2,
                    causal_type=CausalType.INDIRECT,
                    strength=CausalStrength.WEAK,
                    confidence=0.6,
                    description=f"隐式因果: {sentence1} → {sentence2}"
                )
                relations.append(relation)
        
        return relations
    
    def _has_implicit_causality(self, sentence1: str, sentence2: str) -> bool:
        """判断是否有隐式因果关系"""
        # 简化版: 检查时间顺序和语义关联
        time_keywords_1 = ["先", "开始", "首先", "最初"]
        time_keywords_2 = ["后", "接着", "然后", "随后", "最后"]
        
        has_1 = any(kw in sentence1 for kw in time_keywords_1)
        has_2 = any(kw in sentence2 for kw in time_keywords_2)
        
        return has_1 and has_2
    
    def _deduplicate_relations(self, relations: List[CausalRelation]) -> List[CausalRelation]:
        """去重因果关系"""
        unique_relations = []
        seen = set()
        
        for rel in relations:
            key = (rel.cause, rel.effect)
            if key not in seen:
                seen.add(key)
                unique_relations.append(rel)
        
        return unique_relations
    
    def build_causal_chain(self, relations: List[CausalRelation]) -> List[CausalChain]:
        """
        构建因果链
        
        Args:
            relations: 因果关系列表
        
        Returns:
            因果链列表
        """
        if not relations:
            return []
        
        # 构建因果关系图
        graph = self._build_causal_graph(relations)
        
        # 寻找因果链
        chains = []
        visited = set()
        
        for relation in relations:
            if relation.cause not in visited:
                chain = self._trace_chain(relation.cause, graph)
                if len(chain) > 1:
                    # 构建因果链对象
                    causal_chain = self._create_causal_chain(chain, relations)
                    chains.append(causal_chain)
                visited.update(chain)
        
        return chains
    
    def _build_causal_graph(self, relations: List[CausalRelation]) -> Dict[str, List[str]]:
        """构建因果关系图"""
        graph = {}
        
        for rel in relations:
            cause = rel.cause
            effect = rel.effect
            
            if cause not in graph:
                graph[cause] = []
            if effect not in graph:
                graph[effect] = []
            
            graph[cause].append(effect)
        
        return graph
    
    def _trace_chain(self, start: str, graph: Dict[str, List[str]], 
                     visited: Optional[Set[str]] = None) -> List[str]:
        """追踪因果链"""
        if visited is None:
            visited = set()
        
        if start in visited or start not in graph:
            return [start]
        
        visited.add(start)
        chain = [start]
        
        for next_node in graph[start]:
            if next_node not in visited:
                sub_chain = self._trace_chain(next_node, graph, visited)
                chain.extend(sub_chain)
        
        return chain
    
    def _create_causal_chain(self, nodes: List[str], 
                             relations: List[CausalRelation]) -> CausalChain:
        """创建因果链对象"""
        chain = CausalChain(id=f"chain_{nodes[0][:10]}")
        
        # 添加关系
        for i in range(len(nodes) - 1):
            cause = nodes[i]
            effect = nodes[i + 1]
            
            # 查找对应的关系
            for rel in relations:
                if rel.cause == cause and rel.effect == effect:
                    chain.add_relation(rel)
                    break
        
        # 计算完整度
        chain.completeness = self._calculate_chain_completeness(chain)
        
        # 识别缺口
        chain.gaps = self._identify_chain_gaps(chain)
        
        return chain
    
    def _calculate_chain_completeness(self, chain: CausalChain) -> float:
        """计算因果链完整度"""
        if not chain.relations:
            return 0.0
        
        # 简化版: 基于置信度
        avg_confidence = sum(rel.confidence for rel in chain.relations) / len(chain.relations)
        return avg_confidence
    
    def _identify_chain_gaps(self, chain: CausalChain) -> List[str]:
        """识别因果链缺口"""
        gaps = []
        
        # 检查是否有跳过中间环节
        for i in range(len(chain.relations) - 1):
            rel1 = chain.relations[i]
            rel2 = chain.relations[i + 1]
            
            # 如果两个关系之间没有明显的连接
            if rel1.effect != rel2.cause:
                gaps.append(
                    f"因果链断裂: {rel1.effect} → {rel2.cause} 之间缺少中间环节"
                )
        
        return gaps
    
    def detect_causal_gaps(self, chain: CausalChain) -> List[CausalGap]:
        """
        检测因果缺口
        
        Args:
            chain: 因果链对象
        
        Returns:
            因果缺口列表
        """
        gaps = []
        gap_id = 1
        
        # 1. 检查链中的缺口
        for gap_desc in chain.gaps:
            # 解析缺口描述
            if "→" in gap_desc:
                parts = gap_desc.split("→")
                from_event = parts[0].replace("因果链断裂: ", "").strip()
                to_event = parts[1].replace(" 之间缺少中间环节", "").strip()
                
                gap = CausalGap(
                    id=f"gap_{gap_id}",
                    from_event=from_event,
                    to_event=to_event,
                    gap_type="missing_intermediate",
                    description=gap_desc,
                    possible_causes=self._infer_missing_causes(from_event, to_event)
                )
                gaps.append(gap)
                gap_id += 1
        
        # 2. 检查是否缺少根本原因
        if not chain.relations:
            return gaps
        
        first_relation = chain.relations[0]
        if len(first_relation.cause) < 10:  # 原因描述太短,可能不完整
            gap = CausalGap(
                id=f"gap_{gap_id}",
                from_event="?",
                to_event=first_relation.cause,
                gap_type="missing_cause",
                description=f"缺少根本原因: {first_relation.cause} 之前可能有其他原因",
                possible_causes=self._infer_missing_causes("?", first_relation.cause)
            )
            gaps.append(gap)
        
        # 3. 检查是否缺少最终结果
        last_relation = chain.relations[-1]
        if len(last_relation.effect) < 10:  # 结果描述太短,可能不完整
            gap = CausalGap(
                id=f"gap_{gap_id}",
                from_event=last_relation.effect,
                to_event="?",
                gap_type="missing_effect",
                description=f"缺少最终结果: {last_relation.effect} 之后可能有其他结果",
                possible_causes=self._infer_missing_effects(last_relation.effect)
            )
            gaps.append(gap)
        
        return gaps
    
    def _infer_missing_causes(self, from_event: str, to_event: str) -> List[str]:
        """推断缺失的原因"""
        possible_causes = []
        
        # 简化版: 基于常见因果模式
        if "争执" in to_event or "冲突" in to_event:
            possible_causes.extend([
                "情绪激动",
                "言语冲突",
                "行为不当",
                "误解"
            ])
        
        if "投诉" in to_event:
            possible_causes.extend([
                "权益受损",
                "服务不满",
                "期望未满足",
                "纠纷未解决"
            ])
        
        return possible_causes
    
    def _infer_missing_effects(self, from_event: str) -> List[str]:
        """推断缺失的结果"""
        possible_effects = []
        
        # 简化版: 基于常见因果模式
        if "投诉" in from_event:
            possible_effects.extend([
                "行政介入",
                "媒体曝光",
                "舆论发酵",
                "声誉受损"
            ])
        
        if "冲突" in from_event:
            possible_effects.extend([
                "报警",
                "肢体冲突",
                "人身伤害",
                "财产损失"
            ])
        
        return possible_effects
    
    def infer_hidden_causes(self, chain: CausalChain) -> List[str]:
        """
        推断隐藏的原因
        
        Args:
            chain: 因果链对象
        
        Returns:
            推断出的隐藏原因列表
        """
        hidden_causes = []
        
        # 获取所有已知原因
        known_causes = set(rel.cause for rel in chain.relations)
        known_effects = set(rel.effect for rel in chain.relations)
        
        # 查找没有被作为结果的原因
        for cause in known_causes:
            if cause not in known_effects and cause != chain.root_cause:
                hidden_causes.append(f"隐藏原因: {cause}")
        
        return hidden_causes
    
    def evaluate_causal_strength(self, relation: CausalRelation) -> float:
        """
        评估因果强度
        
        Args:
            relation: 因果关系对象
        
        Returns:
            因果强度分数 0-1
        """
        score = 0.0
        
        # 1. 因果类型权重
        type_weights = {
            CausalType.DIRECT: 0.9,
            CausalType.INDIRECT: 0.6,
            CausalType.NECESSARY: 0.7,
            CausalType.SUFFICIENT: 0.85,
            CausalType.CONTRIBUTORY: 0.5
        }
        score += type_weights.get(relation.causal_type, 0.5)
        
        # 2. 因果强度权重
        strength_weights = {
            CausalStrength.STRONG: 0.3,
            CausalStrength.MODERATE: 0.2,
            CausalStrength.WEAK: 0.1
        }
        score += strength_weights.get(relation.strength, 0.1)
        
        # 3. 置信度
        score *= relation.confidence
        
        return min(score, 1.0)
    
    def analyze_causality(self, text: str) -> CausalAnalysis:
        """
        完整的因果分析
        
        Args:
            text: 文本内容
        
        Returns:
            因果分析结果
        """
        # 1. 提取因果关系
        relations = self.extract_causal_relations(text)
        
        # 2. 构建因果链
        chains = self.build_causal_chain(relations)
        
        # 3. 检测因果缺口
        gaps = []
        for chain in chains:
            chain_gaps = self.detect_causal_gaps(chain)
            gaps.extend(chain_gaps)
        
        # 4. 识别关键原因和结果
        key_causes = self._identify_key_causes(relations)
        key_effects = self._identify_key_effects(relations)
        
        # 5. 根本原因分析
        root_cause_analysis = self._analyze_root_cause(chains)
        
        # 6. 替代解释
        alternative_explanations = self._generate_alternative_explanations(text, relations)
        
        return CausalAnalysis(
            causal_relations=relations,
            causal_chains=chains,
            causal_gaps=gaps,
            key_causes=key_causes,
            key_effects=key_effects,
            root_cause_analysis=root_cause_analysis,
            alternative_explanations=alternative_explanations
        )
    
    def _identify_key_causes(self, relations: List[CausalRelation]) -> List[str]:
        """识别关键原因"""
        # 计算每个原因的出现次数
        cause_counts = {}
        for rel in relations:
            cause_counts[rel.cause] = cause_counts.get(rel.cause, 0) + 1
        
        # 按出现次数排序
        sorted_causes = sorted(cause_counts.items(), key=lambda x: x[1], reverse=True)
        
        # 返回前5个
        return [cause for cause, count in sorted_causes[:5]]
    
    def _identify_key_effects(self, relations: List[CausalRelation]) -> List[str]:
        """识别关键结果"""
        # 计算每个结果的出现次数
        effect_counts = {}
        for rel in relations:
            effect_counts[rel.effect] = effect_counts.get(rel.effect, 0) + 1
        
        # 按出现次数排序
        sorted_effects = sorted(effect_counts.items(), key=lambda x: x[1], reverse=True)
        
        # 返回前5个
        return [effect for effect, count in sorted_effects[:5]]
    
    def _analyze_root_cause(self, chains: List[CausalChain]) -> Dict[str, Any]:
        """分析根本原因"""
        if not chains:
            return {"root_cause": "无法确定", "confidence": 0.0}
        
        # 找出所有因果链的根本原因
        root_causes = [chain.root_cause for chain in chains if chain.root_cause]
        
        if not root_causes:
            return {"root_cause": "无法确定", "confidence": 0.0}
        
        # 如果只有一个,直接返回
        if len(root_causes) == 1:
            return {
                "root_cause": root_causes[0],
                "confidence": 0.9,
                "reason": "单一因果链,根本原因明确"
            }
        
        # 如果有多个,选择最可能的
        # 简化版: 选择最短的描述(通常更根本)
        root_cause = min(root_causes, key=lambda x: len(x))
        
        return {
            "root_cause": root_cause,
            "confidence": 0.7,
            "reason": "存在多条因果链,选择最可能的原因",
            "other_possibilities": root_causes
        }
    
    def _generate_alternative_explanations(self, text: str, 
                                         relations: List[CausalRelation]) -> List[str]:
        """生成替代解释"""
        alternatives = []
        
        # 基于常见法律场景
        if "投诉" in text:
            alternatives.append("替代解释: 投诉可能是出于维护自身合法权益,而非恶意")
        
        if "争执" in text or "冲突" in text:
            alternatives.append("替代解释: 争执可能是双方沟通不畅导致,而非单方面责任")
        
        if "网络" in text and "发布" in text:
            alternatives.append("替代解释: 网络发布可能是出于警示他人,而非诽谤")
        
        if len(relations) > 0:
            alternatives.append("替代解释: 原因和结果之间可能存在其他未被观察到的中间因素")
        
        return alternatives


# 便捷函数
def analyze_causality(text: str) -> Dict[str, Any]:
    """
    便捷函数: 分析文本中的因果关系
    
    Args:
        text: 文本内容
    
    Returns:
        完整的因果分析结果
    """
    reasoner = CausalReasoner()
    analysis = reasoner.analyze_causality(text)
    
    return {
        "causal_relations": [
            {
                "id": rel.id,
                "cause": rel.cause,
                "effect": rel.effect,
                "type": rel.causal_type.value,
                "strength": rel.strength.value,
                "confidence": rel.confidence
            }
            for rel in analysis.causal_relations
        ],
        "causal_chains": [
            {
                "id": chain.id,
                "root_cause": chain.root_cause,
                "final_effect": chain.final_effect,
                "completeness": chain.completeness,
                "path": chain.get_path()
            }
            for chain in analysis.causal_chains
        ],
        "causal_gaps": [
            {
                "id": gap.id,
                "from": gap.from_event,
                "to": gap.to_event,
                "type": gap.gap_type,
                "description": gap.description
            }
            for gap in analysis.causal_gaps
        ],
        "key_causes": analysis.key_causes,
        "key_effects": analysis.key_effects,
        "root_cause": analysis.root_cause_analysis.get("root_cause", ""),
        "root_cause_confidence": analysis.root_cause_analysis.get("confidence", 0.0),
        "alternative_explanations": analysis.alternative_explanations
    }


if __name__ == "__main__":
    # 测试
    test_text = """
    因为对方在店门口反复议价、长时间试用,导致店铺无法正常营业。
    随后对方支付了400余元,但由于再次要求赠品,双方发生争执。
    对方现场报警并拍照取证,然后在社交媒体发布诽谤内容,
    最终导致店铺停业并被行政处罚。
    """
    
    result = analyze_causality(test_text)
    print("因果分析结果:")
    print(f"因果关系数量: {len(result['causal_relations'])}")
    print(f"因果链数量: {len(result['causal_chains'])}")
    print(f"因果缺口数量: {len(result['causal_gaps'])}")
    print(f"根本原因: {result['root_cause']} (置信度: {result['root_cause_confidence']})")
    print(f"\n关键原因:")
    for cause in result['key_causes']:
        print(f"  - {cause}")
    print(f"\n关键结果:")
    for effect in result['key_effects']:
        print(f"  - {effect}")
    print(f"\n替代解释:")
    for alt in result['alternative_explanations']:
        print(f"  - {alt}")
