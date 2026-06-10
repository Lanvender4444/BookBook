import uuid
import json
import re
import io
import tempfile
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from models import Book
from config import BOOKS_DIR, ensure_books_dir

def sanitize_filename(name: str) -> str:
    """清理文件名，移除非法字符"""
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = name.strip()[:100]  # 限制长度
    return name if name else "untitled"

def get_book_filepath(book_id: str, title: str) -> Path:
    """获取书籍文件保存路径"""
    ensure_books_dir()
    safe_title = sanitize_filename(title)
    filename = f"{book_id}_{safe_title}.md"
    return Path(BOOKS_DIR) / filename

def save_book(db: Session, outline: dict, chapters: list, user_id: str, language: str = "zh-CN") -> str:
    """保存书籍到本地文件和数据库"""
    book_id = str(uuid.uuid4())  # 完整 UUID
    
    # 生成 Markdown 内容
    md_content = f"# {outline['title']}\n\n"
    md_content += f"{outline['description']}\n\n---\n\n"
    
    for i, (chapter_data, content) in enumerate(zip(outline['chapters'], chapters)):
        md_content += f"## 第{i+1}章：{chapter_data['title']}\n\n{content}\n\n"
    
    # 保存到本地文件
    filepath = get_book_filepath(book_id, outline['title'])
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    # 保存到数据库
    book = Book(
        id=book_id,
        title=outline['title'],
        description=outline['description'],
        outline=outline,
        file_path=str(filepath),
        author_id=user_id,
        source="local",
        language=language
    )
    db.add(book)
    db.commit()
    
    return book_id

def save_book_sync(db: Session, outline: dict, chapters: list, user_id: str, language: str = "zh-CN") -> str:
    """同步版本的书籍保存，用于后台线程"""
    book_id = str(uuid.uuid4())  # 完整 UUID
    
    # 生成 Markdown 内容
    md_content = f"# {outline['title']}\n\n"
    md_content += f"{outline['description']}\n\n---\n\n"
    
    for i, (chapter_data, content) in enumerate(zip(outline['chapters'], chapters)):
        md_content += f"## 第{i+1}章：{chapter_data['title']}\n\n{content}\n\n"
    
    # 保存到本地文件
    filepath = get_book_filepath(book_id, outline['title'])
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    # 保存到数据库
    book = Book(
        id=book_id,
        title=outline['title'],
        description=outline['description'],
        outline=outline,
        file_path=str(filepath),
        author_id=user_id,
        source="local",
        language=language
    )
    db.add(book)
    db.commit()
    
    return book_id

def save_p2p_book(db: Session, book_data: dict, peer_id: str) -> str:
    """保存 P2P 接收的书籍"""
    book_id = book_data['id']
    
    # 生成 Markdown 内容
    md_content = f"# {book_data['title']}\n\n"
    md_content += f"{book_data['description']}\n\n---\n\n"
    
    for ch in book_data.get('chapters', []):
        md_content += f"## {ch['title']}\n\n{ch['content']}\n\n"
    
    # 保存到本地文件
    filepath = get_book_filepath(book_id, book_data['title'])
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    # 保存到数据库
    book = Book(
        id=book_id,
        title=book_data['title'],
        description=book_data['description'],
        outline=book_data.get('outline', {}),
        file_path=str(filepath),
        source="p2p",
        peer_origin=peer_id,
        language=book_data.get('language')
    )
    db.add(book)
    db.commit()
    
    return book_id

def get_book(db: Session, book_id: str):
    return db.query(Book).filter(Book.id == book_id).first()

def get_all_books(db: Session):
    return db.query(Book).order_by(Book.created_at.desc()).all()

def delete_book(db: Session, book_id: str) -> bool:
    book = db.query(Book).filter(Book.id == book_id).first()
    if book:
        # 删除本地文件
        filepath = Path(book.file_path)
        if filepath.exists():
            filepath.unlink()
        
        db.delete(book)
        db.commit()
        return True
    return False

def get_book_content(db: Session, book_id: str) -> str:
    """读取书籍文件内容"""
    book = get_book(db, book_id)
    if not book:
        return None
    
    filepath = Path(book.file_path)
    if not filepath.exists():
        return None
    
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def get_book_chapters(db: Session, book_id: str) -> list:
    """从 Markdown 内容解析章节"""
    content = get_book_content(db, book_id)
    if not content:
        return []
    
    chapters = []
    # 按 ## 分割章节
    parts = re.split(r'\n## ', content)
    
    for i, part in enumerate(parts):
        if i == 0:
            continue  # 跳过标题部分
        
        lines = part.strip().split('\n', 1)
        title = lines[0].strip()
        chapter_content = lines[1].strip() if len(lines) > 1 else ""
        
        # 移除章节标题中的"第X章："前缀
        title = re.sub(r'^第\d+章：?', '', title).strip()
        
        chapters.append({
            'index': i - 1,
            'title': title,
            'content': chapter_content
        })
    
    return chapters

def export_to_markdown(db: Session, book_id: str) -> str:
    """导出为 Markdown"""
    return get_book_content(db, book_id)

def _parse_chapters(md_content: str):
    """从 Markdown 内容解析出标题、描述和章节列表"""
    title = ""
    description = ""
    chapters = []

    chapter_parts = re.split(r'\n## ', md_content)

    for i, part in enumerate(chapter_parts):
        if i == 0:
            header_lines = part.strip().split('\n')
            for line in header_lines:
                if line.startswith('# '):
                    title = line[2:].strip()
                elif line.strip() and line.strip() != '---':
                    if not description:
                        description = line.strip()
                    else:
                        description += '\n' + line.strip()
        else:
            lines_text = part.strip().split('\n', 1)
            ch_title = lines_text[0].strip()
            ch_content = lines_text[1].strip() if len(lines_text) > 1 else ""
            ch_title = re.sub(r'^第\d+章：?', '', ch_title).strip()
            chapters.append({"title": ch_title, "content": ch_content})

    return title, description, chapters


def export_to_txt(md_content: str) -> bytes:
    """导出为纯文本，去除 Markdown 格式标记"""
    text = md_content
    text = re.sub(r'```[\s\S]*?```', lambda m: m.group(0).replace('```', '').strip('\n'), text)
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', text)
    text = re.sub(r'_{1,2}([^_]+)_{1,2}', r'\1', text)
    text = re.sub(r'~~([^~]+)~~', r'\1', text)
    text = re.sub(r'^\s*[-*+]\s+', '  - ', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '  ', text, flags=re.MULTILINE)
    text = re.sub(r'^---+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip().encode('utf-8')


def export_to_epub(md_content: str, title: str = "Book") -> bytes:
    """导出为 EPUB"""
    from ebooklib import epub

    book_title, description, chapters = _parse_chapters(md_content)
    if title and title != "Book":
        book_title = title

    book = epub.EpubBook()
    book.set_identifier(str(uuid.uuid4()))
    book.set_title(book_title)
    book.set_language('zh')
    book.add_author('AI eBook Generator')
    if description:
        book.add_metadata('DC', 'description', description)

    spine_items = ['nav']
    toc_items = []

    style = '''
    body { font-family: serif; line-height: 1.8; margin: 1em; }
    h1 { font-size: 1.6em; text-align: center; margin: 1.5em 0 0.8em; }
    h2 { font-size: 1.3em; margin: 1.2em 0 0.6em; border-bottom: 1px solid #ddd; padding-bottom: 0.3em; }
    h3 { font-size: 1.1em; margin: 1em 0 0.4em; }
    p { margin: 0.5em 0; text-indent: 2em; }
    pre { background: #f5f5f5; padding: 1em; overflow-x: auto; font-size: 0.85em; }
    code { background: #f5f5f5; padding: 0.1em 0.3em; font-size: 0.9em; }
    blockquote { border-left: 3px solid #ccc; margin: 0.5em 0; padding: 0.5em 1em; color: #555; }
    '''

    nav_css = epub.EpubItem(uid='style_nav', file_name='style/nav.css', media_type='text/css', content=style)
    book.add_item(nav_css)

    intro_html = f'''<html><body>
    <h1>{book_title}</h1>
    {'<p>' + description + '</p>' if description else ''}
    </body></html>'''
    intro = epub.EpubHtml(title=book_title, file_name='intro.xhtml', lang='zh')
    intro.content = intro_html
    intro.add_item(nav_css)
    book.add_item(intro)
    spine_items.append(intro)

    for i, ch in enumerate(chapters):
        ch_html_content = _markdown_to_simple_html(ch['content'])
        chapter = epub.EpubHtml(
            title=ch['title'],
            file_name=f'chapter_{i+1}.xhtml',
            lang='zh'
        )
        chapter.content = f'''<html><head><link rel="stylesheet" href="style/nav.css"/></head>
        <body><h2>{ch['title']}</h2>{ch_html_content}</body></html>'''
        chapter.add_item(nav_css)
        book.add_item(chapter)
        spine_items.append(chapter)
        toc_items.append(chapter)

    book.toc = toc_items
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = spine_items

    buffer = io.BytesIO()
    epub.write_epub(buffer, book)
    buffer.seek(0)
    return buffer.read()


def export_to_docx(md_content: str, title: str = "Book") -> bytes:
    """导出为 Word (.docx)"""
    from docx import Document
    from docx.shared import Pt, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    book_title, description, chapters = _parse_chapters(md_content)
    if title and title != "Book":
        book_title = title

    doc = Document()

    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)

    heading_style = doc.styles['Heading 1']
    heading_style.font.size = Pt(22)
    heading_style.font.bold = True

    heading2_style = doc.styles['Heading 2']
    heading2_style.font.size = Pt(16)
    heading2_style.font.bold = True

    doc.add_heading(book_title, level=1)

    if description:
        desc_para = doc.add_paragraph(description)
        desc_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        desc_para.style.font.size = Pt(11)

    doc.add_paragraph('')

    for ch in chapters:
        doc.add_heading(ch['title'], level=2)
        paragraphs = ch['content'].split('\n')
        for p_text in paragraphs:
            p_text = p_text.strip()
            if not p_text:
                continue
            if p_text.startswith('#'):
                level = len(p_text) - len(p_text.lstrip('#'))
                text = p_text.lstrip('#').strip()
                if level <= 3:
                    doc.add_heading(text, level=min(level, 2))
                else:
                    para = doc.add_paragraph()
                    run = para.add_run(text)
                    run.bold = True
            elif p_text.startswith('- ') or p_text.startswith('* '):
                items = []
                for line in paragraphs:
                    line = line.strip()
                    if line.startswith('- ') or line.startswith('* '):
                        items.append(line[2:])
                    elif line and not line.startswith('- ') and not line.startswith('* '):
                        break
                for item in items:
                    doc.add_paragraph(item, style='List Bullet')
                break
            elif p_text.startswith('```'):
                code_lines = []
                for line in paragraphs[paragraphs.index(p_text)+1:]:
                    if line.strip() == '```':
                        break
                    code_lines.append(line)
                if code_lines:
                    code_para = doc.add_paragraph('\n'.join(code_lines))
                    code_para.style.font.name = 'Courier New'
                    code_para.style.font.size = Pt(9)
            else:
                clean_text = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', p_text)
                clean_text = re.sub(r'_{1,2}([^_]+)_{1,2}', r'\1', clean_text)
                clean_text = re.sub(r'~~([^~]+)~~', r'\1', clean_text)
                clean_text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean_text)
                doc.add_paragraph(clean_text)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.read()


def export_to_pdf(md_content: str, title: str = "Book") -> bytes:
    """导出为 PDF（使用 weasyprint）"""
    from weasyprint import HTML

    book_title, description, chapters = _parse_chapters(md_content)
    if title and title != "Book":
        book_title = title

    html_parts = [f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<style>
  @page {{ margin: 2cm; size: A4; }}
  body {{ font-family: "Noto Sans SC", "Microsoft YaHei", "SimSun", "PingFang SC", sans-serif; line-height: 1.8; color: #333; font-size: 14px; }}
  h1 {{ font-size: 24px; text-align: center; margin: 2em 0 1em; border-bottom: 2px solid #333; padding-bottom: 0.5em; }}
  h2 {{ font-size: 18px; margin: 1.5em 0 0.8em; border-bottom: 1px solid #ccc; padding-bottom: 0.3em; page-break-before: always; }}
  h3 {{ font-size: 16px; margin: 1em 0 0.5em; }}
  h2:first-of-type {{ page-break-before: auto; }}
  p {{ margin: 0.5em 0; text-indent: 2em; }}
  .description {{ text-align: center; color: #666; margin: 1em 0 2em; }}
  pre {{ background: #f5f5f5; padding: 1em; overflow-x: auto; font-size: 12px; }}
  code {{ background: #f5f5f5; padding: 0.2em 0.4em; font-size: 0.9em; }}
  blockquote {{ border-left: 3px solid #ccc; margin: 0.5em 0; padding: 0.5em 1em; color: #555; }}
  strong {{ font-weight: bold; }}
  em {{ font-style: italic; }}
</style>
</head>
<body>
<h1>{book_title}</h1>''']

    if description:
        html_parts.append(f'<p class="description">{description}</p>')

    html_parts.append(_markdown_to_full_html(md_content))

    html_parts.append('</body></html>')

    full_html = '\n'.join(html_parts)

    pdf_bytes = HTML(string=full_html).write_pdf()
    return pdf_bytes


def _markdown_to_simple_html(md_text: str) -> str:
    """将 Markdown 章节内容转为简单 HTML（用于 EPUB 章节体）"""
    html = md_text
    html = re.sub(r'```(\w*)\n([\s\S]*?)```', r'<pre><code>\2</code></pre>', html)
    html = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'', html)
    html = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', html)
    html = re.sub(r'^####\s+(.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^##\s+(.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^#\s+(.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^\*\s+(.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'^-\s+(.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'^>\s+(.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)
    html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', html)
    html = re.sub(r'~~([^~]+)~~', r'<del>\1</del>', html)

    paragraphs = html.split('\n\n')
    result = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if p.startswith('<h') or p.startswith('<pre') or p.startswith('<li') or p.startswith('<blockquote'):
            result.append(p)
        else:
            lines = p.split('\n')
            processed = []
            for line in lines:
                line = line.strip()
                if line:
                    processed.append(line)
            if processed:
                result.append('<p>' + ' '.join(processed) + '</p>')

    return '\n'.join(result)


def _markdown_to_full_html(md_text: str) -> str:
    """将完整 Markdown 内容转为带章节的 HTML（用于 PDF）"""
    html_parts = []
    parts = re.split(r'\n## ', md_text)

    for i, part in enumerate(parts):
        if i == 0:
            continue

        lines = part.strip().split('\n', 1)
        ch_title = lines[0].strip()
        ch_title = re.sub(r'^第\d+章：?', '', ch_title).strip()
        ch_content = lines[1].strip() if len(lines) > 1 else ""
        ch_html = _markdown_to_simple_html(ch_content)
        html_parts.append(f'<h2>{ch_title}</h2>\n{ch_html}')

    return '\n'.join(html_parts)


def update_books_dir(new_dir: str):
    """更新书籍保存目录"""
    import os
    os.environ['BOOKS_DIR'] = new_dir
    ensure_books_dir()
