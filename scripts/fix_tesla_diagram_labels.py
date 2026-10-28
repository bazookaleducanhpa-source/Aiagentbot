from pathlib import Path
file=Path(__file__).resolve().parents[1]/'output/tesla-cappy-skillry-v3/src/Diagrams.tsx'
text=file.read_text(encoding='utf-8')
for old,new in [('VÒOI PHÚT','VÒI PHỤT'),('KHÍ PHÚT RA','KHÍ PHỤT RA'),('KHÔNG GIAN THÍNG CÓ KIÌM SOÁT','KHÔNG GIAN THỬ CÓ KIỂM SOÁT')]:
    text=text.replace(old,new)
file.write_text(text,encoding='utf-8')
