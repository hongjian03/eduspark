#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
留学标签识别应用
使用AI从自然语言中提取国家、专业、学历标签
"""

import streamlit as st
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import traceback

# 导入自定义模块
from utils.ai_agent import create_ai_agent, extract_tags, create_default_prompt
from utils.data_loader import load_data_dicts

# 配置页面
st.set_page_config(
    page_title="留学标签识别",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 加载数据字典
@st.cache_data
def load_cached_data():
    """缓存加载数据字典"""
    return load_data_dicts()

# 可用的模型列表（阿里百炼）
AVAILABLE_MODELS = {
    "deepseek-v3": "DeepSeek-v3 (默认)",
    "deepseek-r1": "DeepSeek-r1",
    "qwen-plus": "通义千问-plus", 
    "qwen-max": "通义千问-max"
}

def main():
    """主函数"""
    st.title("🎓 留学标签识别系统")
    st.markdown("---")
    
    try:
        # 加载数据字典
        with st.spinner("正在加载数据字典..."):
            data_dicts = load_cached_data()
        
        if not data_dicts:
            st.error("❌ 无法加载数据字典，请检查文件是否存在")
            return
            
        st.success("✅ 数据字典加载成功")
    except Exception as e:
        st.error(f"❌ 加载数据时出现错误: {str(e)}")
        return
        
    # 读取所有标签池
    country_options = list(data_dicts['countries'].keys())
    degree_options = list(data_dicts['degrees'].keys())
    major_options = list(data_dicts['majors'].keys())
    default_sub_major_options = list(data_dicts['majors'][major_options[0]]['children'].keys())
    ai_country = st.session_state.get('ai_country', country_options[0])
    ai_degree = st.session_state.get('ai_degree', degree_options[0])
    ai_major = st.session_state.get('ai_major', major_options[0])
    ai_sub_major = st.session_state.get('ai_sub_major', default_sub_major_options[0])

    # 1. 输入文本
    st.subheader("📝 输入区域")
    user_input = st.text_area(
        "请输入描述文本",
        placeholder="例如：我是统计学的本科生，高考600分，我想要申请一下英国的硕士。",
        height=120,
        help="请输入包含学历、专业、国家信息的自然语言描述"
    )
    if st.button("🚀 开始识别", type="primary"):
        api_key = st.secrets.get("DASHSCOPE_API_KEY", "")
        if not user_input.strip():
            st.warning("⚠️ 请先输入描述文本")
        elif not api_key:
            st.error("❌ 请先配置API密钥")
        else:
            with st.spinner("🤖 AI正在分析中..."):
                try:
                    # 创建AI代理
                    agent = create_ai_agent(
                        model_name=st.session_state.get('selected_model', list(AVAILABLE_MODELS.keys())[0]),
                        data_dicts=data_dicts,
                        custom_prompt=st.session_state.get('custom_prompt', None)
                    )
                    result = extract_tags(agent, user_input)
                    st.session_state['last_result'] = result
                    st.session_state['last_input'] = user_input
                    # 自动联动下拉框
                    if result.get('country') in country_options:
                        st.session_state['ai_country'] = result['country']
                    if result.get('degree') in degree_options:
                        st.session_state['ai_degree'] = result['degree']
                    if result.get('major') in major_options:
                        st.session_state['ai_major'] = result['major']
                        sub_major_list = list(data_dicts['majors'][result['major']]['children'].keys())
                        if result.get('sub_major') in sub_major_list:
                            st.session_state['ai_sub_major'] = result['sub_major']
                        else:
                            st.session_state['ai_sub_major'] = sub_major_list[0]
                except Exception as e:
                    st.error(f"❌ 识别过程中出现错误: {str(e)}")
                    st.error("详细错误信息:")
                    st.code(traceback.format_exc())

    # 2. 识别结果
    st.markdown("---")
    st.subheader("📊 识别结果")
    if 'last_result' in st.session_state and 'last_input' in st.session_state:
        result = st.session_state['last_result']
        st.markdown("**原始输入:**")
        st.info(st.session_state['last_input'])
        st.markdown("**识别结果:**")
        if result:
            if result.get('country'):
                st.markdown("🌍 **国家:** " + result['country'])
            else:
                st.markdown("🌍 **国家:** 未识别")
            if result.get('degree'):
                st.markdown("🎓 **学历:** " + result['degree'])
            else:
                st.markdown("🎓 **学历:** 未识别")
            if result.get('major'):
                major_text = result['major']
                if result.get('sub_major'):
                    major_text += f" → {result['sub_major']}"
                st.markdown("📚 **专业:** " + major_text)
            else:
                st.markdown("📚 **专业:** 未识别")
            with st.expander("🔍 详细信息"):
                st.json(result)
        else:
            st.warning("⚠️ 未能识别出标签信息")
    else:
        st.info("💡 请在上方输入文本并点击识别按钮")
        st.markdown("**示例输入:**")
        examples = [
            "我是统计学的本科生，想申请英国的硕士",
            "计算机专业博士，考虑去美国深造", 
            "金融学本科毕业，希望到澳大利亚读研",
            "艺术设计专业，想去日本留学",
            "医学院学生，计划申请加拿大的博士项目"
        ]
        for i, example in enumerate(examples, 1):
            st.markdown(f"{i}. {example}")

    # 3. 模拟选项框
    st.markdown("---")
    st.subheader("🎯 标签选择模拟（AI识别后自动联动）")
    country_select = st.selectbox("意向目的地", country_options, index=country_options.index(st.session_state.get('ai_country', country_options[0])), key="ai_country")
    major_select = st.selectbox("意向专业（一级）", major_options, index=major_options.index(st.session_state.get('ai_major', major_options[0])), key="ai_major")
    sub_major_options = list(data_dicts['majors'][st.session_state['ai_major']]['children'].keys())
    sub_major_select = st.selectbox("意向专业（二级）", sub_major_options, index=sub_major_options.index(st.session_state.get('ai_sub_major', sub_major_options[0])) if st.session_state.get('ai_sub_major', sub_major_options[0]) in sub_major_options else 0, key="ai_sub_major")
    degree_select = st.selectbox("学历", degree_options, index=degree_options.index(st.session_state.get('ai_degree', degree_options[0])), key="ai_degree")

    # 4. 选择模型
    st.markdown("---")
    st.subheader("🧠 选择AI模型")
    selected_model = st.selectbox(
        "选择AI模型",
        options=list(AVAILABLE_MODELS.keys()),
        format_func=lambda x: AVAILABLE_MODELS[x],
        index=0,
        key="selected_model"
    )
    api_key = st.secrets.get("DASHSCOPE_API_KEY", "")
    if api_key:
        st.success("✅ API密钥已配置")
    else:
        st.error("❌ 请在Streamlit Secrets中配置DASHSCOPE_API_KEY")

    # 5. 自定义提示词
    st.markdown("---")
    st.subheader("🔧 自定义提示词（可选）")
    default_prompt = create_default_prompt(data_dicts)
    if not st.session_state.get('custom_prompt'):
        st.session_state['custom_prompt'] = default_prompt
    custom_prompt = st.text_area(
        "自定义提示词",
        value=st.session_state['custom_prompt'],
        placeholder="如果需要自定义AI提示词，请在此输入...",
        height=200,
        help="留空将使用系统默认提示词"
    )
    if st.button("💾 保存提示词"):
        st.session_state['custom_prompt'] = custom_prompt
        st.success("✅ 提示词已保存到会话中")

if __name__ == "__main__":
    main() 