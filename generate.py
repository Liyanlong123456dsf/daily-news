#!/usr/bin/env python3
"""生成网页版每日早报"""
import sys
import re
from datetime import datetime
import markdown

def generate_html(title, date_str, md_content):
    # 读取模板
    with open('template.html', 'r', encoding='utf-8') as f:
        template = f.read()

    # 将 markdown 转换为 HTML
    md = markdown.Markdown(extensions=['tables', 'fenced_code'])
    html_content = md.convert(md_content)

    # 后处理：给新闻列表添加卡片样式
    # 把 ol > li 转换为卡片
    html_content = re.sub(
        r'<li>\s*<strong>([^<]+)</strong>\s*—\s*(.+?)</li>',
        r'<li class="news-card"><h3>\1</h3><p>\2</p></li>',
        html_content,
        flags=re.DOTALL
    )

    # GitHub 热榜样式化
    html_content = re.sub(
        r'<li>\s*<strong>([^<]+)</strong>\s*—\s*([0-9.]+k\+?)\s*⭐\s*(.*?)</li>',
        r'<li class="github-item"><svg class="github-icon" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg><div><a href="https://github.com/\1" target="_blank" class="text-blue-600 font-semibold hover:underline">\1</a><p class="text-sm text-gray-600 mt-1">\2 ⭐ \3</p></div></li>',
        html_content
    )

    # 替换占位符
    html = template.replace('{{TITLE}}', title)
    html = html.replace('{{DATE}}', date_str)
    html = html.replace('{{CONTENT}}', html_content)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"已生成 index.html - {title}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 generate.py <markdown文件>")
        sys.exit(1)

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        md_content = f.read()

    today = datetime.now().strftime('%Y年%m月%d日')
    title = f"每日早报 | {today}"
    generate_html(title, today, md_content)
