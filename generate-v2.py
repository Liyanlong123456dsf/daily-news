#!/usr/bin/env python3
"""生成网页版每日早报 - V2版本
采用移动端优化的设计，参考 Craft.do 和 Notion 风格
"""
import sys
import re
from datetime import datetime
import markdown

def parse_markdown_sections(md_content):
    """解析 markdown 内容，转换为 HTML"""
    
    # 分离标题
    lines = md_content.strip().split('\n')
    
    html_parts = []
    current_section = None
    in_news_list = False
    in_github_list = False
    in_trend_box = False
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # 处理一级标题 - 板块标题
        if line.startswith('## '):
            # 关闭之前的列表
            if in_news_list:
                html_parts.append('</div>')
                in_news_list = False
            if in_github_list:
                html_parts.append('</div>')
                in_github_list = False
            if in_trend_box:
                html_parts.append('</div></div>')
                in_trend_box = False
            
            section_title = line[3:].strip()
            section_class = "section"
            section_icon = "📝"
            
            # 根据标题确定图标和样式
            if "综合" in section_title or "要闻" in section_title:
                section_icon = "📰"
            elif "AI" in section_title:
                section_class = "section section-ai"
                section_icon = "🤖"
            
            html_parts.append(f'''
<div class="{section_class}">
    <div class="section-header">
        <div class="section-icon">{section_icon}</div>
        <h2 class="section-title">{section_title}</h2>
    </div>
''')
            current_section = section_title
            i += 1
            continue
        
        # 处理趋势观察（必须在普通 ### 标题之前检查）
        if (line.startswith('### ') or line.startswith('#### ')) and ("趋势" in line or "观察" in line):
            if in_news_list:
                html_parts.append('</div>')
                in_news_list = False
            if in_github_list:
                html_parts.append('</div>')
                in_github_list = False
            
            subsection_title = line.strip('#').strip()
            html_parts.append(f'''
<div class="trend-box">
    <div class="trend-header">
        <span class="trend-icon">🔍</span>
        <span class="trend-title">{subsection_title}</span>
    </div>
    <div class="trend-content">
''')
            in_trend_box = True
            i += 1            
            # 收集段落内容
            trend_content = []
            while i < len(lines) and not lines[i].strip().startswith('#') and not lines[i].strip().startswith('---'):
                if lines[i].strip():
                    trend_content.append(lines[i].strip())
                i += 1
            if trend_content:
                html_parts.append(f'<p>{" ".join(trend_content)}</p>')
            html_parts.append('</div></div>')
            in_trend_box = False
            continue
        
        # 处理三级标题 - 子板块
        if line.startswith('### '):
            if in_news_list:
                html_parts.append('</div>')
                in_news_list = False
            if in_github_list:
                html_parts.append('</div>')
                in_github_list = False
            
            subsection_title = line[4:].strip()
            html_parts.append(f'<h3 style="font-size: 1.1rem; font-weight: 600; margin: 1.5rem 0 1rem; color: var(--text-primary);">{subsection_title}</h3>')
            current_section = subsection_title  # 更新当前板块
            i += 1
            continue
        
        # 处理四级标题 - 子子板块
        if line.startswith('#### '):
            if in_news_list:
                html_parts.append('</div>')
                in_news_list = False
            if in_github_list:
                html_parts.append('</div>')
                in_github_list = False
            
            subsection_title = line[5:].strip()
            html_parts.append(f'<h3 style="font-size: 1.1rem; font-weight: 600; margin: 1.5rem 0 1rem; color: var(--text-primary);">{subsection_title}</h3>')
            current_section = subsection_title  # 更新当前板块以便 GitHub 热榜识别
            i += 1
            continue
        
        # 处理段落文本
        if line and not line.startswith('#') and not line.startswith('-') and not re.match(r'^\d+\.', line):
            if in_trend_box:
                html_parts.append(f'<p>{line}</p>')
            i += 1
            continue
        
        i += 1
    
    # 关闭未关闭的容器
    if in_news_list:
        html_parts.append('</div>')
    if in_github_list:
        html_parts.append('</div>')
    if in_trend_box:
        html_parts.append('</div></div>')
    if current_section:
        html_parts.append('</div>')
    
    return '\n'.join(html_parts)

def generate_html(title, date_str, md_content):
    """生成完整的 HTML 页面"""
    
    # 读取模板
    with open('template-v2.html', 'r', encoding='utf-8') as f:
        template = f.read()
    
    # 解析 markdown 并转换为 HTML
    html_content = parse_markdown_sections(md_content)
    
    # 替换占位符
    html = template.replace('{{TITLE}}', title)
    html = html.replace('{{DATE}}', date_str)
    html = html.replace('{{CONTENT}}', html_content)
    
    # 保存文件
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 已生成网页版日报: index.html")
    print(f"   标题: {title}")
    print(f"   日期: {date_str}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 generate-v2.py <markdown文件>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    today = datetime.now()
    date_str = f"{today.year}年{today.month}月{today.day}日 星期{['一','二','三','四','五','六','日'][today.weekday()]}"
    title = f"每日早报 | {date_str}"
    
    generate_html(title, date_str, md_content)
