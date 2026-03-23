"""
EasyMED - Clinical Skills Evaluation Module

Evaluates a medical student's consultation performance against an expert
case template.  The evaluator uses an LLM to analyse six dimensions:

    1. 问诊技巧  – history-taking quality
    2. 体格检查  – physical examination completeness
    3. 辅助检查  – appropriate use of laboratory / imaging studies
    4. 诊断思维  – diagnostic reasoning
    5. 治疗方案  – treatment planning
    6. 整体表现  – overall performance

Usage:
    from evaluation import ClinicalEvaluator

    evaluator = ClinicalEvaluator()   # reads config from env vars

    result = evaluator.evaluate(session_data, case_template)
    for section, text in result.items():
        print(f"=== {section} ===")
        print(text)

Session data format
-------------------
session_data = {
    "sessionId": "...",
    "userId":    "...",
    "caseId":    "...",
    "history": [
        {"question": "...", "answer": "...", "intentClassification": "..."},
        ...
    ],
    "performedExams": [
        {"itemName": "...", "result": "...", "examType": "physical_exam|auxiliary_exam"},
        ...
    ],
    "userSubmissions": [
        {
            "data": {
                "mainDiagnoses": [{"diagnosisName": "..."}],
                "differentialDiagnoses": [{"disease": "...", "status": "support|exclude"}],
            }
        },
        ...
    ],
    "userTreatments": [
        {"data": {"treatmentPlan": "..."}},
        ...
    ],
}

Case template format
--------------------
case_template = {
    "caseId":    "...",
    "caseTitle": "...",
    "patientProfile": {
        "name": "...", "age_value": 30, "age_unit": "岁",
        "gender": "男", "chief_complaint": "...",
        "present_illness_history": "...",
        ...
    },
    "mustConsultionItems":    ["主要症状", "发作时间", ...],
    "optionalConsultionItems":["生活习惯", ...],
    "mustPhysicalExams":      ["体温", "血压", ...],
    "optionalPhysicalExams":  [...],
    "mustAuxiliaryLabs":      ["血常规", "胸部CT", ...],
    "optionalAuxiliaryLabs":  [...],
    "physicalExams":          {"体温": "36.5°C", ...},
    "auxiliaryLabs":          {"血常规": "...", ...},
    "diagnoses": {
        "mainDiagnosis": {"disease": "..."},
        "differentialDiagnoses": [{"disease": "..."}, ...]
    },
    "treatments": "1. 吸氧\n2. 抗感染治疗\n...",
}
"""

import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from openai import OpenAI


class ClinicalEvaluator:
    """
    Evaluates a medical student's clinical consultation against an expert case template.

    Returns a dict with keys:
        "consultation", "physical", "auxiliary", "diagnosis", "treatment", "overall"
    each containing a plain-text evaluation paragraph.

    API configuration (same env vars as VirtualPatient):
        EASYMED_API_KEY   – required
        EASYMED_BASE_URL  – optional
        EASYMED_MODEL     – optional, defaults to "gpt-4o"
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key  = api_key  or os.environ.get("EASYMED_API_KEY")
        self.base_url = base_url or os.environ.get("EASYMED_BASE_URL")
        self.model    = model    or os.environ.get("EASYMED_MODEL", "gpt-4o")

        if not self.api_key:
            raise ValueError(
                "API key is required. "
                "Set the EASYMED_API_KEY environment variable or pass api_key=."
            )

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def evaluate(
        self,
        session_data: Dict,
        case_template: Dict,
    ) -> Dict[str, str]:
        """
        Evaluate the student's performance for a single session.

        Args:
            session_data:   Dict describing what the student did.
            case_template:  Dict containing the expert standard answer.

        Returns:
            Dict with keys "consultation", "physical", "auxiliary",
            "diagnosis", "treatment", "overall", each mapping to a
            plain-text evaluation string.
        """
        session_summary = self._build_session_summary(session_data, case_template)
        expert_answer   = self._build_expert_answer(case_template)
        prompt          = self._build_evaluation_prompt(session_summary, expert_answer)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            raw_text = response.choices[0].message.content.strip()
            return self._parse_evaluation(raw_text)

        except Exception as exc:
            print(f"[ClinicalEvaluator] LLM call failed: {exc}")
            return self._default_evaluation()

    # ------------------------------------------------------------------
    # Session summary builder
    # ------------------------------------------------------------------

    def _build_session_summary(self, session: Dict, template: Dict) -> str:
        parts: List[str] = []
        patient = template.get("patientProfile", {})

        parts.append(
            f"【病例信息】\n"
            f"患者：{patient.get('name', '未知')}，"
            f"{patient.get('age_value', '')} {patient.get('age_unit', '岁')}，"
            f"{patient.get('gender', '未知')}\n"
            f"主诉：{patient.get('chief_complaint', '')}\n"
            f"现病史：{patient.get('present_illness_history', '')}\n"
        )

        # History-taking
        lines: List[str] = []
        for item in session.get("history", []):
            if item.get("question") and item.get("answer"):
                q_line = f"医生问：{item['question']}"
                if item.get("intentClassification"):
                    q_line += f"（意图：{item['intentClassification']}）"
                lines.append(q_line)
                lines.append(f"患者答：{item['answer']}")

        if lines:
            parts.append("【问诊过程】")
            parts.extend(lines[:40])
            if len(lines) > 40:
                parts.append("... (truncated)")

        # Physical / auxiliary exams
        physical: List[str] = []
        auxiliary: List[str] = []
        for exam in session.get("performedExams", []):
            if not exam.get("itemName"):
                continue
            line = f"{exam['itemName']}：{exam.get('result', '')}"
            if exam.get("examType") == "physical_exam":
                physical.append(line)
            else:
                auxiliary.append(line)

        if physical:
            parts.append("\n【体格检查】")
            parts.extend(physical)

        if auxiliary:
            parts.append("\n【辅助检查】")
            parts.extend(auxiliary)

        # Diagnosis
        submissions = session.get("userSubmissions", [])
        if submissions:
            sub_data = submissions[-1].get("data", {})
            parts.append("【学生诊断】")

            main_dx = sub_data.get("mainDiagnoses", [])
            if main_dx:
                parts.append("主要诊断：")
                for dx in main_dx:
                    parts.append(f"  - {dx.get('diagnosisName', '')}")

            diff_dx = sub_data.get("differentialDiagnoses", [])
            if diff_dx:
                parts.append("鉴别诊断：")
                for dx in diff_dx:
                    status = "支持" if dx.get("status") == "support" else "排除"
                    parts.append(f"  - {dx.get('disease', '')} ({status})")

        # Treatment
        treatments = session.get("userTreatments", [])
        if treatments:
            plan = treatments[-1].get("data", {}).get("treatmentPlan", "")
            if plan:
                parts.append("\n【治疗方案】")
                parts.append(f"治疗计划：{plan}")

        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Expert answer builder
    # ------------------------------------------------------------------

    def _build_expert_answer(self, template: Dict) -> str:
        lines: List[str] = []

        lines.append("【标准问诊要点】")
        must_consult = template.get("mustConsultionItems", [])
        lines.append("必须问诊项目：" + "、".join(must_consult))
        opt_consult  = template.get("optionalConsultionItems", [])
        if opt_consult:
            lines.append("可选问诊项目：" + "、".join(opt_consult))

        lines.append("\n【标准体格检查】")
        must_phys = template.get("mustPhysicalExams", [])
        lines.append("必须检查项目：" + "、".join(must_phys))
        opt_phys  = [i for i in template.get("optionalPhysicalExams", []) if i.strip()]
        if opt_phys:
            lines.append("可选检查项目：" + "、".join(opt_phys))
        phys_results = template.get("physicalExams", {})
        if phys_results:
            lines.append("标准检查结果：")
            for k, v in phys_results.items():
                lines.append(f"  - {k}：{v}")

        lines.append("\n【标准辅助检查】")
        must_aux = template.get("mustAuxiliaryLabs", [])
        lines.append("必须检查项目：" + "、".join(must_aux))
        opt_aux  = [i for i in template.get("optionalAuxiliaryLabs", []) if i.strip()]
        if opt_aux:
            lines.append("可选检查项目：" + "、".join(opt_aux))
        aux_results = template.get("auxiliaryLabs", {})
        if aux_results:
            lines.append("标准检查结果：")
            for k, v in aux_results.items():
                lines.append(f"  - {k}：{v}")

        lines.append("\n【标准诊断】")
        dx = template.get("diagnoses", {})
        main_dx = dx.get("mainDiagnosis", {})
        if isinstance(main_dx, list):
            lines.append("主要诊断：" + ", ".join(d.get("disease", "") for d in main_dx))
        else:
            lines.append(f"主要诊断：{main_dx.get('disease', '')}")

        diff_dxs = dx.get("differentialDiagnoses", [])
        if diff_dxs:
            lines.append("鉴别诊断：")
            for d in diff_dxs:
                lines.append(f"  - {d.get('disease', '')}")

        lines.append(f"\n【标准治疗方案】")
        lines.append(template.get("treatments", ""))

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Prompt / parse helpers
    # ------------------------------------------------------------------

    def _build_evaluation_prompt(self, session_summary: str, expert_answer: str) -> str:
        return f"""
你是一位资深的临床医学教育专家，现在需要对一名医学生的临床技能练习进行评估。

【重要评估原则】
1. 严格按照专家标准答案进行评估，不得添加任何标准答案之外的要求
2. 只对比学生表现与标准答案的差异，不要自己判断对错
3. 标准答案中列出的是必须要做的，没有列出的不作为扣分依据
4. 重点评估学生是否完成了标准答案中的要求
5. 不要对标准答案之外的内容进行评价
6. 不要提及标准答案不符等内容
7. 对比产生的结果需要条理展示，不要出现重复内容

【学生表现记录】
{session_summary}

【专家标准答案】
{expert_answer}

请严格按照标准答案对学生表现进行评估，重点分析以下几个方面：

1. **问诊技巧**：
   - 严格对比标准问诊要点，学生是否完成了所有必须问诊项目
   - 检查是否遗漏了重要的问诊意图类别
   - 遗漏项目：列出学生遗漏的问诊意图，并说明该问诊与诊断的相关性
   - 重点评价问诊的完整性、准确性

2. **体格检查**：
   - 严格对比标准体检项目，学生是否完成了所有必须检查项目
   - 完成项目：列出学生选取的必须检查项目和可选检查项目
   - 遗漏项目：列出学生未完成的必须体检项目，并说明该检查与诊断的相关性。若无遗漏，请注明。
   - 多余项目：列出学生做了专家标准答案之外的体检操作，评价是否符合当前诊断思路

3. **辅助检查**：
   - 严格对比标准辅助检查项目，学生是否完成了所有必须检查项目
   - 完成项目：列出学生选取的必须检查项目和可选检查项目
   - 遗漏项目：列出学生未完成的必须辅助检查项目，并说明该检查与诊断的相关性。若无遗漏，请注明。
   - 多余项目：列出学生做了专家标准答案之外的辅助检查操作，评价是否符合当前诊断思路

4. **诊断思维**：
   - 严格对比标准诊断，学生诊断是否与专家标准答案一致
   - 对比鉴别诊断的考虑是否符合标准答案
   - 评估学生选择的诊断依据是否充分、准确

5. **治疗方案**：
   - 分别列出学生的治疗方案和专家标准答案中该患者使用的治疗方案
   - 严格对比标准治疗方案，清晰指出差异点、遗漏点，并给出改进建议

6. **整体表现**：
   - 基于标准答案综合评价学生的整体表现
   - 总结学生在标准要求方面的完成情况
   - 给出针对性的改进建议

【重要提醒】
- 请严格按照以上六个模块的标题和要点进行输出
- 每个阶段评价控制在 200–300 字左右

评估格式如下：

## 问诊评价
[基于标准问诊要点的具体评价]

## 体检评价
[基于标准体检项目的具体评价]

## 辅助检查评价
[基于标准辅助检查项目的具体评价]

## 诊断评价
[基于标准诊断的具体评价]

## 治疗评价
[基于标准治疗方案的具体评价]

## 整体评价
[基于标准答案的整体评价]

注意：请严格按照以上要求格式进行评估，不要出现任何其他内容。
"""

    def _parse_evaluation(self, text: str) -> Dict[str, str]:
        sections = {
            "consultation": "",
            "physical":     "",
            "auxiliary":    "",
            "diagnosis":    "",
            "treatment":    "",
            "overall":      "",
        }
        mapping = {
            "问诊评价":    "consultation",
            "体检评价":    "physical",
            "辅助检查评价": "auxiliary",
            "诊断评价":    "diagnosis",
            "治疗评价":    "treatment",
            "整体评价":    "overall",
        }

        current = None
        for line in text.split("\n"):
            line = line.strip()
            matched = False
            for label, key in mapping.items():
                if label in line:
                    current = key
                    matched = True
                    break
            if not matched and current and line and not line.startswith("#"):
                sections[current] += line + "\n"

        return {k: v.strip() for k, v in sections.items()}

    def _default_evaluation(self) -> Dict[str, str]:
        return {
            "consultation": "问诊过程基本完成，建议进一步提升问诊技巧。",
            "physical":     "体格检查项目基本合理，注意检查的全面性。",
            "auxiliary":    "辅助检查选择基本合理，注意检查的针对性。",
            "diagnosis":    "诊断思路基本正确，建议加强诊断依据的收集。",
            "treatment":    "治疗方案需要进一步完善。",
            "overall":      "整体表现中等，有继续提升的空间。",
        }


# ---------------------------------------------------------------------------
# Quick demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    session_file  = "sample_session.json"
    template_file = "sample_template.json"

    for f in (session_file, template_file):
        if not os.path.exists(f):
            print(f"Demo file '{f}' not found. Please provide sample JSON files.")
            exit(1)

    with open(session_file,  encoding="utf-8") as f:
        session = json.load(f)
    with open(template_file, encoding="utf-8") as f:
        template = json.load(f)

    evaluator = ClinicalEvaluator()
    result    = evaluator.evaluate(session, template)

    print("=== EasyMED Clinical Evaluation ===\n")
    labels = {
        "consultation": "问诊技巧",
        "physical":     "体格检查",
        "auxiliary":    "辅助检查",
        "diagnosis":    "诊断思维",
        "treatment":    "治疗方案",
        "overall":      "整体表现",
    }
    for key, label in labels.items():
        print(f"### {label}")
        print(result[key])
        print()
