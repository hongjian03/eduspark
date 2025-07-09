# 🎓 留学标签识别系统

一个基于AI的留学信息标签提取工具，能够从自然语言描述中准确识别国家、专业、学历三个维度的标签。

## ✨ 功能特性

- 🤖 **AI驱动**：使用阿里百炼大模型进行智能识别
- 📊 **标准化输出**：所有标签都经过标准化处理，确保数据一致性
- 🎯 **专业层级**：支持一级专业+二级专业的层级识别
- 🔧 **可定制**：支持自定义提示词
- 📈 **追踪监控**：集成LangSmith进行模型调用追踪
- 🌐 **云部署**：可直接部署到Streamlit Cloud

## 🚀 快速开始

### 本地运行

1. **克隆项目**
```bash
git clone <repository-url>
cd eduspark
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置API密钥**
创建 `.streamlit/secrets.toml` 文件：
```toml
DASHSCOPE_API_KEY = "your_dashscope_api_key_here"
LANGCHAIN_API_KEY = "your_langchain_api_key_here"  # 可选
```

4. **运行应用**
```bash
streamlit run app.py
```

### Streamlit Cloud部署

1. **推送代码到GitHub**

2. **在Streamlit Cloud中创建应用**
   - 连接GitHub仓库
   - 选择主分支和app.py文件

3. **配置Secrets**
   在应用设置中添加：
   ```
   DASHSCOPE_API_KEY = "your_api_key"
   LANGCHAIN_API_KEY = "your_langchain_key"  # 可选
   ```

## 📋 使用说明

### 输入示例
```
我是统计学的本科生，高考600分，我想要申请一下英国的硕士。
```

### 输出结果
```json
{
  "country": "英国",
  "degree": "硕士", 
  "major": "理工科",
  "sub_major": "统计学"
}
```

## 🏗️ 系统架构

```
eduspark/
├── app.py                 # 主应用文件
├── utils/
│   ├── __init__.py
│   ├── data_loader.py     # 数据加载工具
│   └── ai_agent.py        # AI代理模块
├── output/                # 数据字典文件
│   ├── countries_dict.json
│   ├── majors_dict.json
│   └── degrees_dict.json
├── data/                  # 原始CSV数据
├── .streamlit/
│   └── secrets.toml       # 配置文件
├── requirements.txt       # 依赖列表
└── README.md
```

## 🎛️ 配置选项

### 模型选择
支持以下阿里百炼模型：
- **DeepSeek** (默认)
- 通义千问 Plus/Max/Turbo
- 百川2 Turbo
- 零一万物 Large

### 自定义提示词
可以通过界面自定义AI提示词，覆盖默认行为。

## 📊 数据说明

### 国家标签 (28个)
美国、英国、澳大利亚、加拿大、新加坡等主要留学目的地

### 学历标签 (16个)
博士、硕士、本科、高中、社区学院等各类学历层次

### 专业标签 (5个一级 + 50个二级)
- **商科**：金融学、经济学、管理学等
- **文社科**：传媒学、教育学、法学等  
- **理工科**：计算机、数学、统计学等
- **艺术**：艺术设计、音乐、美术等
- **其他**：医学、护理学、体育类等

## 🔧 技术栈

- **前端框架**：Streamlit
- **AI框架**：LangChain
- **大模型**：阿里百炼 (DeepSeek等)
- **数据处理**：Pandas + JSON
- **监控追踪**：LangSmith

## 📝 开发指南

### 添加新标签
1. 更新对应的CSV文件 (`data/` 目录)
2. 重新运行 `dataprocess.py` 生成新的JSON文件
3. 重启应用加载新数据

### 自定义提示词格式
系统支持完全自定义的提示词，只需确保输出格式为：
```json
{
  "country": "国家名或null",
  "degree": "学历名或null",
  "major": "一级专业名或null", 
  "sub_major": "二级专业名或null"
}
```

## ⚠️ 注意事项

1. **API配额**：阿里百炼API有调用限制，请合理使用
2. **数据一致性**：所有标签必须严格匹配数据字典中的值
3. **专业层级**：专业识别必须包含一级和二级的对应关系

## 🐛 故障排除

### 常见问题

1. **API密钥错误**
   - 检查 `secrets.toml` 配置
   - 确认阿里百炼API密钥有效

2. **模型调用失败**
   - 检查网络连接
   - 确认API配额充足

3. **数据加载失败**
   - 确认 `output/` 目录下JSON文件存在
   - 检查文件格式是否正确

## 📞 技术支持

如有问题请联系开发团队或提交Issue。 