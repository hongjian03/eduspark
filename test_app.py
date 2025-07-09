#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - 验证应用基本功能
"""

import sys
import json
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from utils.data_loader import load_data_dicts


def test_data_loading():
    """测试数据加载功能"""
    print("=== 测试数据加载 ===")
    
    data_dicts = load_data_dicts()
    
    if not data_dicts:
        print("❌ 数据加载失败")
        return False
    
    print(f"✅ 国家数据: {len(data_dicts.get('countries', {}))} 个")
    print(f"✅ 学历数据: {len(data_dicts.get('degrees', {}))} 个")
    print(f"✅ 专业数据: {len(data_dicts.get('majors', {}))} 个一级专业")
    
    # 显示部分数据示例
    print("\n📊 数据示例:")
    
    # 国家示例
    countries = list(data_dicts['countries'].keys())[:5]
    print(f"国家示例: {', '.join(countries)}")
    
    # 学历示例
    degrees = list(data_dicts['degrees'].keys())[:5]
    print(f"学历示例: {', '.join(degrees)}")
    
    # 专业示例
    majors = list(data_dicts['majors'].keys())
    print(f"专业示例: {', '.join(majors)}")
    
    return True


def test_prompt_generation():
    """测试提示词生成"""
    print("\n=== 测试提示词生成 ===")
    
    from utils.ai_agent import create_default_prompt
    
    data_dicts = load_data_dicts()
    if not data_dicts:
        print("❌ 无法加载数据，跳过提示词测试")
        return False
    
    prompt = create_default_prompt(data_dicts)
    
    if prompt and len(prompt) > 100:
        print("✅ 提示词生成成功")
        print(f"提示词长度: {len(prompt)} 字符")
        print("提示词预览:")
        print("-" * 50)
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        print("-" * 50)
        return True
    else:
        print("❌ 提示词生成失败")
        return False


def test_data_validation():
    """测试数据完整性"""
    print("\n=== 测试数据完整性 ===")
    
    data_dicts = load_data_dicts()
    if not data_dicts:
        print("❌ 无法加载数据")
        return False
    
    # 检查必需的字段
    required_keys = ['countries', 'majors', 'degrees']
    for key in required_keys:
        if key not in data_dicts:
            print(f"❌ 缺少 {key} 数据")
            return False
    
    # 检查专业数据结构
    for major_name, major_info in data_dicts['majors'].items():
        if 'id' not in major_info or 'children' not in major_info:
            print(f"❌ 专业 {major_name} 数据结构不正确")
            return False
    
    print("✅ 数据结构验证通过")
    
    # 统计信息
    total_sub_majors = sum(len(info['children']) for info in data_dicts['majors'].values())
    print(f"📊 总计: {len(data_dicts['countries'])} 个国家, "
          f"{len(data_dicts['degrees'])} 个学历, "
          f"{len(data_dicts['majors'])} 个一级专业, "
          f"{total_sub_majors} 个二级专业")
    
    return True


def main():
    """主测试函数"""
    print("🧪 开始测试留学标签识别应用")
    print("=" * 60)
    
    tests = [
        ("数据加载", test_data_loading),
        ("提示词生成", test_prompt_generation),
        ("数据完整性", test_data_validation)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"\n✅ {test_name} 测试通过")
                passed += 1
            else:
                print(f"\n❌ {test_name} 测试失败")
                failed += 1
        except Exception as e:
            print(f"\n❌ {test_name} 测试异常: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"🎯 测试结果: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有测试通过！应用基础功能正常")
        print("\n📝 下一步:")
        print("1. 配置API密钥在 .streamlit/secrets.toml")
        print("2. 运行 streamlit run app.py 启动应用")
    else:
        print("⚠️ 部分测试失败，请检查配置和数据文件")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 