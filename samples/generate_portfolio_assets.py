#!/usr/bin/env python3
"""Build the two portfolio covers and three-page reports, locally and repeatably.

Run: python3 generate_portfolio_assets.py
Use --sources-only to prepare HTML for review before PDF conversion.
All temporary conversion files remain inside the samples directory.
"""
from __future__ import annotations

import hashlib
import html
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
REG = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
NAVY, TEAL, ORANGE, GOLD, LIGHT = '#122A45', '#37C9A3', '#E8734A', '#F5C518', '#F2F5F9'
OLD = ('gig1-image-1.png', 'gig1-image-2.png', 'gig1-image-3.png',
       'sample-proofreading-change-log.pdf', 'generate_gallery_assets.py',
       'gig1-proofreading-sample.html')


def p(text, cls=''):
    return f'<p class="{cls}">{html.escape(text)}</p>'


def table(headers, rows, widths=None):
    cells = ''.join(f'<th bgcolor="#122A45" width="{widths[i]}%">{html.escape(h)}</th>' if widths else
                    f'<th bgcolor="#122A45">{html.escape(h)}</th>' for i, h in enumerate(headers))
    body = ''.join('<tr>' + ''.join(f'<td bgcolor="#F2F5F9">{html.escape(v)}</td>' for v in row) + '</tr>' for row in rows)
    return f'<table cellspacing="0" cellpadding="9"><thead><tr>{cells}</tr></thead><tbody>{body}</tbody></table>'


CSS = '''
@page { size: A4; margin: 18mm 17mm; }
body { font-family: "DejaVu Sans", sans-serif; font-size: 10pt; color: #122A45; line-height: 1.45; }
h1, h2, h3, p, td, th { font-family: "DejaVu Sans", sans-serif; }
h1 { font-size: 31pt; line-height: 1.15; margin-top: 18mm; margin-bottom: 6mm; }
h2 { font-size: 17pt; margin-top: 8mm; margin-bottom: 5mm; }
h3 { font-size: 11pt; color: #122A45; margin-top: 7mm; }
p { margin-top: 3mm; margin-bottom: 4mm; }
.eyebrow { font-size: 9pt; letter-spacing: 2pt; color: #167760; font-weight: bold; border-top: 5pt solid #37C9A3; padding-top: 5mm; }
.subtitle { font-size: 17pt; color: #526579; margin-bottom: 14mm; }
.notice { background: #F2F5F9; border-left: 4pt solid #E8734A; padding: 5mm; font-size: 9pt; }
.notice-title { font-size: 10pt; font-weight: bold; }
.meta { font-size: 9pt; margin-top: 10mm; }
.footer { font-size: 8pt; color: #526579; border-top: 1pt solid #dbe2ea; margin-top: 8mm; padding-top: 3mm; }
.page { page-break-before: always; }
pre { background: #F2F5F9; padding: 5mm; font-family: "DejaVu Sans", monospace; font-size: 10pt; line-height: 1.5; border-left: 3pt solid #37C9A3; }
table { border-collapse: collapse; width: 100%; font-size: 8pt; margin-top: 4mm; }
th { background: #122A45; color: #ffffff; text-align: left; font-size: 8pt; }
td { vertical-align: top; border-bottom: 1pt solid #dbe2ea; background: #F2F5F9; }
tr { page-break-inside: avoid; }
.qa table { font-size: 7.5pt; }
.qa th { font-size: 7.5pt; }
li { margin-bottom: 3mm; }
'''


def document(title, pages):
    # Writer's HTML importer honors a paragraph break, but ignores it on div.
    pages = [page.replace('<div class="page">', '<p style="page-break-before: always;"></p><div>')
             .replace('<div class="page qa">', '<p style="page-break-before: always;"></p><div class="qa">')
             for page in pages]
    return '<!DOCTYPE html>\n<html lang="id"><head><meta charset="utf-8">' + \
        f'<title>{html.escape(title)}</title><style>{CSS}</style></head><body>\n' + \
        '\n'.join(pages) + '\n</body></html>\n'


def cover_page(title, subtitle, disclaimer, metadata):
    return p('DOKUMEN CONTOH REKAAN', 'eyebrow') + f'<h1>{title}</h1>' + p(subtitle, 'subtitle') + \
        '<div class="notice">' + p('---------- DOKUMEN CONTOH REKAAN ----------', 'notice-title') + \
        p(disclaimer) + '</div><div class="meta">' + ''.join(p(t) for t in metadata) + \
        '</div>' + p('SAMPLE', 'footer')


def sources():
    cleanup = [cover_page('LAPORAN PEMBERSIHAN DATA CSV', 'Sebelum dan Sesudah',
        'Dibuat untuk ilustrasi saja. Bukan proyek klien nyata, bukan testimoni, dan bukan klaim hasil profit. Seluruh nilai, baris, dan nama kolom di dalam dokumen ini bersifat rekaan serta tidak merujuk pada pihak mana pun.',
        ['Layanan terkait : Proofreading Bahasa Indonesia dan English sederhana, dengan change log dan proses AI-assisted, human-reviewed.',
         'Jenis berkas    : Contoh laporan (PDF)',
         'Cakupan         : 3 halaman — Sampul / Sebelum-Sesudah / Ringkasan & Change Log'])]
    cleanup.append('<div class="page">' + p('SAMPLE', 'eyebrow') +
        '<h2>SEBELUM — potongan CSV mentah (rekaan)</h2>' +
        '<pre>id,nama,tanggal,jumlah\n1,Roti ,5/1/2024,12\n2, Teh,2024-1-7,8\n2, Teh,2024-1-7,8\n3,Kopi,07/02/2024,3.5</pre>' +
        '<h2>SESUDAH — hasil pembersihan (rekaan)</h2>' +
        '<pre>id,nama,tanggal,jumlah\n1,Roti,2024-01-05,12\n2,Teh,2024-01-07,8\n3,Kopi,2024-02-07,3.5</pre>' +
        '<h3>Penjelasan singkat:</h3><ul>' + ''.join('<li>' + t + '</li>' for t in [
            'Spasi di awal/akhir nilai teks dibuang agar seragam.',
            'Semua tanggal diseragamkan ke pola YYYY-MM-DD.',
            'Baris dengan id ganda (id 2) dihapus salah satu salinannya.',
            'Angka desimal tetap dipertahankan, hanya kerapian format yang dirapikan.']) + '</ul></div>')
    cleanup.append('<div class="page">' + p('SAMPLE', 'eyebrow') + '<h2>RINGKASAN</h2>' +
        p('Empat baris data mentah menjadi tiga baris data bersih. Empat jenis perbaikan dicatat: spasi, format tanggal, duplikasi, dan kerapian angka desimal. Tidak ada perubahan pada makna atau nilai asli data.') +
        '<h2>CHANGE LOG</h2>' + table(['No', 'Masalah pada data', 'Penyesuaian', 'Dampak'], [
            ['1', 'Spasi awal/akhir pada "Roti " dan " Teh"', 'Spasi dibuang', 'Nilai teks menjadi rapi'],
            ['2', 'Tanggal campuran (5/1/2024, 2024-1-7, 07/02/2024)', 'Diseragamkan ke YYYY-MM-DD', 'Urutan tanggal terbaca'],
            ['3', 'Baris duplikat dengan id 2', 'Salinan duplikat dihapus', 'Jumlah data berkurang satu'],
            ['4', 'Desimal "3.5" tidak seragam', 'Format desimal ditetapkan', 'Konsisten saat diimpor']], [6, 35, 30, 29]) +
        p('Catatan proses: dokumen rekaan ini disusun dengan bantuan alat (AI-assisted), lalu setiap perubahan diperiksa ulang secara manual (human-reviewed) untuk memastikan makna tidak berubah.') +
        p('Ulangi penegasan: ini contoh rekaan, bukan testimoni, bukan data klien, dan bukan klaim profit.', 'notice') + '</div>')
    qa = [cover_page('DAFTAR KASUS UJI IMPOR CSV', 'Dokumentasi QA untuk alur unggah data',
        'Dibuat untuk ilustrasi saja. Bukan proyek klien nyata, bukan testimoni, dan bukan klaim hasil profit. Seluruh ID, skenario, dan nilai di bawah ini bersifat rekaan serta tidak merujuk pada sistem atau pihak tertentu.',
        ['Layanan terkait : Proofreading dan QA dokumen, dengan change log dan proses AI-assisted, human-reviewed.',
         'Jenis berkas    : Contoh PDF (3 halaman — Sampul / Daftar Kasus / Ringkasan & Change Log)'])]
    qa.append('<div class="page qa">' + p('DOKUMEN CONTOH REKAAN', 'eyebrow') + table(
        ['ID', 'Skenario', 'Contoh Input (rekaan)', 'Hasil Diharapkan', 'Hasil Aktual', 'Status'], [
            ['TC-01', 'Kolom wajib kosong', 'nilai nama kosong', 'Baris ditolak, pesan jelas', 'Sesuai', 'Lulus'],
            ['TC-02', 'Urutan kolom tertukar', 'header dibalik', 'Impor gagal, petunjuk urutan', 'Sesuai', 'Lulus'],
            ['TC-03', 'Encoding berbeda', 'berkas non-UTF-8', 'Pesan encoding, tak lanjut', 'Kurang jelas', 'Perbaikan'],
            ['TC-04', 'Baris ganda', 'dua id sama', 'Duplikat terdeteksi, dilapor', 'Sesuai', 'Lulus'],
            ['TC-05', 'Koma di dalam teks', 'nilai "Kopi, hitam"', 'Dibaca sebagai satu nilai', 'Terpotong', 'Perbaikan']],
        [10, 18, 18, 25, 14, 15]) + '</div>')
    qa.append('<div class="page">' + p('SAMPLE', 'eyebrow') + '<h2>RINGKASAN</h2>' +
        p('Lima kasus diuji: tiga lulus, dua perlu tindak lanjut. Fokus perbaikan ada pada kejelasan pesan encoding dan penanganan koma di dalam nilai teks. Seluruh kasus merupakan contoh rekaan untuk keperluan ilustrasi.') +
        '<h2>CHANGE LOG</h2>' + table(['No', 'Temuan', 'Tindakan', 'Status'], [
            ['1', 'TC-03: pesan encoding sulit dipahami', 'Menambahkan contoh perbaikan ke dalam teks pesan', 'Terjadwal'],
            ['2', 'TC-05: nilai berkoma terpotong saat diimpor', 'Mengusulkan penanganan tanda kutip pada parser', 'Terjadwal']], [6, 34, 41, 19]) +
        p('Catatan proses: daftar kasus rekaan ini disusun dengan bantuan alat (AI-assisted), lalu setiap kasus ditelaah ulang secara manual (human-reviewed) agar logika dan bahasanya tetap jelas.') +
        p('Ulangi penegasan: ini contoh rekaan, bukan testimoni, bukan data klien, dan bukan klaim profit.', 'notice') + '</div>')
    return {'sample-csv-cleanup-report': document('LAPORAN PEMBERSIHAN DATA CSV', cleanup),
            'sample-csv-import-qa': document('DAFTAR KASUS UJI IMPOR CSV', qa)}


def draw_cover(name, lines, qa=False):
    # Render at double resolution for clean typography and geometric edges.
    scale = 2
    im = Image.new('RGB', (1280 * scale, 769 * scale), NAVY)
    d = ImageDraw.Draw(im)
    def box(xy, fill, radius=0, outline=None, width=1):
        xy = tuple(int(v * scale) for v in xy)
        d.rounded_rectangle(xy, radius=radius * scale, fill=fill, outline=outline, width=width * scale)
    def text(x, y, value, size, color, bold=True):
        font = ImageFont.truetype(BOLD if bold else REG, size * scale)
        assert x + d.textlength(value, font=font) / scale < 1250
        d.text((x * scale, y * scale), value, font=font, fill=color)
    box((0, 0, 1280, 12), TEAL)
    box((74, 83, 134, 89), TEAL)
    text(151, 69, 'SAMPLE', 20, TEAL)
    text(70, 188, lines[0], 55 if qa else 48, '#FFFFFF')
    text(70, 277, lines[1], 55, TEAL)
    box((73, 392, 143, 399), ORANGE)
    text(70, 438, lines[2], 36, '#FFFFFF')
    # A large paper sheet with grid cells makes the subject readable at a glance.
    box((853, 142, 1196, 629), '#203E5C', 20)
    box((830, 119, 1173, 606), LIGHT, 18)
    box((858, 151, 1145, 198), TEAL, 6)
    for row in range(5):
        y = 224 + row * 61
        box((858, y, 1145, y + 45), '#FFFFFF', 5)
        box((872, y + 16, 900, y + 28), '#B1C0CE', 3)
        box((915, y + 16, 1062, y + 24), '#D1DBE4', 3)
        color = ORANGE if qa and row in (2, 4) else '#17846B'
        if qa and row in (2, 4):
            box((1092, y + 10, 1100, y + 27), color, 2)
            box((1092, y + 31, 1100, y + 35), color, 2)
        else:
            pts = [(1081, y + 23), (1090, y + 31), (1108, y + 13)]
            d.line([(x * scale, z * scale) for x, z in pts], fill=color, width=5 * scale)
    box((74, 683, 1206, 685), '#365069')
    box((74, 684, 249, 688), TEAL)
    box((1134, 74, 1206, 80), GOLD)
    im.resize((1280, 769), Image.Resampling.LANCZOS).save(OUT / name)


def run(args, **kwargs):
    return subprocess.run(args, check=True, capture_output=True, text=True, timeout=180, **kwargs).stdout


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    before = {name: digest(OUT / name) for name in OLD}
    docs = sources()
    for stem, content in docs.items():
        (OUT / (stem + '.html')).write_text(content, encoding='utf-8')
    if '--sources-only' in sys.argv:
        print('HTML sources ready for guard and selfcheck.')
        return
    draw_cover('portfolio-csv-cover.png', ['CSV DATA CLEANUP', 'BEFORE + AFTER', 'SHORT REPORT'])
    draw_cover('portfolio-qa-cover.png', ['CSV IMPORT QA', 'TEST CASES', 'CHECK REPORT'], qa=True)
    # An isolated profile and HOME prevent writes outside the authorized folder.
    with tempfile.TemporaryDirectory(prefix='.portfolio-build-', dir=OUT) as tmp:
        env = dict(os.environ, HOME=tmp, TMPDIR=tmp, XDG_CACHE_HOME=tmp,
                   XDG_CONFIG_HOME=tmp, XDG_DATA_HOME=tmp)
        for stem in docs:
            source = OUT / (stem + '.html')
            run(['libreoffice', '-env:UserInstallation=' + Path(tmp, 'profile').as_uri(),
                 '--headless', '--convert-to', 'pdf:writer_pdf_Export', '--outdir', tmp, str(source)], env=env)
            generated = Path(tmp, stem + '.pdf')
            info = run(['pdfinfo', str(generated)])
            assert re.search(r'^Pages:\s+3\s*$', info, re.M), info
            pages = run(['pdftotext', '-layout', str(generated), '-']).split('\f')
            expected = (['LAPORAN PEMBERSIHAN', 'SEBELUM', 'CHANGE LOG'] if 'cleanup' in stem else
                        ['DAFTAR KASUS', 'TC-05', 'CHANGE LOG'])
            for page, keyword in zip(pages, expected):
                assert keyword in page, (stem, keyword, page)
            assert 'RINGKASAN' in pages[2] and 'human-reviewed' in pages[2]
            assert 'DOKUMEN CONTOH REKAAN' in pages[0]
            if 'cleanup' in stem:
                assert 'SESUDAH' in pages[1] and '2024-02-07' in pages[1]
            else:
                assert all(f'TC-{i:02}' in pages[1] for i in range(1, 6))
            generated.replace(OUT / generated.name)
            print(f'{generated.name}: 3 pages; per-page keywords verified')
    for name in ('portfolio-csv-cover.png', 'portfolio-qa-cover.png'):
        with Image.open(OUT / name) as image:
            assert image.size == (1280, 769)
            print(f'{name}: {image.size}')
    assert before == {name: digest(OUT / name) for name in OLD}, 'Old gallery assets changed'
    print('Old gallery SHA-256: unchanged')


if __name__ == '__main__':
    main()
