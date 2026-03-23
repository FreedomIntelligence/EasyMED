"""
EasyMED - Medical Intent Recognition Module

Classifies a doctor's question during a consultation into one or more
standardized medical inquiry intent categories (30+ categories).

Intent categories cover the full spectrum of clinical history-taking:
chief complaint, onset time, symptom characteristics, past medical history,
family history, social history, ICE (ideas/concerns/expectations), and more.

Usage:
    from intent_recognition import IntentRecognizer

    recognizer = IntentRecognizer()   # reads config from env vars

    intent = recognizer.recognize(
        question="您最近有发烧吗？",
        history=[
            {"question": "哪里不舒服？", "answer": "肚子疼"},
        ],
    )
    print(intent)  # e.g. "伴随症状"
"""

import os
from openai import OpenAI
from typing import List, Dict, Optional


# ---------------------------------------------------------------------------
# Intent category reference
# ---------------------------------------------------------------------------

INTENT_CATEGORIES = [
    "个人信息",
    "主要症状",
    "发作时间",
    "诱因",
    "症况部位",
    "症状性质",
    "持续时间频率",
    "加重缓解情况",
    "伴随症状",
    "病情演变",
    "诊疗经过",
    "一般情况",
    "大小便情况",
    "体重变化",
    "慢性病史",
    "传染病史",
    "手术外伤史",
    "输血史",
    "过敏史",
    "预防接种史",
    "长期用药史",
    "旅行史",
    "生活习惯",
    "职业情况",
    "冶游史",
    "婚育史",
    "家族史",
    "月经史",
    "患者理解",
    "患者担忧",
    "患者期望",
    "闲聊",
]


class IntentRecognizer:
    """
    Classifies doctor questions into standardized medical inquiry intent categories.

    Each question is assigned 1–3 intent labels from the 32-category taxonomy.
    The output is a comma-separated string, e.g. "症况部位,加重缓解情况".

    API configuration (same env vars as VirtualPatient):
        EASYMED_API_KEY   – required
        EASYMED_BASE_URL  – optional
        EASYMED_MODEL     – optional, defaults to "gpt-4o"
    """

    _SYSTEM_PROMPT = """你是一个专业的医疗意图识别助手，根据以下规则及专业的医疗知识，对输入语句进行分类，并返回对应的引号"："前缀内容。不做任何前缀和后缀解释。如：个人信息。你需要结合输入的**医患对话历史**，判断最新输入的语句意图，按照分类规则进行标注。

请注意：每句话最多归类三个，输出格式：个人信息,诱因,一般情况

### 示例：
- 用户输入："你多大了呀？"
  - 输出：个人情况
- **输入**："哪里痛？有什么让症状加重吗？体重有没有变化？"
  - **意图分类**：症况部位,加重缓解因素,体重变化
- **输入**："天气真好啊"
  - **意图分类**：闲聊

### **分类规则：**

#### **1. 临床医疗问诊内容**
根据患者语句内容及对话上下文，将语句归类到以下问诊意图类别：

个人信息：询问病人的一般项目（如"您的姓名是？""今年多大了？"）
主要症状：询问主要症状（如"哪里不舒服？""现在有什么症状？"）
发作时间：询问主要症状发生时间（如"是什么时候开始的？""这种情况从什么时候有的？"）
诱因：询问主要症状病因与诱因（如"这次是为什么会这样？""有什么诱因吗？"）
症况部位：主要症状的部位（如"哪里痛？""不舒服的地方是哪里？"）
症状性质：主要症状的性质（如"疼痛是刺痛还是钝痛？""是什么样的感觉？"）
持续时间频率：主要症状的持续时间或频率（如"这个症状持续多久了？""多久发作一次？"）
加重缓解情况：主要症状的加重及缓解情况（如"有什么让症状加重吗？""做什么会好一点？"）
伴随症状：询问伴随症状及其特点（如"有没有别的不舒服？""还有其他症状吗？"）
病情演变：病情的发展与演变（如"这个症状是越来越严重还是缓解了？""这些天情况有没有变化？"）
诊疗经过：发病后的就诊、治疗情况及效果（如"之前看过医生吗？""做过什么检查吗？""用了什么药？""效果怎么样？"）
一般情况：询问病程中的精神、睡眠、饮食情况（如"睡眠怎么样？""胃口怎么样？"）
大小便情况：询问病程中的大小便情况（如"大便正常吗？""小便有没有异常？"）
体重变化：询问病程中的体力、体重改变情况（如"最近体力怎么样？""体重有没有变化？"）
慢性病史：询问是否有高血压、糖尿病、冠心病等慢性病病史（如"有高血压吗？""得过糖尿病吗？"）
传染病史：询问是否有肝炎、结核等传染病史（如"有没有得过肝炎？""是否有结核病史？"）
手术外伤史：询问是否有手术及外伤史（如"做过手术吗？""有没有受过外伤？"）
输血史：询问是否有输血史（如"输过血吗？"）
过敏史：询问药物或食物过敏情况（如"对什么药物过敏吗？""有食物过敏吗？"）
预防接种史：询问预防接种史（如"打过疫苗吗？""最近有没有接种疫苗？"）
长期用药史：询问目前正在规律或长期使用的所有药物，无论针对何种疾病。（如"您平时需要长期吃什么药吗？""除了这次吃的药，您还有在用其他药吗？"）
旅行史：询问居住地，近期是否有疫区旅居史（如"住在哪里？""近期去过疫区吗？"）
生活习惯：询问个人史中生活习惯及烟酒等嗜好（如"抽烟喝酒吗？""生活习惯怎么样？"）
职业情况：询问个人史中职业和工作条件（如"做什么工作的？""工作环境怎么样？"）
冶游史：高危性行为情况（如"有没有高危性行为？"）
婚育史：询问婚育史（如"结婚了吗？""有几个孩子？"）
家族史：询问家族史（如"家里人有没有类似的病史？""家族里有遗传病吗？"）
月经史：询问月经史（如"初潮是什么时候""月经规律吗？""有没有痛经""最后一次月经是什么时候？"）
患者理解：询问患者本人对病情的理解（如"您自己觉得可能是什么原因引起的呢？"）
患者担忧：询问患者本人对病情的担忧（如"关于这个情况，您最担心的是什么？"）
患者期望：询问患者本人对诊疗的期望（如"您希望我们能帮您解决什么问题？"）
闲聊：寒暄、闲聊或医疗科普问题（如"九价疫苗有什么用？""天气不错啊"，"包括不明确或非医疗问诊类的内容"）
---

### **特别说明：**
- **结合对话历史**：当输入语句模糊或上下文依赖性强时，请结合医患对话历史判断语句意图。例如：
  - 如果患者之前提到了"胃痛"，而后输入"有点久了"，则应归类为"持续时间"。
  - 如果之前提到"头晕"，而后说"是不是贫血引起的"，则应归类为"诱因"。
- 若输入内容过于模糊或无法明确归类，请优先归类为"闲聊"。
- 如果语句不是问句（例如陈述句或描述句），但具备明确医疗信息，请结合上下文归类到对应问诊意图。

---

### 示例：
- 用户输入：`"有没有注意到其他异常的变化？"`
  - 意图分类：伴随症状
- **输入**：`"你平时吃什么药？"`
  - **意图分类**：长期用药史
- **输入**：`"天气真好啊"`
  - **意图分类**：闲聊"""

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

    def recognize(
        self,
        question: str,
        history: Optional[List[Dict]] = None,
    ) -> str:
        """
        Classify the doctor's question into intent category/categories.

        Args:
            question: The doctor's question text.
            history:  Previous turns as [{"question": str, "answer": str}, ...].
                      Up to the last 5 turns are used for context.

        Returns:
            A comma-separated string of intent labels, e.g. "症况部位,加重缓解情况".
            Returns "其他" on failure.
        """
        history_block = ""
        if history:
            history_block = "\n**医患对话历史：**\n"
            for item in (history or [])[-5:]:
                history_block += f"医生问：{item['question']}\n"
                history_block += f"患者答：{item['answer']}\n\n"

        full_prompt = (
            f"{self._SYSTEM_PROMPT}\n\n"
            f"{history_block}\n"
            f'**输入**："{question}"\n'
            f"**意图分类**："
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.1,
            )
            result = response.choices[0].message.content.strip()

            # Strip any accidental "：xxx" prefix the model might produce
            if "：" in result:
                result = result.split("：")[-1].strip()

            return result

        except Exception as exc:
            print(f"[IntentRecognizer] Error: {exc}")
            return "其他"


# ---------------------------------------------------------------------------
# Quick demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    recognizer = IntentRecognizer()
    test_cases = [
        ("您哪里不舒服？", []),
        ("什么时候开始的？", [{"question": "您哪里不舒服？", "answer": "肚子疼"}]),
        ("有没有恶心或者呕吐？", []),
        ("家里有没有类似的毛病？", []),
        ("天气真好啊", []),
    ]

    print("=== Intent Recognition Demo ===\n")
    for q, h in test_cases:
        intent = recognizer.recognize(q, h)
        print(f"Q: {q}")
        print(f"Intent: {intent}\n")
