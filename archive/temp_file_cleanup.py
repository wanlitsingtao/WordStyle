# -*- coding: utf-8 -*-
"""
临时文件清理模块
负责清理上传过程中产生的临时文件
"""
import os
import time
from pathlib import Path
from datetime import datetime, timedelta
import logging

logger = logging.getLogger('WordStyle')


def cleanup_temp_files(temp_dir, max_age_hours=24):
    """
    清理指定目录中的临时文件
    
    Args:
        temp_dir: 临时文件目录路径
        max_age_hours: 文件最大存活时间（小时），超过此时间的文件将被删除
    
    Returns:
        dict: 包含清理统计信息的字典
    """
    temp_path = Path(temp_dir)
    
    if not temp_path.exists():
        logger.warning(f"临时目录不存在: {temp_dir}")
        return {'deleted': 0, 'errors': 0, 'total_size_freed': 0}
    
    deleted_count = 0
    error_count = 0
    total_size_freed = 0
    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
    
    # 查找所有临时文件
    temp_patterns = ['temp_source_*', 'temp_template_*']
    
    for pattern in temp_patterns:
        for temp_file in temp_path.glob(pattern):
            try:
                # 检查文件修改时间
                file_mtime = datetime.fromtimestamp(temp_file.stat().st_mtime)
                
                if file_mtime < cutoff_time:
                    # 文件超过最大存活时间，删除它
                    file_size = temp_file.stat().st_size
                    temp_file.unlink()
                    deleted_count += 1
                    total_size_freed += file_size
                    logger.info(f"已删除过期临时文件: {temp_file.name} ({file_size / 1024:.1f} KB)")
                    
            except Exception as e:
                error_count += 1
                logger.error(f"删除临时文件失败 {temp_file.name}: {e}")
    
    # 同时清理.lock文件
    for lock_file in temp_path.glob('*.lock'):
        try:
            file_mtime = datetime.fromtimestamp(lock_file.stat().st_mtime)
            if file_mtime < cutoff_time:
                lock_file.unlink()
                logger.debug(f"已删除过期锁文件: {lock_file.name}")
        except Exception as e:
            logger.error(f"删除锁文件失败 {lock_file.name}: {e}")
    
    result = {
        'deleted': deleted_count,
        'errors': error_count,
        'total_size_freed': total_size_freed,
        'size_freed_mb': total_size_freed / (1024 * 1024)
    }
    
    if deleted_count > 0:
        logger.info(f"临时文件清理完成: 删除{deleted_count}个文件，释放{result['size_freed_mb']:.2f} MB空间")
    
    return result


def cleanup_on_startup(temp_dir):
    """
    应用启动时清理临时文件
    清理超过24小时的临时文件
    """
    logger.info("开始清理临时文件...")
    result = cleanup_temp_files(temp_dir, max_age_hours=24)
    
    if result['deleted'] > 0:
        logger.info(
            f"临时文件清理完成: 删除{result['deleted']}个文件，"
            f"释放{result['size_freed_mb']:.2f} MB空间"
        )
    else:
        logger.info("没有需要清理的临时文件")
    
    return result


if __name__ == "__main__":
    # 测试代码
    import sys
    from pathlib import Path
    
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 获取项目根目录
    project_root = Path(__file__).parent
    temp_dir = project_root
    
    print("🧹 临时文件清理工具")
    print("=" * 50)
    
    result = cleanup_on_startup(temp_dir)
    
    print(f"\n清理结果:")
    print(f"  删除文件数: {result['deleted']}")
    print(f"  错误数: {result['errors']}")
    print(f"  释放空间: {result['size_freed_mb']:.2f} MB")
