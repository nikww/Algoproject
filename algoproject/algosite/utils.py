import os
import base64
from io import BytesIO
from docx import Document
from django.utils.html import escape


def process_whitespace_indent(text):
    leading_spaces = len(text) - len(text.lstrip(' '))
    leading_tabs = len(text) - len(text.lstrip('\t'))

    indent_px = (leading_spaces * 5) + (leading_tabs * 40)
    return f'margin-left: {indent_px}px;' if indent_px > 0 else ''


def docx_bin_to_html(docx_binary):
    document = Document(BytesIO(docx_binary))
    rels = document.part.rels
    image_map = {}

    for rel in rels.values():
        if "image" in rel.reltype:
            image_bytes = rel.target_part.blob
            b64 = base64.b64encode(image_bytes).decode('utf-8')
            mime_type = 'image/png'
            image_map[rel.rId] = f"data:{mime_type};base64,{b64}"

    html = ''
    pic_namespace = {'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture'}
    a_namespace = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}

    for para in document.paragraphs:
        p_style = []

        pf = para.paragraph_format

        # Process official indent properties
        if pf.left_indent is not None:
            left_pt = pf.left_indent.pt
            p_style.append(f"margin-left: {left_pt}pt;")

        if pf.first_line_indent is not None:
            indent_pt = pf.first_line_indent.pt
            p_style.append(f"text-indent: {indent_pt}pt;")

        if pf.right_indent is not None:
            right_pt = pf.right_indent.pt
            p_style.append(f"margin-right: {right_pt}pt;")


        alignment_map = {
            0: "left",
            1: "center",
            2: "right",
            3: "justify"
        }
        if pf.alignment is not None and pf.alignment in alignment_map:
            p_style.append(f"text-align: {alignment_map[pf.alignment]};")

        whitespace_style = process_whitespace_indent(para.text)
        if whitespace_style:
            p_style.append(whitespace_style)

        style_attr = f' style="{" ".join(p_style)}"' if p_style else ""
        p_html = f'<p{style_attr}>'


        for run in para.runs:
            text = escape(run.text) if run.text else ""
            run_html = text

            if run.bold:
                run_html = f'<strong>{run_html}</strong>'
            if run.italic:
                run_html = f'<em>{run_html}</em>'
            if run.underline:
                run_html = f'<u>{run_html}</u>'

            if run.font.color and run.font.color.rgb:
                run_html = f'<span style="color:#{run.font.color.rgb}">{run_html}</span>'

            if run.font.size:
                size_pt = run.font.size.pt
                run_html = f'<span style="font-size:{size_pt}pt">{run_html}</span>'

            for pic in run._element.findall(".//pic:pic", namespaces=pic_namespace):
                blip = pic.find(".//a:blip", namespaces=a_namespace)
                if blip is not None:
                    rId = blip.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
                    img_src = image_map.get(rId, "")
                    if img_src:
                        run_html += f'<img src="{img_src}" style="display:block; max-width:100%; margin:5px 0;"/>'

            p_html += run_html

        p_html += "</p>"
        html += p_html
    return ''.join(html)