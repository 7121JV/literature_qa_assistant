#!/usr/bin/env python3
import subprocess
import sys
import os


def check_environment():
    """检查环境"""
    print("检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("错误: 需要Python 3.8或更高版本")
        return False
    print(f"Python版本: {sys.version}")
    return True


def install_requirements():
    """安装依赖"""
    print("安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("依赖安装完成！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败: {e}")
        return False


def download_model():
    """下载模型文件"""
    print("检查模型文件...")
    model_path = "./models/all-MiniLM-L6-v2"

    if os.path.exists(model_path) and os.listdir(model_path):
        print("模型文件已存在")
        return True

    print("下载模型中...")
    try:
        # 使用huggingface_hub下载
        from huggingface_hub import snapshot_download
        snapshot_download(
            repo_id='sentence-transformers/all-MiniLM-L6-v2',
            local_dir=model_path,
            local_dir_use_symlinks=False
        )
        print("模型下载完成！")
        return True
    except Exception as e:
        print(f"模型下载失败: {e}")
        print("请手动下载模型或确保本地模型路径正确")
        return False


def create_directories():
    """创建必要的目录"""
    directories = [
        'data/raw',
        'data/processed',
        'data/faiss_index',
        'models',
        'utils',
        'agents',
        'config',
        'logs',
        'test_data'
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"创建目录: {directory}")


def main():
    """主安装函数"""
    print("=== 文献智能问答助手安装程序 ===")

    if not check_environment():
        return

    create_directories()

    if not install_requirements():
        return

    if not download_model():
        print("警告: 模型下载失败，请手动配置")

    print("\n安装完成！")
    print("请执行以下步骤：")
    print("1. 编辑 .env 文件，设置您的 DeepSeek API 密钥")
    print("2. 将文献文档放入 data/raw/ 目录")
    print("3. 运行: python main.py --process 处理文档")
    print("4. 运行: python main.py --interactive 进入交互模式")


if __name__ == "__main__":
    main()