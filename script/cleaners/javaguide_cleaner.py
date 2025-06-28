#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JavaGuide专用内容清洗器
用于将JavaGuide网站的原始HTML内容清洗为结构化的JSON数据
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import re
import json
from datetime import datetime
from urllib.parse import urlparse


class JavaGuideCleaner:
    def __init__(self):
        self.base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'knowledge')
        self.raw_dir = os.path.join(self.base_dir, 'raw')
        self.cleaned_dir = os.path.join(self.base_dir, 'cleaned', 'javaguide')
        
        # 创建输出目录
        os.makedirs(self.cleaned_dir, exist_ok=True)
    
    def clean_from_url(self, url):
        """
        直接从URL获取内容并清洗
        """
        try:
            print(f"正在获取网页内容: {url}")
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            response.encoding = response.apparent_encoding or 'utf-8'
            
            return self.clean_html_content(response.text, url)
            
        except requests.RequestException as e:
            print(f"请求失败: {e}")
            return []
    
    def clean_from_file(self, html_file_path, source_url=None):
        """
        从本地HTML文件清洗内容
        """
        try:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            if not source_url:
                # 尝试从文件名推断URL
                filename = os.path.basename(html_file_path)
                source_url = f"本地文件: {filename}"
            
            return self.clean_html_content(html_content, source_url)
            
        except Exception as e:
            print(f"读取文件失败: {e}")
            return []
    
    def clean_html_content(self, html_content, source_url):
        """
        清洗HTML内容的核心方法
        """
        soup = BeautifulSoup(html_content, 'lxml')
        
        # 查找主要内容区域
        main_content = self._find_main_content(soup)
        if not main_content:
            print("未找到主要内容区域")
            return []
        
        # 提取文章元数据
        article_title = self._extract_title(main_content)
        print(f"文章标题: {article_title}")
        
        # 结构化解析内容
        knowledge_chunks = self._parse_content_structure(main_content, article_title, source_url)
        
        print(f"成功提取 {len(knowledge_chunks)} 个知识块")
        return knowledge_chunks
    
    def _find_main_content(self, soup):
        """
        查找主要内容区域
        """
        # 尝试多种可能的主内容选择器
        selectors = [
            'main',
            '.main-content',
            '#main-content', 
            'article',
            '.article-content',
            '.content',
            '.post-content'
        ]
        
        for selector in selectors:
            content = soup.select_one(selector)
            if content:
                return content
        
        # 如果都找不到，返回body
        return soup.find('body')
    
    def _extract_title(self, content):
        """
        提取文章标题
        """
        # 尝试多种方式获取标题
        title_selectors = ['h1', '.title', '.article-title']
        
        for selector in title_selectors:
            title_elem = content.select_one(selector)
            if title_elem:
                return title_elem.get_text(strip=True)
        
        return "未知标题"
    
    def _parse_content_structure(self, content, article_title, source_url):
        """
        解析内容结构，提取Q&A对
        """
        knowledge_chunks = []
        
        # 查找所有的二级标题作为分类
        h2_elements = content.find_all('h2')
        
        if not h2_elements:
            # 如果没有h2，尝试h3
            return self._parse_simple_structure(content, article_title, source_url)
        
        for h2 in h2_elements:
            sub_category = h2.get_text(strip=True)
            
            # 查找当前h2下的所有h3
            h3_elements = []
            current = h2.find_next_sibling()
            
            while current:
                if current.name == 'h2':
                    break
                if current.name == 'h3':
                    h3_elements.append(current)
                current = current.find_next_sibling()
            
            # 如果没有h3，将整个h2section作为一个知识块
            if not h3_elements:
                content_elements = self._get_section_content(h2)
                if content_elements:
                    chunk = self._create_knowledge_chunk(
                        sub_category, "", content_elements, 
                        article_title, sub_category, source_url
                    )
                    knowledge_chunks.append(chunk)
                continue
            
            # 处理每个h3
            for h3 in h3_elements:
                question = h3.get_text(strip=True)
                content_elements = self._get_section_content(h3)
                
                if content_elements:
                    chunk = self._create_knowledge_chunk(
                        question, sub_category, content_elements,
                        article_title, sub_category, source_url
                    )
                    knowledge_chunks.append(chunk)
        
        return knowledge_chunks
    
    def _parse_simple_structure(self, content, article_title, source_url):
        """
        解析简单结构（只有h3或更简单的结构）
        """
        knowledge_chunks = []
        h3_elements = content.find_all('h3')
        
        if not h3_elements:
            # 没有明确的标题结构，将整个内容作为一个块
            all_text = content.get_text(strip=True)
            if all_text:
                chunk = self._create_knowledge_chunk(
                    article_title, "", [content],
                    article_title, "通用", source_url
                )
                knowledge_chunks.append(chunk)
            return knowledge_chunks
        
        for h3 in h3_elements:
            question = h3.get_text(strip=True)
            content_elements = self._get_section_content(h3)
            
            if content_elements:
                chunk = self._create_knowledge_chunk(
                    question, "", content_elements,
                    article_title, "通用", source_url
                )
                knowledge_chunks.append(chunk)
        
        return knowledge_chunks
    
    def _get_section_content(self, header_element):
        """
        获取标题元素后面的内容，直到下一个同级或更高级标题
        """
        content_elements = []
        current = header_element.find_next_sibling()
        header_level = int(header_element.name[1]) if header_element.name.startswith('h') else 999
        
        while current:
            if current.name and current.name.startswith('h'):
                current_level = int(current.name[1])
                if current_level <= header_level:
                    break
            
            if current.name:  # 忽略纯文本节点
                content_elements.append(current)
            current = current.find_next_sibling()
        
        return content_elements
    
    def _create_knowledge_chunk(self, question, sub_category, content_elements, 
                               article_title, category, source_url):
        """
        创建知识块JSON对象
        """
        # 将内容元素转换为HTML字符串
        answer_html = "".join(str(elem) for elem in content_elements)
        
        # 转换为Markdown格式
        answer_md = md(answer_html, heading_style="ATX")
        
        # 清洗内容
        answer_md = self._clean_markdown_content(answer_md)
        
        # 生成唯一ID
        chunk_id = self._generate_chunk_id(article_title, question)
        
        # 创建知识块
        chunk = {
            "chunk_id": chunk_id,
            "source_info": {
                "name": "JavaGuide",
                "url": source_url,
                "type": "技术博客",
                "created_at": datetime.now().isoformat()
            },
            "category": category,
            "sub_category": sub_category,
            "question": question,
            "answer_markdown": answer_md.strip(),
            "answer_text": self._markdown_to_text(answer_md),
            "content_for_embedding": f"问题: {question}\n回答: {self._markdown_to_text(answer_md)}",
            "keywords": self._extract_keywords(question + " " + answer_md),
            "word_count": len(answer_md.split()),
            "character_count": len(answer_md)
        }
        
        return chunk
    
    def _clean_markdown_content(self, markdown_text):
        """
        清洗Markdown内容
        """
        # 移除广告等不需要的内容
        patterns_to_remove = [
            r'这是一则或许对你有用的小广告.*',
            r'推荐阅读.*',
            r'相关推荐.*',
            r'点击关注.*',
            r'扫码关注.*',
            r'关注公众号.*',
            r'\[.*?\]\(#.*?\)',  # 移除锚点链接
        ]
        
        for pattern in patterns_to_remove:
            markdown_text = re.sub(pattern, '', markdown_text, flags=re.DOTALL | re.IGNORECASE)
        
        # 清理多余的空行
        markdown_text = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown_text)
        
        return markdown_text.strip()
    
    def _markdown_to_text(self, markdown_text):
        """
        将Markdown转换为纯文本
        """
        # 移除Markdown标记
        text = re.sub(r'[#*`_\[\]()!]', '', markdown_text)
        text = re.sub(r'\n+', ' ', text)
        return text.strip()
    
    def _extract_keywords(self, text):
        """
        提取关键词（简单实现）
        """
        # 这里可以使用更复杂的NLP技术，现在先简单实现
        tech_keywords = [
            'Java', 'Spring', 'Maven', 'Gradle', 'JVM', 'MySQL', 'Redis',
            'Docker', 'Kubernetes', 'Git', 'Linux', 'HTTP', 'TCP', 'IP',
            '算法', '数据结构', '设计模式', '微服务', '分布式', '高并发'
        ]
        
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in tech_keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords[:10]  # 最多返回10个关键词
    
    def _generate_chunk_id(self, article_title, question):
        """
        生成唯一的chunk ID
        """
        base_id = f"javaguide-{article_title}-{question}"
        # 清理特殊字符并截断
        clean_id = re.sub(r'[^\w\-]', '_', base_id)[:100]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{clean_id}_{timestamp}"
    
    def save_cleaned_data(self, knowledge_chunks, filename=None):
        """
        保存清洗后的数据
        """
        if not knowledge_chunks:
            print("没有数据需要保存")
            return None
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"javaguide_cleaned_{timestamp}.json"
        
        output_path = os.path.join(self.cleaned_dir, filename)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(knowledge_chunks, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 成功保存 {len(knowledge_chunks)} 个知识块到: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ 保存文件失败: {e}")
            return None


def main():
    """
    主函数
    """
    cleaner = JavaGuideCleaner()
    
    if len(sys.argv) > 1:
        # 命令行参数模式
        input_path = sys.argv[1]
        
        if input_path.startswith(('http://', 'https://')):
            # URL模式
            cleaned_data = cleaner.clean_from_url(input_path)
        else:
            # 文件模式
            cleaned_data = cleaner.clean_from_file(input_path)
        
        if cleaned_data:
            cleaner.save_cleaned_data(cleaned_data)
    else:
        # 交互模式
        print("JavaGuide内容清洗器")
        print("=" * 50)
        print("支持两种输入模式：")
        print("1. 输入JavaGuide文章URL")
        print("2. 输入本地HTML文件路径")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n请输入URL或文件路径 (输入 'quit' 退出): ").strip()
                
                if user_input.lower() in ['quit', 'q', 'exit']:
                    print("再见！")
                    break
                
                if not user_input:
                    print("请输入有效的URL或文件路径")
                    continue
                
                if user_input.startswith(('http://', 'https://')):
                    cleaned_data = cleaner.clean_from_url(user_input)
                else:
                    cleaned_data = cleaner.clean_from_file(user_input)
                
                if cleaned_data:
                    saved_path = cleaner.save_cleaned_data(cleaned_data)
                    if saved_path:
                        print(f"\n数据已保存，可以查看第一个知识块示例：")
                        print(json.dumps(cleaned_data[0], indent=2, ensure_ascii=False)[:500] + "...")
                else:
                    print("清洗失败，请检查输入")
                    
            except KeyboardInterrupt:
                print("\n\n程序被中断，再见！")
                break
            except Exception as e:
                print(f"\n发生错误: {e}")


if __name__ == "__main__":
    main() 