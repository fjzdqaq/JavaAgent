#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据处理主脚本
统一管理不同网站的数据爬取和清洗工作
"""

import os
import sys
import argparse
from pathlib import Path

# 添加cleaners目录到系统路径
cleaners_dir = os.path.join(os.path.dirname(__file__), 'cleaners')
sys.path.append(cleaners_dir)


def get_available_cleaners():
    """
    获取可用的清洗器列表
    """
    cleaners = {}
    cleaners_path = Path(__file__).parent / 'cleaners'
    
    for file in cleaners_path.glob('*_cleaner.py'):
        cleaner_name = file.stem.replace('_cleaner', '')
        cleaners[cleaner_name] = file
    
    return cleaners


def run_javaguide_cleaner(input_source):
    """
    运行JavaGuide清洗器
    """
    try:
        from javaguide_cleaner import JavaGuideCleaner
        
        cleaner = JavaGuideCleaner()
        
        if input_source.startswith(('http://', 'https://')):
            print(f"🌐 从URL清洗JavaGuide内容: {input_source}")
            cleaned_data = cleaner.clean_from_url(input_source)
        else:
            print(f"📁 从文件清洗JavaGuide内容: {input_source}")
            cleaned_data = cleaner.clean_from_file(input_source)
        
        if cleaned_data:
            saved_path = cleaner.save_cleaned_data(cleaned_data)
            return saved_path
        else:
            print("❌ 清洗失败")
            return None
            
    except ImportError:
        print("❌ JavaGuide清洗器导入失败，请检查依赖包是否安装")
        return None
    except Exception as e:
        print(f"❌ 清洗过程出错: {e}")
        return None


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='数据处理工具')
    parser.add_argument('--cleaner', '-c', 
                       choices=['javaguide'], 
                       default='javaguide',
                       help='选择清洗器类型')
    parser.add_argument('--input', '-i', 
                       required=True,
                       help='输入源（URL或文件路径）')
    parser.add_argument('--list', '-l', 
                       action='store_true',
                       help='列出可用的清洗器')
    
    args = parser.parse_args()
    
    if args.list:
        print("可用的清洗器:")
        cleaners = get_available_cleaners()
        for name in cleaners:
            print(f"  - {name}")
        return
    
    print("🚀 数据处理工具启动")
    print("=" * 50)
    
    if args.cleaner == 'javaguide':
        result = run_javaguide_cleaner(args.input)
        if result:
            print(f"✅ 处理完成，结果保存至: {result}")
        else:
            print("❌ 处理失败")
    else:
        print(f"❌ 不支持的清洗器类型: {args.cleaner}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # 交互模式
        print("数据处理工具 - 交互模式")
        print("=" * 50)
        
        cleaners = get_available_cleaners()
        print("可用的清洗器:")
        for i, name in enumerate(cleaners, 1):
            print(f"  {i}. {name}")
        
        while True:
            try:
                cleaner_choice = input("\n请选择清洗器类型 (输入数字或名称，'quit'退出): ").strip()
                
                if cleaner_choice.lower() in ['quit', 'q', 'exit']:
                    print("再见！")
                    break
                
                # 处理数字选择
                if cleaner_choice.isdigit():
                    idx = int(cleaner_choice) - 1
                    cleaner_names = list(cleaners.keys())
                    if 0 <= idx < len(cleaner_names):
                        selected_cleaner = cleaner_names[idx]
                    else:
                        print("❌ 无效的选择")
                        continue
                else:
                    selected_cleaner = cleaner_choice
                
                if selected_cleaner not in cleaners:
                    print("❌ 不支持的清洗器类型")
                    continue
                
                input_source = input("请输入URL或文件路径: ").strip()
                if not input_source:
                    print("❌ 输入不能为空")
                    continue
                
                if selected_cleaner == 'javaguide':
                    result = run_javaguide_cleaner(input_source)
                    if result:
                        print(f"✅ 处理完成，结果保存至: {result}")
                    else:
                        print("❌ 处理失败")
                        
            except KeyboardInterrupt:
                print("\n\n程序被中断，再见！")
                break
            except Exception as e:
                print(f"\n❌ 发生错误: {e}")
    else:
        # 命令行模式
        main() 