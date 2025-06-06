import os
import base64
from io import BytesIO
from docx import Document
from django.conf import settings
from django.utils.html import escape
from docx.oxml.ns import nsdecls

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
        indent = para.paragraph_format.left_indent
        indent_px = int(indent.pt) if indent else 0
        style = f"padding-left: {indent_px}px;" if indent_px > 0 else ""
        p_html = f'<p style="{style}">'

        for run in para.runs:
            text = escape(run.text)
            if run.bold:
                text = f'<strong>{text}</strong>'
            if run.italic:
                text = f'<em>{text}</em>'
            if run.underline:
                text = f'<u>{text}</u>'
            if run.font.color and run.font.color.rgb:
                text = f'<span style="color: #{run.font.color.rgb}">{text}</span>'
            if run.font.size:
                size_pt = run.font.size.pt
                text = f'<span style="font-size: {size_pt}pt;">{text}</span>'

            for pic in run._element.findall(".//pic:pic", namespaces=pic_namespace):
                blip = pic.find(".//a:blip", namespaces=a_namespace)
                if blip is not None:
                    rId = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                    img_src = image_map.get(rId, '')
                    if img_src:
                        text += f'<img src="{img_src}" style="max-width:100%; margin: 5px 0;" />'

            p_html += text
        p_html += '</p>'
        html += p_html

    return html
