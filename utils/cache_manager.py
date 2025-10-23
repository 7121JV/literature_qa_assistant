import os
import json
import hashlib
import pickle
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

from config.settings import settings


class CacheManager:
    def __init__(self):
        self.cache_dir = os.path.join(settings.FAISS_INDEX_PATH, "cache")
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        # 缓存过期时间（小时）
        self.cache_expiry_hours = 24

    def _get_cache_key(self, query: str, filters: Dict[str, Any] = None) -> str:
        """生成缓存键"""
        cache_str = query + str(filters or {})
        return hashlib.md5(cache_str.encode()).hexdigest()

    def get_cached_result(self, query: str, filters: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """获取缓存结果"""
        if not settings.CACHE_ENABLED:
            return None

        cache_key = self._get_cache_key(query, filters)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")

        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    cache_data = pickle.load(f)

                # 检查是否过期
                cache_time = datetime.fromisoformat(cache_data['timestamp'])
                if datetime.now() - cache_time < timedelta(hours=self.cache_expiry_hours):
                    return cache_data['result']
                else:
                    # 删除过期缓存
                    os.remove(cache_file)
            except Exception as e:
                print(f"缓存读取失败: {e}")

        return None

    def set_cached_result(self, query: str, result: Dict[str, Any], filters: Dict[str, Any] = None):
        """设置缓存结果"""
        if not settings.CACHE_ENABLED:
            return

        cache_key = self._get_cache_key(query, filters)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")

        cache_data = {
            'query': query,
            'result': result,
            'timestamp': datetime.now().isoformat(),
            'filters': filters
        }

        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
        except Exception as e:
            print(f"缓存写入失败: {e}")

    def clear_expired_cache(self):
        """清理过期缓存"""
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.pkl'):
                filepath = os.path.join(self.cache_dir, filename)
                try:
                    with open(filepath, 'rb') as f:
                        cache_data = pickle.load(f)

                    cache_time = datetime.fromisoformat(cache_data['timestamp'])
                    if datetime.now() - cache_time >= timedelta(hours=self.cache_expiry_hours):
                        os.remove(filepath)
                except Exception as e:
                    print(f"缓存清理失败 {filename}: {e}")