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
from utils.ai_agent import create_ai_agent, extract_tags
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
    "deepseek-chat": "DeepSeek (默认)",
    "qwen-plus": "通义千问 Plus",
    "qwen-max": "通义千问 Max", 
    "qwen-turbo": "通义千问 Turbo",
    "baichuan2-turbo": "百川2 Turbo",
    "yi-large": "零一万物 Large"
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
        
        # 侧边栏配置
        with st.sidebar:
            st.header("⚙️ 配置选项")
            
            # 模型选择
            selected_model = st.selectbox(
                "选择AI模型",
                options=list(AVAILABLE_MODELS.keys()),
                format_func=lambda x: AVAILABLE_MODELS[x],
                index=0
            )
            
            # API配置状态
            api_key = st.secrets.get("DASHSCOPE_API_KEY", "")
            if api_key:
                st.success("✅ API密钥已配置")
            else:
                st.error("❌ 请在Streamlit Secrets中配置DASHSCOPE_API_KEY")
            
            # LangSmith配置状态
            langsmith_key = st.secrets.get("LANGCHAIN_API_KEY", "")
            if langsmith_key:
                st.success("✅ LangSmith追踪已启用")
                
            st.markdown("---")
            
            # 数据统计
            st.subheader("📊 数据统计")
            st.write(f"🌍 国家数量: {len(data_dicts['countries'])}")
            st.write(f"🎓 学历数量: {len(data_dicts['degrees'])}")
            
            # 专业统计
            major_count = 0
            for major_info in data_dicts['majors'].values():
                major_count += len(major_info['children'])
            st.write(f"📚 专业数量: {len(data_dicts['majors'])} 个一级专业")
            st.write(f"📖 二级专业: {major_count} 个")
        
        # 主界面布局
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📝 输入区域")
            
            # 用户输入框
            user_input = st.text_area(
                "请输入描述文本",
                placeholder="例如：我是统计学的本科生，高考600分，我想要申请一下英国的硕士。",
                height=120,
                help="请输入包含学历、专业、国家信息的自然语言描述"
            )
            
            # 自定义提示词
            with st.expander("🔧 自定义提示词（可选）"):
                custom_prompt = st.text_area(
                    "自定义提示词",
                    value=st.session_state.get('custom_prompt', ''),
                    placeholder="如果需要自定义AI提示词，请在此输入...",
                    height=200,
                    help="留空将使用系统默认提示词"
                )
                
                if st.button("💾 保存提示词"):
                    st.session_state['custom_prompt'] = custom_prompt
                    st.success("✅ 提示词已保存到会话中")
            
            # 识别按钮
            if st.button("🚀 开始识别", type="primary", use_container_width=True):
                if not user_input.strip():
                    st.warning("⚠️ 请先输入描述文本")
                elif not api_key:
                    st.error("❌ 请先配置API密钥")
                else:
                    with st.spinner("🤖 AI正在分析中..."):
                        try:
                            # 创建AI代理
                            agent = create_ai_agent(
                                model_name=selected_model,
                                data_dicts=data_dicts,
                                custom_prompt=custom_prompt if custom_prompt.strip() else None
                            )
                            
                            # 提取标签
                            result = extract_tags(agent, user_input)
                            
                            # 保存结果到session state
                            st.session_state['last_result'] = result
                            st.session_state['last_input'] = user_input
                            
                        except Exception as e:
                            st.error(f"❌ 识别过程中出现错误: {str(e)}")
                            st.error("详细错误信息:")
                            st.code(traceback.format_exc())
        
        with col2:
            st.subheader("📊 识别结果")
            
            # 显示结果
            if 'last_result' in st.session_state and 'last_input' in st.session_state:
                result = st.session_state['last_result']
                
                # 显示原文
                st.markdown("**原始输入:**")
                st.info(st.session_state['last_input'])
                
                st.markdown("**识别结果:**")
                
                # 创建结果展示区域
                if result:
                    # 国家标签
                    if result.get('country'):
                        st.markdown("🌍 **国家:** " + result['country'])
                    else:
                        st.markdown("🌍 **国家:** 未识别")
                    
                    # 学历标签  
                    if result.get('degree'):
                        st.markdown("🎓 **学历:** " + result['degree'])
                    else:
                        st.markdown("🎓 **学历:** 未识别")
                    
                    # 专业标签
                    if result.get('major'):
                        major_text = result['major']
                        if result.get('sub_major'):
                            major_text += f" → {result['sub_major']}"
                        st.markdown("📚 **专业:** " + major_text)
                    else:
                        st.markdown("📚 **专业:** 未识别")
                    
                    # 详细信息
                    with st.expander("🔍 详细信息"):
                        st.json(result)
                
                else:
                    st.warning("⚠️ 未能识别出标签信息")
            
            else:
                st.info("💡 请在左侧输入文本并点击识别按钮")
                
                # 显示示例
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

if __name__ == "__main__":
    main() 