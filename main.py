import os
import sys
import argparse
from typing import List, Dict, Any

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.document_processor import DocumentProcessor
from utils.vector_store import VectorStore
from utils.cache_manager import CacheManager
from agents.deepseek_agent import DeepSeekAgent
from config.settings import settings


class LiteratureQAAssistant:
    def __init__(self):
        self.processor = DocumentProcessor()
        self.vector_store = VectorStore()
        self.cache_manager = CacheManager()
        self.deepseek_agent = DeepSeekAgent()

        # 尝试加载现有索引
        if not self.vector_store.load_index():
            print("未找到现有索引，需要先处理文档")

    def process_documents(self, input_dir: str = None):
        """处理文档并创建索引"""
        if input_dir is None:
            input_dir = settings.RAW_DATA_PATH

        if not os.path.exists(input_dir):
            print(f"输入目录不存在: {input_dir}")
            return

        # 收集所有支持的文档
        documents = []
        for filename in os.listdir(input_dir):
            file_path = os.path.join(input_dir, filename)
            file_ext = os.path.splitext(filename)[1].lower()

            if file_ext in settings.SUPPORTED_EXTENSIONS:
                try:
                    print(f"处理文档: {filename}")
                    processed_doc = self.processor.process_document(file_path)
                    documents.append(processed_doc)

                    # 保存处理后的JSON
                    output_file = os.path.join(
                        settings.PROCESSED_DATA_PATH,
                        f"{os.path.splitext(filename)[0]}.json"
                    )
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(processed_doc, f, ensure_ascii=False, indent=2)

                except Exception as e:
                    print(f"处理文档 {filename} 时出错: {e}")

        if documents:
            print(f"开始创建索引，共 {len(documents)} 个文档")
            self.vector_store.create_index(documents)
            print("索引创建完成")
        else:
            print("未找到可处理的文档")

    def ask_question(self, question: str, content_filter: str = None, use_cache: bool = True):
        """回答问题"""
        # 检查缓存
        if use_cache:
            cached_result = self.cache_manager.get_cached_result(question, {"filter": content_filter})
            if cached_result:
                print("=== 缓存回答 ===")
                self._display_result(cached_result)
                return cached_result

        # 检索相关文档
        print("检索相关文献...")
        search_results = self.vector_store.hybrid_search(
            question, top_k=5, content_filter=content_filter
        )

        if not search_results:
            print("未找到相关文献")
            return None

        # 使用DeepSeek进行分析
        print("进行深度分析...")
        result = self.deepseek_agent.analyze_with_citations(question, search_results)

        # 缓存结果
        if use_cache:
            self.cache_manager.set_cached_result(question, result, {"filter": content_filter})

        # 显示结果
        self._display_result(result)
        return result

    def _display_result(self, result: Dict[str, Any]):
        """显示结果"""
        print("\n=== 思考分析 ===")
        print(result.get('analysis', '无分析内容'))

        print("\n=== 最终回答 ===")
        print(result.get('answer', '无回答内容'))

        print("\n=== 引用来源 ===")
        for i, (idx, score, doc) in enumerate(result.get('sources', [])):
            print(f"{i + 1}. {doc['format_source']}《{doc['title']}》 (相关度: {score:.4f})")

    def interactive_mode(self):
        """交互式模式"""
        print("=== 文献智能问答助手 ===")
        print("输入 'quit' 或 'exit' 退出")
        print("输入 'filter:表格' 或 'filter:公式' 进行内容筛选")

        current_filter = None

        while True:
            try:
                question = input("\n请输入问题: ").strip()

                if question.lower() in ['quit', 'exit']:
                    break
                elif question.startswith('filter:'):
                    filter_type = question.replace('filter:', '').strip()
                    if filter_type in ['表格', '公式', '全部']:
                        current_filter = filter_type if filter_type != '全部' else None
                        print(f"已设置内容筛选: {current_filter or '无'}")
                    else:
                        print("支持的筛选类型: 表格, 公式, 全部")
                    continue

                if question:
                    self.ask_question(question, current_filter)

            except KeyboardInterrupt:
                print("\n再见!")
                break
            except Exception as e:
                print(f"发生错误: {e}")


def main():
    parser = argparse.ArgumentParser(description="文献文档智能问答助手")
    parser.add_argument("--process", action="store_true", help="处理文档并创建索引")
    parser.add_argument("--question", type=str, help="直接提问")
    parser.add_argument("--filter", type=str, choices=['表格', '公式'], help="内容筛选")
    parser.add_argument("--interactive", action="store_true", help="交互式模式")

    args = parser.parse_args()

    assistant = LiteratureQAAssistant()

    if args.process:
        assistant.process_documents()
    elif args.question:
        assistant.ask_question(args.question, args.filter)
    else:
        assistant.interactive_mode()


if __name__ == "__main__":
    main()