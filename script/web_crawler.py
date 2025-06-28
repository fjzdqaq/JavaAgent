#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页爬虫工具
根据输入的网址爬取内容，生成HTML、Markdown、纯文本三种格式的文件
并分别保存到knowledge文件夹的不同子目录中
"""

import os
import sys
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import html2text
import re
from datetime import datetime


class WebCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 创建输出目录
        self.base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'knowledge-pre')
        self.html_dir = os.path.join(self.base_dir, 'html')
        self.md_dir = os.path.join(self.base_dir, 'markdown')
        self.txt_dir = os.path.join(self.base_dir, 'text')
        
        self._create_directories()
    
    def _create_directories(self):
        """创建必要的目录"""
        for directory in [self.html_dir, self.md_dir, self.txt_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                print(f"创建目录: {directory}")
    
    def _sanitize_filename(self, url):
        """生成安全的文件名"""
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        path = parsed.path.strip('/').replace('/', '_')
        
        # 生成基础文件名
        if path:
            filename = f"{domain}_{path}"
        else:
            filename = domain
        
        # 清理文件名中的特殊字符
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'_+', '_', filename)
        
        # 添加时间戳避免重名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename}_{timestamp}"
        
        return filename
    
    def _fetch_content(self, url):
        """获取网页内容"""
        try:
            print(f"正在获取网页内容: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            response.encoding = response.apparent_encoding or 'utf-8'
            return response.text
        except requests.RequestException as e:
            print(f"获取网页失败: {e}")
            return None
    
    def _save_html(self, content, filename):
        """保存HTML格式文件"""
        html_path = os.path.join(self.html_dir, f"{filename}.html")
        try:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"HTML文件已保存: {html_path}")
            return html_path
        except Exception as e:
            print(f"保存HTML文件失败: {e}")
            return None
    
    def _convert_to_markdown(self, content):
        """将HTML转换为Markdown格式"""
        try:
            # 配置html2text
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            h.ignore_tables = False
            h.body_width = 0  # 不限制行宽
            h.unicode_snob = True
            h.escape_snob = True
            
            markdown_content = h.handle(content)
            return markdown_content
        except Exception as e:
            print(f"转换为Markdown失败: {e}")
            return None
    
    def _save_markdown(self, content, filename):
        """保存Markdown格式文件"""
        markdown_content = self._convert_to_markdown(content)
        if not markdown_content:
            return None
            
        md_path = os.path.join(self.md_dir, f"{filename}.md")
        try:
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"Markdown文件已保存: {md_path}")
            return md_path
        except Exception as e:
            print(f"保存Markdown文件失败: {e}")
            return None
    
    def _extract_text(self, content):
        """提取纯文本内容"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # 移除脚本和样式元素
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 获取文本
            text = soup.get_text()
            
            # 清理文本
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            print(f"提取文本失败: {e}")
            return None
    
    def _save_text(self, content, filename):
        """保存纯文本文件"""
        text_content = self._extract_text(content)
        if not text_content:
            return None
            
        txt_path = os.path.join(self.txt_dir, f"{filename}.txt")
        try:
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            print(f"文本文件已保存: {txt_path}")
            return txt_path
        except Exception as e:
            print(f"保存文本文件失败: {e}")
            return None
    
    def crawl(self, url):
        """爬取指定URL的内容"""
        print(f"开始爬取: {url}")
        print("-" * 50)
        
        # 验证URL格式
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # 获取网页内容
        content = self._fetch_content(url)
        if not content:
            print("无法获取网页内容，爬取失败")
            return False
        
        # 生成文件名
        filename = self._sanitize_filename(url)
        print(f"生成文件名: {filename}")
        
        # 保存三种格式的文件
        results = []
        
        # 保存HTML
        html_result = self._save_html(content, filename)
        if html_result:
            results.append(html_result)
        
        # 保存Markdown
        md_result = self._save_markdown(content, filename)
        if md_result:
            results.append(md_result)
        
        # 保存纯文本
        txt_result = self._save_text(content, filename)
        if txt_result:
            results.append(txt_result)
        
        print("-" * 50)
        if results:
            print(f"爬取完成！共生成 {len(results)} 个文件:")
            for result in results:
                print(f"  - {result}")
            return True
        else:
            print("爬取失败，未能生成任何文件")
            return False


def main():
    """主函数"""
    crawler = WebCrawler()
    
    if len(sys.argv) > 1:
        # 命令行参数模式
        url = sys.argv[1]
        crawler.crawl(url)
    else:
        # 交互模式
        print("网页爬虫工具")
        print("=" * 50)
        print("功能：根据输入的网址爬取内容，生成HTML、Markdown、纯文本三种格式")
        print("文件将分别保存到knowledge文件夹的html、markdown、text子目录中")
        print("=" * 50)
        
        while True:
            try:
                url = input("\n请输入要爬取的网址 (输入 'quit' 或 'q' 退出): ").strip()
                
                if url.lower() in ['quit', 'q', 'exit']:
                    print("再见！")
                    break
                
                if not url:
                    print("请输入有效的网址")
                    continue
                
                success = crawler.crawl(url)
                
                if success:
                    print("\n是否继续爬取其他网址？")
                else:
                    print("\n爬取失败，请检查网址是否正确或网络连接")
                    
            except KeyboardInterrupt:
                print("\n\n程序被中断，再见！")
                break
            except Exception as e:
                print(f"\n发生错误: {e}")


if __name__ == "__main__":
    main()