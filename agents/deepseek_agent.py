import requests
import json
from typing import List, Dict, Any

from config.settings import settings


class DeepSeekAgent:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL

    def analyze_with_citations(self, query: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """基于检索结果进行深度分析并生成引用"""

        # 准备上下文
        context = self._prepare_context(search_results)

        # 构建提示词
        prompt = self._build_analysis_prompt(query, context, search_results)

        # 调用DeepSeek API
        response = self._call_deepseek_api(prompt)

        # 解析响应
        return self._parse_response(response, search_results)

    def _prepare_context(self, search_results: List[Dict[str, Any]]) -> str:
        """准备上下文信息"""
        context_parts = []

        for i, (idx, score, doc) in enumerate(search_results):
            context_parts.append(f"文档 {i + 1}:\n")
            context_parts.append(f"标题: {doc['title']}\n")
            context_parts.append(f"格式: {doc['format_source']}\n")
            context_parts.append(f"内容片段: {doc['content'][:500]}...\n")
            context_parts.append(f"相关度得分: {score:.4f}\n")
            context_parts.append("-" * 50 + "\n")

        return "\n".join(context_parts)

    def _build_analysis_prompt(self, query: str, context: str, search_results: List[Dict[str, Any]]) -> str:
        """构建分析提示词"""

        prompt = f"""你是一个专业的文献分析助手。请基于以下检索到的文献内容，回答用户的问题。

用户问题: {query}

检索到的文献内容:
{context}

请按照以下要求进行分析和回答:

1. 首先进行思考分析，整合不同文献的观点，进行逻辑推理
2. 在回答中必须明确标注引用来源，格式为: "来源: [格式]《标题》[具体位置]"
3. 具体位置可以是段落编号、章节名称、表格/公式编号等
4. 回答要专业、准确，基于文献内容进行解读
5. 如果文献中有矛盾观点，请进行对比分析

请按以下格式输出:
思考分析: [你的详细分析过程，包括观点整合、数据关联、逻辑推导等]

回答: [包含引用标注的最终回答，每个重要观点都要注明来源]
"""
        return prompt

    def _call_deepseek_api(self, prompt: str) -> str:
        """调用DeepSeek API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            return result['choices'][0]['message']['content']

        except Exception as e:
            print(f"DeepSeek API调用失败: {e}")
            return f"API调用错误: {str(e)}"

    def _parse_response(self, response: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """解析API响应"""
        # 简单的响应解析，实际应该更复杂
        lines = response.split('\n')
        analysis = ""
        answer = ""
        current_section = ""

        for line in lines:
            if line.startswith('思考分析:'):
                current_section = "analysis"
                analysis = line.replace('思考分析:', '').strip()
            elif line.startswith('回答:'):
                current_section = "answer"
                answer = line.replace('回答:', '').strip()
            else:
                if current_section == "analysis":
                    analysis += "\n" + line
                elif current_section == "answer":
                    answer += "\n" + line

        return {
            "analysis": analysis.strip(),
            "answer": answer.strip(),
            "sources": search_results
        }