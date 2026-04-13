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
            i += 1
            continue
        
        # 处理新闻列表项
        news_match = re.match(r'^(\d+)\.\s*\*\*\[(.+?)\]\((.+?)\)\*\*\s*—\s*(.+)$', line)
        if news_match:
            if not in_news_list:
                html_parts.append('<div class="news-list">')
                in_news_list = True
            
            number = news_match.group(1)
            title = news_match.group(2)
            link = news_match.group(3)
            summary = news_match.group(4)
            
            html_parts.append(f'''
<div class="news-card">
    <div class="news-number">{number}</div>
    <h3 class="news-title"><a href="{link}" target="_blank">{title}</a></h3>
    <p class="news-summary">{summary}</p>
</div>
''')
            i += 1
            continue
        
        # 处理 GitHub 热榜项
        github_match = re.match(r'^-\s*\*\*\[(.+?)\]\((.+?)\)\*\*\s*—\s*(.+)$', line)
        if github_match and ("热榜" in current_section or "GitHub" in current_section):
            if not in_github_list:
                html_parts.append('<div class="github-list">')
                in_github_list = True
            
            repo_name = github_match.group(1)
            repo_link = github_match.group(2)
            desc_text = github_match.group(3)
            
            # 提取 star 数和描述
            star_match = re.search(r'(\d+\.?\d*k?\+?)\s*⭐', desc_text)
            stars = star_match.group(1) if star_match else ""
            
            # 清理描述文本
            desc = re.sub(r'\s*[⭐\d\.]\+?\s*⭐?.*?https?://\S+', '', desc_text).strip()
            
            html_parts.append(f'''
<div class="github-item">
    <div class="github-icon">
        <svg viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
    </div>
    <div class="github-content">
        <div class="github-name"><a href="{repo_link}" target="_blank">{repo_name}</a></div>
        <div class="github-desc">{desc}</div>
        <div class="github-stats">
            <span class="github-stars">⭐ {stars}</span>
        </div>
    </div>
</div>
''')
            i += 1
            continue
        
        # 处理趋势观察
        if line.startswith('### ') and ("趋势" in line or "观察" in line):
            if not in_trend_box:
                subsection_title = line[4:].strip()
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
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('#') and not lines[i].strip().startswith('---'):
                if lines[i].strip():
                    trend_content.append(lines[i].strip())
                i += 1
            
            if trend_content:
                html_parts.append('<p>' + ' '.join(trend_content) + '</p>')
            html_parts.append('</div></div>')
            in_trend_box = False
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
