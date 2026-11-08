"""Draws the research charts as static SVG, one light and one dark file each.
Run: python3 docs/research/make_charts.py  (data below is the measured runs of 2026-11-08)."""
import math, os

OUT = os.path.dirname(os.path.abspath(__file__))
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
THEME = {
    'light': dict(ink='#1f2328', muted='#59636e', grid='#d1d9e0', solo='#2a78d6', split='#eb6834', open='#eb6834', work='#1baf7a'),
    'dark': dict(ink='#e6edf3', muted='#9198a1', grid='#3d444d', solo='#3987e5', split='#d95926', open='#d95926', work='#199e70'),
}
W = 760

TASKS = ['small\nresumir arquivos', 'medium\n3 módulos', 'large\nrápido', 'large\npesquisa', 'large\nfeature', 'large\ndo zero']
USD = ([0.10, 0.21, 0.54, 0.94, 0.89, 1.16], [1.97, 2.20, 1.69, 2.90, 1.78, 4.46])
SECS = ([12, 43, 119, 188, 186, 278], [15, 39, 122, 179, 121, 452])


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def text(x, y, s, fill, size=12, anchor='start', weight=400):
    return f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{esc(s)}</text>'


def bar(x, y, w, h, fill):
    # Rounded only at the data end (the top), square on the baseline.
    r = min(4, w / 2, h)
    if h <= 0:
        return ''
    return (f'<path d="M{x:.1f} {y + h:.1f}V{y + r:.1f}Q{x:.1f} {y:.1f} {x + r:.1f} {y:.1f}'
            f'H{x + w - r:.1f}Q{x + w:.1f} {y:.1f} {x + w:.1f} {y + r:.1f}V{y + h:.1f}Z" fill="{fill}"/>')


def hbar(x, y, w, h, fill, round_end=True):
    r = min(4, h / 2, w) if round_end else 0
    if w <= 0:
        return ''
    return (f'<path d="M{x:.1f} {y:.1f}H{x + w - r:.1f}Q{x + w:.1f} {y:.1f} {x + w:.1f} {y + r:.1f}'
            f'V{y + h - r:.1f}Q{x + w:.1f} {y + h:.1f} {x + w - r:.1f} {y + h:.1f}H{x:.1f}Z" fill="{fill}"/>')


def legend(t, x, y, items):
    out, cx = [], x
    for label, color in items:
        out.append(f'<rect x="{cx}" y="{y - 9}" width="10" height="10" rx="2" fill="{color}"/>')
        out.append(text(cx + 15, y, label, t['ink'], 12))
        cx += 25 + len(label) * 6.6
    return ''.join(out)


def svg(h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img">'
            f'<title>{esc(title)}</title>{body}</svg>')


def grouped(t, title, subtitle, values, fmt, ticks, unit_label, height=366):
    left, right, top, bottom = 56, 16, 100, 52
    ph = height - top - bottom
    pw = W - left - right
    top_v = ticks[-1]
    y = lambda v: top + ph - v / top_v * ph
    out = [text(0, 20, title, t['ink'], 16, weight=600), text(0, 40, subtitle, t['muted'], 12),
           legend(t, 0, 62, [('Sozinha', t['solo']), ('Com 3 subagentes', t['split'])])]
    for v in ticks:
        out.append(f'<line x1="{left}" x2="{W - right}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="{t["grid"]}" stroke-width="1"/>')
        out.append(text(left - 8, y(v) + 4, fmt(v), t['muted'], 11, 'end'))
    out.append(text(0, top - 16, unit_label, t['muted'], 11))
    group = pw / len(TASKS)
    bw = min(26, group / 3.2)
    for i, name in enumerate(TASKS):
        cx = left + group * (i + 0.5)
        for j, (vals, color) in enumerate(((values[0], t['solo']), (values[1], t['split']))):
            v = vals[i]
            x = cx - bw - 1 + j * (bw + 2)
            out.append(bar(x, y(v), bw, top + ph - y(v), color))
            out.append(text(x + bw / 2, y(v) - 5, fmt(v), t['ink'], 10.5, 'middle'))
        for k, line in enumerate(name.split('\n')):
            out.append(text(cx, top + ph + 18 + k * 14, line, t['ink'] if k == 0 else t['muted'], 11.5 if k == 0 else 10.5, 'middle', 600 if k == 0 else 400))
    return svg(height, ''.join(out), title)


def cost(t):
    return grouped(t, 'Custo de cada tarefa', 'Mesmas 3 etapas, feitas sozinha e divididas. Dividir custou de 2 a 20 vezes mais em todas.',
                   USD, lambda v: f'${v:.2f}'.replace('.', ','), [0, 1, 2, 3, 4, 5], 'US$')


def time(t):
    return grouped(t, 'Tempo de relógio de cada tarefa', 'Com só 3 etapas em paralelo, dividir poupou no máximo 65 s, e numa delas atrasou.',
                   SECS, lambda v: f'{v:.0f}', [0, 100, 200, 300, 400, 500], 'segundos')


def anatomy(t):
    rows = [('small', 0.536, 0.100), ('medium', 0.552, 0.126), ('large, cache quente', 0.126, 0.435), ('large, cache frio', 0.552, 0.870)]
    h, left, top, rowh = 270, 150, 84, 40
    scale = (W - left - 170) / 1.5
    out = [text(0, 20, 'Para onde vai o dinheiro de um subagente', t['ink'], 16, weight=600),
           text(0, 40, 'Custo médio de um subagente: abrir (prompt de sistema e ferramentas, ~69 mil tokens) e trabalhar.', t['muted'], 12),
           legend(t, 0, 62, [('Abertura', t['open']), ('Trabalho', t['work'])])]
    for v in (0, 0.5, 1.0, 1.5):
        x = left + v * scale
        out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top - 8}" y2="{top + rowh * len(rows)}" stroke="{t["grid"]}" stroke-width="1"/>')
        out.append(text(x, top + rowh * len(rows) + 16, f'${v:.2f}'.replace('.', ','), t['muted'], 11, 'middle'))
    for i, (name, opening, work) in enumerate(rows):
        y = top + i * rowh
        out.append(text(left - 10, y + 17, name, t['ink'], 12, 'end'))
        wo = opening * scale
        out.append(hbar(left, y + 4, wo - 1, 20, t['open'], round_end=False))
        out.append(hbar(left + wo + 1, y + 4, work * scale - 1, 20, t['work']))
        share = round(opening / (opening + work) * 100)
        out.append(text(left + (opening + work) * scale + 8, y + 18, f'${opening + work:.2f}'.replace('.', ',') + f'  ·  abertura {share}%', t['ink'], 11.5))
    return svg(h, ''.join(out), 'Para onde vai o dinheiro de um subagente')


def requests(t):
    sizes = ['small', 'medium', 'large']
    solo, split = [0.67, 1.0, 2.6], [3.0, 2.7, 7.9]
    h, left, top, rowh = 250, 80, 84, 52
    scale = (W - left - 60) / 9
    out = [text(0, 20, 'Requisições por etapa', t['ink'], 16, weight=600),
           text(0, 40, 'Sozinha, a sessão já tem o contexto e escreve tudo de uma vez. O subagente começa do zero e explora.', t['muted'], 12),
           legend(t, 0, 62, [('Sozinha', t['solo']), ('Subagente', t['split'])])]
    for i, s in enumerate(sizes):
        y = top + i * rowh
        out.append(text(left - 10, y + 22, s, t['ink'], 12, 'end', 600))
        for j, (v, c) in enumerate(((solo[i], t['solo']), (split[i], t['split']))):
            yy = y + j * 20
            out.append(hbar(left, yy + 2, v * scale, 16, c))
            out.append(text(left + v * scale + 6, yy + 14, f'{v:.1f}'.replace('.', ','), t['ink'], 11.5))
    return svg(h, ''.join(out), 'Requisições por etapa')


def accuracy(t):
    versions = ['0.3.2', '0.4.0', '0.5.0']
    solo, split = [24.6, 3.0, 1.06], [8.4, 1.72, 1.14]
    h, left, right, top, bottom = 330, 56, 16, 74, 46
    ph, pw = h - top - bottom, W - left - right
    lo, hi = math.log10(0.5), math.log10(50)
    y = lambda v: top + ph - (math.log10(v) - lo) / (hi - lo) * ph
    out = [text(0, 20, 'Quantas vezes a estimativa errou o custo real (large)', t['ink'], 16, weight=600),
           text(0, 40, 'Escala logarítmica. A linha de 1× é o acerto exato; a faixa em volta dela é a margem de 15%.', t['muted'], 12),
           legend(t, 0, 62, [('Sozinha', t['solo']), ('Com subagentes', t['split'])])]
    out.append(f'<rect x="{left}" y="{y(1.15):.1f}" width="{pw}" height="{y(0.85) - y(1.15):.1f}" fill="{t["grid"]}" opacity="0.55"/>')
    for v in (0.5, 1, 2, 5, 10, 20, 50):
        out.append(f'<line x1="{left}" x2="{W - right}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="{t["grid"]}" stroke-width="{1.5 if v == 1 else 1}"/>')
        out.append(text(left - 8, y(v) + 4, f'{v:g}×'.replace('.', ','), t['ink'] if v == 1 else t['muted'], 11, 'end'))
    group = pw / 3
    bw = 34
    for i, ver in enumerate(versions):
        cx = left + group * (i + 0.5)
        for j, (v, c) in enumerate(((solo[i], t['solo']), (split[i], t['split']))):
            x = cx - bw - 2 + j * (bw + 4)
            top_y, base = (y(v), y(1)) if v >= 1 else (y(1), y(v))
            out.append(bar(x, top_y, bw, base - top_y, c) if v >= 1 else f'<rect x="{x}" y="{top_y:.1f}" width="{bw}" height="{base - top_y:.1f}" fill="{c}"/>')
            out.append(text(x + bw / 2, y(max(v, 1)) - 6, f'{v:.2g}×'.replace('.', ','), t['ink'], 11, 'middle', 600))
        out.append(text(cx, top + ph + 22, f'versão {ver}', t['ink'], 12, 'middle', 600))
    return svg(h, ''.join(out), 'Quantas vezes a estimativa errou o custo real')


for name, draw in (('cost', cost), ('time', time), ('anatomy', anatomy), ('requests', requests), ('accuracy', accuracy)):
    for mode, t in THEME.items():
        with open(os.path.join(OUT, f'{name}-{mode}.svg'), 'w') as f:
            f.write(draw(t))
print('ok')
