#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI代理模块
使用LangChain集成阿里百炼模型，进行标签提取
"""

import os
import json
import re
from typing import Dict, Any, Optional
import streamlit as st

# LangChain导入
from langchain_openai import ChatOpenAI

try:
    from langchain_core.messages import HumanMessage, SystemMessage
except ImportError:
    from langchain.schema import HumanMessage, SystemMessage

from langchain.prompts import PromptTemplate

# 数据处理工具
from .data_loader import get_country_list, get_degree_list, get_major_list, get_flat_major_mapping


def setup_langsmith():
    """设置LangSmith追踪"""
    try:
        langchain_api_key = st.secrets.get("LANGCHAIN_API_KEY", "")
        if langchain_api_key:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_API_KEY"] = langchain_api_key
            os.environ["LANGCHAIN_PROJECT"] = "留学标签识别"
            return True
    except Exception as e:
        print(f"LangSmith设置失败: {e}")
    return False


def create_default_prompt(data_dicts: Dict[str, Any]) -> str:
    """
    创建默认提示词
    
    Args:
        data_dicts: 数据字典
        
    Returns:
        默认提示词字符串
    """
    
    country_list = get_country_list(data_dicts['countries'])
    degree_list = get_degree_list(data_dicts['degrees'])
    major_list = get_major_list(data_dicts['majors'])
    
    prompt = f"""
你是一个专业的留学标签识别助手。你的任务是从用户输入的自然语言中准确提取出国家、专业、学历三个标签。

## 标签池（你只能从以下标签中选择，不能自创标签）

### 国家标签池：
{country_list}

### 学历标签池：
{degree_list}

### 专业标签池：
{major_list}

## 提取规则

1. **国家标签**：从国家标签池中选择最匹配的国家名称
2. **学历标签**：从学历标签池中选择最匹配的学历名称
3. **专业标签**：必须输出"一级专业+二级专业"的组合
   - 如果用户提到的是二级专业，需要找到对应的一级专业
   - 格式：一级专业 → 二级专业
   - 例如：理工科 → 计算机、商科 → 金融学

## 输出格式

请严格按照以下JSON格式输出，不要包含任何其他文本：

```json
{{
  "country": "识别到的国家名称或null",
  "degree": "识别到的学历名称或null", 
  "major": "识别到的一级专业名称或null",
  "sub_major": "识别到的二级专业名称或null"
}}
```

## 注意事项

1. 如果某个标签无法识别，请返回最接近的选项，严禁返回空
2. 专业必须严格按照一级→二级的包含关系
3. 只能使用标签池中的准确名称，不能自创或修改
4. 输出必须是有效的JSON格式

现在请分析用户输入并提取标签：
"""
    
    return prompt


def create_ai_agent(model_name: str, data_dicts: Dict[str, Any], custom_prompt: Optional[str] = None):
    """
    创建AI代理
    
    Args:
        model_name: 模型名称
        data_dicts: 数据字典
        custom_prompt: 自定义提示词
        
    Returns:
        AI代理实例
    """
    
    # 设置LangSmith追踪
    setup_langsmith()
    
    # 获取API密钥
    api_key = st.secrets.get("DASHSCOPE_API_KEY", "")
    if not api_key:
        raise ValueError("请配置DASHSCOPE_API_KEY")
    
    # 创建聊天模型（使用阿里云兼容接口）
    llm = ChatOpenAI(
        api_key=api_key,
        model=model_name,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        temperature=0.1
    )
    
    # 使用自定义提示词或默认提示词
    if custom_prompt:
        system_prompt = custom_prompt
    else:
        system_prompt = create_default_prompt(data_dicts)
    
    # 创建简单的标签提取器
    class TagExtractor:
        def __init__(self, llm, system_prompt, data_dicts):
            self.llm = llm
            self.system_prompt = system_prompt
            self.data_dicts = data_dicts
            
        def extract(self, user_input: str) -> Dict[str, Any]:
            """提取标签"""
            try:
                # 创建消息
                messages = [
                    SystemMessage(content=self.system_prompt),
                    HumanMessage(content=user_input)
                ]
                
                # 调用模型
                response = self.llm(messages)
                response_text = response.content
                
                # 解析JSON响应
                raw_result = self._parse_response(response_text)
                
                # 验证和标准化结果
                validated_result = self._validate_result(raw_result)
                
                # 在返回结果中包含原始AI返回和验证后的结果
                validated_result['_raw_ai_response'] = raw_result
                validated_result['_full_ai_response'] = response_text
                
                return validated_result
                
            except Exception as e:
                print(f"标签提取错误: {e}")
                return {
                    "country": None,
                    "degree": None,
                    "major": None,
                    "sub_major": None,
                    "error": str(e),
                    "_raw_ai_response": None,
                    "_full_ai_response": None
                }
        
        def _parse_response(self, response_text: str) -> Dict[str, Any]:
            """解析模型响应"""
            try:
                # 尝试提取JSON
                json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # 如果没有代码块，尝试直接解析
                    json_str = response_text.strip()
                
                result = json.loads(json_str)
                return result
                
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
                print(f"原始响应: {response_text}")
                return {
                    "country": None,
                    "degree": None,
                    "major": None,
                    "sub_major": None,
                    "error": f"JSON解析失败: {str(e)}"
                }
        
        def _validate_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
            """验证和标准化结果"""
            validated = {
                "country": None,
                "degree": None,
                "major": None,
                "sub_major": None
            }
            
            # 验证国家
            if result.get('country') and result['country'] in self.data_dicts['countries']:
                validated['country'] = result['country']
            
            # 验证学历
            if result.get('degree') and result['degree'] in self.data_dicts['degrees']:
                validated['degree'] = result['degree']
            
            # 验证专业
            major = result.get('major')
            sub_major = result.get('sub_major')
            
            if major and major in self.data_dicts['majors']:
                validated['major'] = major
                
                # 验证二级专业
                if sub_major and sub_major in self.data_dicts['majors'][major]['children']:
                    validated['sub_major'] = sub_major
            
            # 如果有错误信息，保留它
            if 'error' in result:
                validated['error'] = result['error']
            
            return validated
    
    return TagExtractor(llm, system_prompt, data_dicts)


def extract_tags(agent, user_input: str) -> Dict[str, Any]:
    """
    使用代理提取标签
    
    Args:
        agent: AI代理实例
        user_input: 用户输入
        
    Returns:
        提取的标签结果
    """
    return agent.extract(user_input) 