#!/usr/bin/env python3
"""
系统测试脚本
"""
import os
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
from utils.document_processor import DocumentProcessor
from utils.vector_store import VectorStore


def test_basic_functionality():
    """测试基本功能"""
    print("=== 系统功能测试 ===")

    # 测试配置加载
    print("1. 测试配置加载...")
    assert settings.DEEPSEEK_API_KEY, "DeepSeek API密钥未设置"
    assert os.path.exists(settings.LOCAL_MODEL_PATH), "模型路径不存在"
    print("✓ 配置加载成功")

    # 测试文档处理器
    print("2. 测试文档处理器...")
    processor = DocumentProcessor()
    print("✓ 文档处理器初始化成功")

    # 测试向量存储
    print("3. 测试向量存储...")
    vector_store = VectorStore()
    print("✓ 向量存储初始化成功")

    print("所有基本功能测试通过！")


def create_test_documents():
    """创建测试文档"""
    print("\n=== 创建测试文档 ===")

    # 创建测试文本文件
    test_content = """
    机器学习研究进展

    摘要：本文综述了机器学习领域的最新研究进展，包括深度学习、强化学习和迁移学习等方向。

    1. 引言
    机器学习是人工智能的重要分支，近年来取得了显著进展。

    2. 深度学习
    深度学习通过多层神经网络实现了端到端的学习。【表格】
    | 模型 | 准确率 | 参数量 |
    |------|--------|--------|
    | CNN  | 95.2%  | 1.2M   |
    | RNN  | 92.8%  | 0.8M   |

    3. 强化学习
    强化学习通过智能体与环境的交互进行学习。Q-learning是经典算法之一。

    4. 结论
    机器学习技术将继续推动人工智能的发展。

    公式示例：损失函数可以表示为 $L = \\frac{1}{n}\\sum_{i=1}^{n}(y_i - \\hat{y}_i)^2$
    """

    # 创建测试文件
    test_files = [
        ("test_data/机器学习研究.txt", test_content),
        ("test_data/深度学习进展.md", f"# 深度学习研究\n\n{test_content}"),
    ]

    for file_path, content in test_files:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"创建测试文件: {file_path}")


if __name__ == "__main__":
    test_basic_functionality()
    create_test_documents()
    print("\n测试完成！现在可以运行主程序了。")