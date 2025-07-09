#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据处理脚本
处理学历、国家、专业的CSV文件，转换为字典格式
"""

import pandas as pd
import json
import os
from pathlib import Path


class DataProcessor:
    def __init__(self, data_dir="data"):
        """初始化数据处理器"""
        self.data_dir = Path(data_dir)
        self.countries_dict = {}
        self.majors_dict = {}
        self.degrees_dict = {}
    
    def load_countries(self, filename="国家id.csv"):
        """
        加载国家数据
        返回格式：{国家中文名: id}
        """
        file_path = self.data_dir / filename
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            print(f"✅ 成功加载国家数据: {len(df)} 条记录")
            
            # 创建字典：{中文名: id}
            self.countries_dict = {}
            for _, row in df.iterrows():
                country_name = row['name']
                country_id = row['id']
                self.countries_dict[country_name] = country_id
            
            print(f"📊 国家字典创建完成，包含 {len(self.countries_dict)} 个国家")
            return self.countries_dict
            
        except Exception as e:
            print(f"❌ 加载国家数据失败: {e}")
            return {}
    
    def load_majors(self, filename="专业id.csv"):
        """
        加载专业数据
        返回格式：{一级专业名: {id: 一级专业id, children: {二级专业名: 二级专业id}}}
        """
        file_path = self.data_dir / filename
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            # 过滤掉已删除的记录
            df = df[df['is_deleted'] == 0]
            print(f"✅ 成功加载专业数据: {len(df)} 条有效记录")
            
            # 分别获取一级和二级专业
            level1_majors = df[df['level'] == 1]
            level2_majors = df[df['level'] == 2]
            
            self.majors_dict = {}
            
            # 先创建一级专业
            for _, row in level1_majors.iterrows():
                major_name = row['name']
                major_id = row['id']
                self.majors_dict[major_name] = {
                    'id': major_id,
                    'children': {}
                }
            
            # 再添加二级专业
            for _, row in level2_majors.iterrows():
                major_name = row['name']
                major_id = row['id']
                parent_id = row['parent_id']
                
                # 找到对应的一级专业
                parent_major = None
                for level1_name, level1_data in self.majors_dict.items():
                    if level1_data['id'] == parent_id:
                        parent_major = level1_name
                        break
                
                if parent_major:
                    self.majors_dict[parent_major]['children'][major_name] = major_id
                else:
                    print(f"⚠️  找不到二级专业 '{major_name}' 的父级专业 (parent_id: {parent_id})")
            
            print(f"📊 专业字典创建完成:")
            print(f"   - 一级专业: {len(self.majors_dict)} 个")
            
            total_level2 = sum(len(data['children']) for data in self.majors_dict.values())
            print(f"   - 二级专业: {total_level2} 个")
            
            return self.majors_dict
            
        except Exception as e:
            print(f"❌ 加载专业数据失败: {e}")
            return {}
    
    def load_degrees(self, filename="学历id.csv"):
        """
        加载学历数据
        返回格式：{学历名称: id}
        """
        file_path = self.data_dir / filename
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            # 过滤掉已删除的记录
            df = df[df['is_deleted'] == 0]
            print(f"✅ 成功加载学历数据: {len(df)} 条有效记录")
            
            # 创建字典：{学历名称: id}
            self.degrees_dict = {}
            for _, row in df.iterrows():
                degree_name = row['name']
                degree_id = row['id']
                self.degrees_dict[degree_name] = degree_id
            
            print(f"📊 学历字典创建完成，包含 {len(self.degrees_dict)} 种学历")
            return self.degrees_dict
            
        except Exception as e:
            print(f"❌ 加载学历数据失败: {e}")
            return {}
    
    def process_all_data(self):
        """处理所有数据文件"""
        print("🚀 开始处理数据文件...")
        print("=" * 50)
        
        # 加载所有数据
        countries = self.load_countries()
        majors = self.load_majors()
        degrees = self.load_degrees()
        
        return {
            'countries': countries,
            'majors': majors,
            'degrees': degrees
        }
    
    def save_to_json(self, output_dir="output"):
        """保存字典到JSON文件"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        try:
            # 保存国家字典
            countries_file = output_path / "countries_dict.json"
            with open(countries_file, 'w', encoding='utf-8') as f:
                json.dump(self.countries_dict, f, ensure_ascii=False, indent=2)
            
            # 保存专业字典
            majors_file = output_path / "majors_dict.json"
            with open(majors_file, 'w', encoding='utf-8') as f:
                json.dump(self.majors_dict, f, ensure_ascii=False, indent=2)
            
            # 保存学历字典
            degrees_file = output_path / "degrees_dict.json"
            with open(degrees_file, 'w', encoding='utf-8') as f:
                json.dump(self.degrees_dict, f, ensure_ascii=False, indent=2)
            
            # 保存合并的字典
            all_data_file = output_path / "all_data_dict.json"
            all_data = {
                'countries': self.countries_dict,
                'majors': self.majors_dict,
                'degrees': self.degrees_dict
            }
            with open(all_data_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 所有字典已保存到 {output_path} 目录")
            
        except Exception as e:
            print(f"❌ 保存文件失败: {e}")
    
    def display_sample_data(self):
        """显示示例数据"""
        print("\n" + "=" * 50)
        print("📋 数据示例:")
        print("=" * 50)
        
        # 显示国家数据样本
        print("\n🌍 国家数据样本:")
        for i, (name, country_id) in enumerate(list(self.countries_dict.items())[:5]):
            print(f"  {name}: {country_id}")
        print(f"  ... 共 {len(self.countries_dict)} 个国家")
        
        # 显示专业数据样本
        print("\n📚 专业数据样本:")
        for i, (level1_name, level1_data) in enumerate(list(self.majors_dict.items())[:3]):
            print(f"  {level1_name} (id: {level1_data['id']}):")
            for j, (level2_name, level2_id) in enumerate(list(level1_data['children'].items())[:3]):
                print(f"    └─ {level2_name}: {level2_id}")
            if len(level1_data['children']) > 3:
                print(f"    └─ ... 共 {len(level1_data['children'])} 个二级专业")
        
        # 显示学历数据样本
        print("\n🎓 学历数据样本:")
        for i, (name, degree_id) in enumerate(list(self.degrees_dict.items())[:8]):
            print(f"  {name}: {degree_id}")
        if len(self.degrees_dict) > 8:
            print(f"  ... 共 {len(self.degrees_dict)} 种学历")


def main():
    """主函数"""
    print("🎯 教育数据处理工具")
    print("=" * 50)
    
    # 创建数据处理器
    processor = DataProcessor()
    
    # 处理所有数据
    all_data = processor.process_all_data()
    
    # 显示示例数据
    processor.display_sample_data()
    
    # 保存到JSON文件
    processor.save_to_json()
    
    print("\n✅ 数据处理完成！")
    print(f"💡 你现在可以在Python中这样使用：")
    print("""
# 使用示例:
from dataprocess import DataProcessor

processor = DataProcessor()
processor.process_all_data()

# 获取国家ID
country_id = processor.countries_dict['美国']  # 返回: 1

# 获取专业结构
business_majors = processor.majors_dict['商科']['children']  # 返回二级专业字典

# 获取学历ID  
degree_id = processor.degrees_dict['硕士']  # 返回: 2
    """)


if __name__ == "__main__":
    main()
