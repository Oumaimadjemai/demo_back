# utils/barcode_svg.py
import barcode
from barcode.writer import SVGWriter
import io
import re

def generate_custom_ean13_svg(code13: str, product_name: str, store_name: str) -> bytes:
    if len(code13) != 13 or not code13.isdigit():
        raise ValueError("Le code EAN13 doit contenir 13 chiffres.")

    # Step 1: Generate base barcode SVG
    ean = barcode.get_barcode_class('ean13')
    ean_barcode = ean(code13, writer=SVGWriter())
    buffer = io.BytesIO()
    ean_barcode.write(buffer, options={
        "module_width": 0.4,
        "module_height": 15,
        "font_size": 10,
        "text_distance": 1.0,
    })
    svg_content = buffer.getvalue().decode("utf-8")

    # Step 2: Clean SVG
    # Remove XML declaration and outer <svg>
    svg_content = re.sub(r'<\?xml.*?\?>', '', svg_content, flags=re.DOTALL)
    svg_content = re.sub(r'<!DOCTYPE[^>]*>', '', svg_content, flags=re.DOTALL)
    svg_content = re.sub(r'</?svg[^>]*>', '', svg_content, flags=re.DOTALL)
    # Remove namespace prefixes like ns0:
    svg_content = re.sub(r'\bns\d+:', '', svg_content)
    svg_content = svg_content.strip()

    # Step 3: Combine into one valid SVG
    svg_template = f"""<svg xmlns="http://www.w3.org/2000/svg" width="220" height="130">
<text x="50%" y="18" font-size="14" text-anchor="middle" font-family="Arial">{store_name}</text>
<text x="50%" y="35" font-size="12" text-anchor="middle" font-family="Arial">{product_name}</text>
<g transform="translate(10,45)">
{svg_content}
</g>
</svg>"""

    return svg_template.encode("utf-8")
