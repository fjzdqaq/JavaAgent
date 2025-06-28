# 智能网页爬虫与数据清洗工具

这个项目提供了一套完整的网页数据爬取和清洗解决方案，支持多种网站的专门化处理。

> 🐳 **Docker环境说明**: 本项目基于Docker开发，您只需安装Docker和VSCode（或Cursor），在开发容器中打开即可直接使用。

## 🌟 功能特点

### 通用爬虫功能
- 支持爬取任意网页内容
- 自动生成HTML、Markdown、纯文本三种格式
- 智能文件命名和目录管理
- 支持命令行和交互式两种模式

### 专业数据清洗
- **模块化设计**：为不同网站创建专门的清洗器
- **结构化输出**：转换为标准JSON格式，便于后续处理
- **内容优化**：自动清理广告、无关内容
- **智能解析**：按标题层级结构化提取Q&A内容

## 📁 项目结构

```
├── script/
│   ├── web_crawler.py          # 🕷️ 通用爬虫（获取原始数据）
│   ├── data_processor.py       # 🔧 数据处理主脚本
│   └── cleaners/               # 🧹 清洗脚本目录
│       └── javaguide_cleaner.py # JavaGuide专用清洗器
├── knowledge/                  # 📚 数据存储目录
│   ├── raw/                   # 📄 原始爬取数据
│   ├── cleaned/               # ✨ 清洗后的结构化数据
│   │   └── javaguide/         # JavaGuide专门目录
│   └── processed/             # 🎯 最终处理后的数据
├── .devcontainer/
│   └── Dockerfile             # 🐳 Docker配置（已包含所需依赖）
└── README.md                  # 📖 项目说明文档
```

## 🚀 快速开始

### 方法一：通用网页爬取

```bash
# 交互式模式
python script/web_crawler.py

# 命令行模式
python script/web_crawler.py https://example.com
```

### 方法二：专业数据清洗

```bash
# JavaGuide内容清洗
python script/cleaners/javaguide_cleaner.py https://javaguide.cn/java/basis/java-basic-questions-01.html

# 使用数据处理主脚本
python script/data_processor.py --cleaner javaguide --input https://javaguide.cn/xxx.html

# 交互式数据处理
python script/data_processor.py
```

## 📋 使用示例

### 爬取原始网页

```bash
python script/web_crawler.py https://javaguide.cn/java/basis/java-basic-questions-01.html
```

生成的文件：
- `knowledge/html/javaguide_cn_java_basis_20231201_143000.html`
- `knowledge/markdown/javaguide_cn_java_basis_20231201_143000.md`
- `knowledge/text/javaguide_cn_java_basis_20231201_143000.txt`

### 清洗JavaGuide内容

```bash
python script/cleaners/javaguide_cleaner.py https://javaguide.cn/java/basis/java-basic-questions-01.html
```

生成结构化JSON数据：
```json
{
  "chunk_id": "javaguide-Java基础常见问题-什么是Java_20231201_143000",
  "source_info": {
    "name": "JavaGuide",
    "url": "https://javaguide.cn/java/basis/java-basic-questions-01.html",
    "type": "技术博客",
    "created_at": "2023-12-01T14:30:00"
  },
  "category": "Java基础常见问题",
  "sub_category": "Java简介",
  "question": "什么是Java？",
  "answer_markdown": "Java是一种...",
  "content_for_embedding": "问题: 什么是Java？\n回答: Java是一种...",
  "keywords": ["Java", "编程语言"]
}
```

## 🛠️ 支持的清洗器

| 清洗器 | 支持网站 | 特殊功能 |
|--------|----------|----------|
| `javaguide_cleaner` | JavaGuide技术博客 | Q&A结构化、关键词提取、内容去噪 |

## 🔧 扩展新的清洗器

1. 在 `script/cleaners/` 目录下创建新的清洗器：
```python
# script/cleaners/your_site_cleaner.py
class YourSiteCleaner:
    def clean_from_url(self, url):
        # 实现您的清洗逻辑
        pass
```

2. 在 `data_processor.py` 中添加对应的处理函数

3. 更新命令行参数选项

## 🐳 Docker环境

所有依赖包已在Dockerfile中预配置，包括：
- `requests` - HTTP请求库
- `beautifulsoup4` - HTML解析库
- `html2text` - HTML转Markdown库
- `markdownify` - 高级Markdown转换库
- `lxml` - 高性能XML/HTML解析器

在Docker环境中可直接运行，无需手动安装依赖。

## 💡 最佳实践

### 数据处理工作流

1. **原始爬取**：使用通用爬虫获取网页原始内容
2. **专业清洗**：根据网站特点使用对应清洗器
3. **结构化存储**：清洗后数据保存为JSON格式
4. **进一步处理**：可用于RAG、搜索、分析等应用

### 文件管理建议

- `knowledge/raw/` - 保存爬虫原始数据，便于重新处理
- `knowledge/cleaned/` - 按网站分类保存清洗后数据
- `knowledge/processed/` - 保存最终应用数据

## ⚠️ 注意事项

1. **合规使用**：请遵守网站robots.txt规则和相关法律法规
2. **请求频率**：避免过于频繁的请求，保护目标网站
3. **内容权限**：确保有权使用和处理目标网站内容
4. **错误处理**：清洗器会自动处理大部分错误，如遇问题请检查网址和网络

## 🔄 版本说明

- **v1.0**: 基础爬虫功能
- **v2.0**: 增加模块化清洗器架构
- **v2.1**: 优化JavaGuide清洗器，增加关键词提取
