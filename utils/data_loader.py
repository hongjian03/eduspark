#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据加载工具
用于加载和处理JSON数据字典
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


def load_data_dicts(data_dir: str = "output") -> Optional[Dict[str, Any]]:
    """
    加载所有数据字典
    
    Args:
        data_dir: 数据目录路径
        
    Returns:
        包含所有数据字典的字典，如果加载失败返回None
    """
    try:
        base_path = Path(__file__).parent.parent / data_dir
        
        # 加载各个数据文件
        files_to_load = {
            'countries': 'countries_dict.json',
            'majors': 'majors_dict.json', 
            'degrees': 'degrees_dict.json'
        }
        
        data_dicts = {}
        
        for key, filename in files_to_load.items():
            file_path = base_path / filename
            
            if not file_path.exists():
                print(f"警告: 文件 {file_path} 不存在")
                continue
                
            with open(file_path, 'r', encoding='utf-8') as f:
                data_dicts[key] = json.load(f)
                
        return data_dicts
        
    except Exception as e:
        print(f"加载数据字典时出现错误: {e}")
        return None


def get_country_list(countries_dict: Dict[str, int]) -> str:
    """
    获取国家列表的字符串表示
    
    Args:
        countries_dict: 国家字典
        
    Returns:
        国家列表字符串
    """
    return "、".join(countries_dict.keys())


def get_degree_list(degrees_dict: Dict[str, int]) -> str:
    """
    获取学历列表的字符串表示
    
    Args:
        degrees_dict: 学历字典
        
    Returns:
        学历列表字符串
    """
    return "、".join(degrees_dict.keys())


def get_major_list(majors_dict: Dict[str, Any]) -> str:
    """
    获取专业列表的字符串表示（一级专业和二级专业）
    
    Args:
        majors_dict: 专业字典
        
    Returns:
        专业列表字符串
    """
    major_list = []
    
    for first_level, info in majors_dict.items():
        major_list.append(f"{first_level}")
        
        # 添加二级专业
        for second_level in info['children'].keys():
            major_list.append(f"  - {second_level}")
    
    return "\n".join(major_list)


def get_flat_major_mapping(majors_dict: Dict[str, Any]) -> Dict[str, str]:
    """
    获取扁平化的专业映射（二级专业 -> 一级专业）
    
    Args:
        majors_dict: 专业字典
        
    Returns:
        扁平化的专业映射字典
    """
    mapping = {}
    
    for first_level, info in majors_dict.items():
        # 一级专业映射到自己
        mapping[first_level] = first_level
        
        # 二级专业映射到一级专业
        for second_level in info['children'].keys():
            mapping[second_level] = first_level
            
    return mapping 