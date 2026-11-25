#!/usr/bin/env python3
"""generate_gallery_assets.py — aset gallery Gig 1 (3 PNG + HTML + PDF).

Jalankan: python3 generate_gallery_assets.py
Output (di folder yang sama dengan script ini):
  gig1-image-1.png, gig1-image-2.png, gig1-image-3.png  (tepat 1280x769)
  gig1-proofreading-sample.html                         (sumber PDF)
  sample-proofreading-change-log.pdf                    (tepat 3 halaman)

LibreOffice dipakai untuk HTML -> PDF. Teks pada gambar dan PDF
tidak boleh diubah; semua teks dideklarasikan konstan di bawah.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W, H = 1280, 769
MARGIN = 90

# --- Teks gambar (JANGAN DIUBAH; pecahan baris mempertahankan urutan kata) ---
IMG1_LINES = ["INDONESIAN PROOFREADING", "+ CONCISE CHANGE LOG"]
IMG2_LINES = ["TRAVEL & BUSINESS DOCS", "· ID + SIMPLE EN"]
IMG3_LINES = ["AI-ASSISTED.", "HUMAN-REVIEWED.", "YOU DECIDE."]

# --- Teks PDF (JANGAN DIUBAH) ---
HAL1 = [
    ("h1", "CONTOH HASIL PROOFREADING"),
    ("p", "Naskah rekaan: Panduan Paket Wisata"),
    ("p", "Bahasa: Indonesia (dengan penyesuaian istilah sederhana)"),
    ("p", "Lingkup: teks perjalanan dan dokumen bisnis"),
    ("p", "Alur: dibantu AI, ditinjau manusia, keputusan akhir di tangan Anda"),
    ("p", "Catatan: seluruh data pada contoh ini rekaan."),
    ("p", "Bukan dokumen klien, bukan data pribadi."),
]
HAL2_SEBELUM = (
    "Paket wisata ini meliputi tiket pesawat, hotel bintang tiga, "
    "dan juga makan pagi. Peserta diharapkan tiba di bandara 2 jam "
    "sebelum keberangkatan. Mohon bawa paspor yang masih berlaku "
    "min 6 bulan. Jika ada pertanyaan bisa hubungi kami lewat email."
)
HAL2_SESUDAH = (
    "Paket wisata ini meliputi tiket pesawat, hotel bintang tiga, "
    "dan sarapan. Peserta diharapkan tiba di bandara dua jam "
    "sebelum keberangkatan. Mohon membawa paspor yang masih berlaku "
    "minimal enam bulan. Jika ada pertanyaan, dapat menghubungi "
    "kami melalui email."
)
TABEL = [
    ("NO", "SEBELUM", "SESUDAH", "ALASAN"),
    ("1", "dan juga makan pagi", "dan sarapan", "Redundansi + konsistensi istilah"),
    ("2", "2 jam", "dua jam", "Ejaan angka konsisten"),
    ("3", "Mohon bawa", "Mohon membawa", "Register formal"),
    ("4", "min 6 bulan", "minimal enam bulan", "Singkatan dihindari + ejaan angka"),
    ("5", "pertanyaan bisa hubungi", "pertanyaan, dapat menghubungi", "Koma + pilihan kata formal"),
    ("6", "lewat email", "melalui email", "Register formal"),
]
HAL3_RINGKASAN = (
    "Ringkasan: 6 penyesuaian, fokus pada redundansi, ejaan angka, "
    "tanda baca, dan konsistensi register. Makna tidak diubah."
)


def fit_size(lines, font_path, max_w, max_h, start=96, min_size=32):
    """Ukuran font terbesar agar semua baris muat di lebar/tinggi maks."""
    size = start
    while size > min_size:
        font = ImageFont.truetype(font_path, size)
        probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
        widths = [probe.textlength(ln, font=font) for ln in lines]
        total_h = int(size * 1.35) * len(lines)
        if max(widths) <= max_w and total_h <= max_h:
            return size, font
        size -= 2
    raise SystemExit(f"GAGAL: teks tidak muat di {max_w}x{max_h}")


def draw_centered(draw, lines, font, cy, color):
    lh = int(font.size * 1.35)
    block_h = lh * len(lines)
    y = cy - block_h // 2
    for ln in lines:
        w = draw.textlength(ln, font=font)
        draw.text(((W - w) / 2, y), ln, font=font, fill=color)
        y += lh


def base_canvas(bg):
    img = Image.new("RGB", (W, H), bg)
    return img, ImageDraw.Draw(img)


def make_image1():
    img, d = base_canvas("#122A45")
    d.rectangle([0, 0, W, 14], fill="#37C9A3")
    d.rectangle([0, H - 14, W, H], fill="#37C9A3")
    size, font = fit_size(IMG1_LINES, FONT_BOLD, W - 2 * MARGIN, 320, start=88)
    draw_centered(d, IMG1_LINES, font, H // 2, "#FFFFFF")
    y = H // 2 + int(size * 1.35) * len(IMG1_LINES) // 2 + 46
    d.rectangle([(W - 260) // 2, y, (W + 260) // 2, y + 6], fill="#37C9A3")
    img.save(OUT / "gig1-image-1.png")
    return size


def make_image2():
    img, d = base_canvas("#F2F5F9")
    d.rectangle([0, 0, 14, H], fill="#E8734A")
    d.rectangle([0, H - 14, W, H], fill="#122A45")
    size, font = fit_size(IMG2_LINES, FONT_BOLD, W - 2 * MARGIN, 320, start=88)
    draw_centered(d, IMG2_LINES, font, H // 2, "#122A45")
    y = H // 2 + int(size * 1.35) * len(IMG2_LINES) // 2 + 46
    d.rectangle([(W - 260) // 2, y, (W + 260) // 2, y + 6], fill="#E8734A")
    img.save(OUT / "gig1-image-2.png")
    return size


def make_image3():
    img, d = base_canvas("#0E2E23")
    d.rectangle([0, 0, W, 14], fill="#F5C518")
    d.rectangle([0, H - 14, W, H], fill="#F5C518")
    size, font = fit_size(IMG3_LINES, FONT_BOLD, W - 2 * MARGIN, 420, start=96)
    draw_centered(d, IMG3_LINES, font, H // 2, "#FFFFFF")
    y = H // 2 + int(size * 1.35) * len(IMG3_LINES) // 2 + 46
    d.rectangle([(W - 260) // 2, y, (W + 260) // 2, y + 6], fill="#F5C518")
    img.save(OUT / "gig1-image-3.png")
    return size


def build_html() -> str:
    rows = []
    for i, row in enumerate(TABEL):
        tag = "th" if i == 0 else "td"
        cells = "".join(f'<{tag}>{c}</{tag}>' for c in row)
        rows.append(f"<tr>{cells}</tr>")
    tabel_html = '<table class="chg">' + "".join(rows) + "</table>"

    hal1_body = "".join(
        f'<{t}>{txt}</{t}>' if t == "h1" else f"<p>{txt}</p>" for t, txt in HAL1
    )
    return f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<title>Contoh Hasil Proofreading</title>
<style>
body {{ font-family: "DejaVu Sans", sans-serif; font-size: 12pt; color: #1a1a1a; }}
h1 {{ font-size: 20pt; color: #122A45; margin-bottom: 18pt; }}
h2 {{ font-size: 15pt; color: #122A45; margin-top: 14pt; margin-bottom: 6pt; }}
p {{ margin-top: 0; margin-bottom: 8pt; line-height: 1.4; }}
table.chg {{ border-collapse: collapse; width: 100%; font-size: 11pt; }}
table.chg th, table.chg td {{ border: 1px solid #666666; padding: 5pt 6pt; text-align: left; vertical-align: top; }}
table.chg th {{ background-color: #E8EDF3; color: #122A45; }}
</style>
</head>
<body>
<div>{hal1_body}</div>
<p style="page-break-before: always;"></p>
<div>
<h2>SEBELUM</h2>
<p>{HAL2_SEBELUM}</p>
<h2>SESUDAH</h2>
<p>{HAL2_SESUDAH}</p>
</div>
<p style="page-break-before: always;"></p>
<div>
{tabel_html}
<p>{HAL3_RINGKASAN}</p>
</div>
</body>
</html>
"""


def convert_pdf(html_path: Path) -> Path:
    pdf_from_html = html_path.with_suffix(".pdf")
    final = OUT / "sample-proofreading-change-log.pdf"
    if pdf_from_html.exists() and pdf_from_html != final:
        pdf_from_html.unlink()
    if final.exists():
        final.unlink()
    profile = "/tmp/opencode/lo_profile_gig1"
    cmd = [
        "libreoffice",
        f"-env:UserInstallation=file://{profile}",
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        str(OUT),
        str(html_path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if res.returncode != 0 or not pdf_from_html.exists():
        raise SystemExit(
            f"GAGAL konversi PDF (rc={res.returncode}): {res.stdout} {res.stderr}"
        )
    pdf_from_html.rename(final)
    return final


def pdf_pages(pdf_path: Path) -> int:
    out = subprocess.run(
        ["pdfinfo", str(pdf_path)], capture_output=True, text=True, check=True
    ).stdout
    for line in out.splitlines():
        if line.startswith("Pages:"):
            return int(line.split()[1])
    raise SystemExit("GAGAL: pdfinfo tidak mencantumkan Pages")


def verify_png(path: Path):
    from PIL import Image as Img

    with Img.open(path) as im:
        if im.size != (W, H):
            raise SystemExit(f"GAGAL: {path.name} ukuran {im.size}, harus ({W}, {H})")


def main() -> int:
    if shutil.which("libreoffice") is None or shutil.which("pdfinfo") is None:
        raise SystemExit("GAGAL: libreoffice/pdfinfo tidak ditemukan")

    sizes = [make_image1(), make_image2(), make_image3()]
    for n in (1, 2, 3):
        verify_png(OUT / f"gig1-image-{n}.png")

    html_path = OUT / "gig1-proofreading-sample.html"
    html_path.write_text(build_html(), encoding="utf-8")

    final = convert_pdf(html_path)
    pages = pdf_pages(final)
    if pages != 3:
        raise SystemExit(f"GAGAL: PDF {final.name} punya {pages} halaman, harus 3")

    if final.stat().st_size == 0 or html_path.stat().st_size == 0:
        raise SystemExit("GAGAL: ada output kosong")

    print("OK — semua aset tergenerasi:")
    for n in (1, 2, 3):
        print(f"  gig1-image-{n}.png  {W}x{H}  font={sizes[n - 1]}pt")
    print(f"  {html_path.name}  {html_path.stat().st_size} bytes")
    print(f"  {final.name}  {pages} halaman  {final.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
