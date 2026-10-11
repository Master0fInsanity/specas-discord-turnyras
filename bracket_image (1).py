"""Generate a SPECAS.LT tournament bracket image from published Firestore data."""
import io
import json
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

PROJECT = 'specas-deagle-turnyras'
URL = f'https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents/tournaments/deagle1v1'
BASE = Path(__file__).resolve().parent
FONT_LOCATIONS = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    'C:/Windows/Fonts/arial.ttf',
]


def font(size, bold=False):
    candidates = ([FONT_LOCATIONS[1]] if bold else []) + FONT_LOCATIONS
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def fit_name(draw, name, font_obj, max_width):
    name = str(name or 'Laukiama')
    while name and draw.textbbox((0, 0), name, font=font_obj)[2] > max_width:
        name = name[:-1]
    return name if name else '…'


def main():
    r = requests.get(URL, timeout=25)
    r.raise_for_status()
    fields = r.json()['fields']
    rounds = json.loads(fields['publishedBracket']['stringValue'])
    confirmations = json.loads(fields.get('confirmed', {}).get('stringValue', '[]'))

    w, h = 1920, 1080
    bg_path = BASE / 'background.png'
    if not bg_path.exists():
        raise FileNotFoundError('Ikeltas background.png nerastas GitHub projekto pagrindiniame aplanke')
    image = ImageOps.fit(Image.open(bg_path).convert('RGB'), (w, h), method=Image.Resampling.LANCZOS)
    overlay = Image.new('RGBA', (w, h), (8, 11, 19, 105))
    image = Image.alpha_composite(image.convert('RGBA'), overlay)
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((42, 22, 1878, 132), radius=22, fill=(8, 12, 22, 202))
    draw.text((76, 44), 'SPECAS.LT  |  DEAGLE 1V1', font=font(43, True), fill='white')
    draw.text((79, 101), 'TURNYRO LENTELE  •  PATVIRTINTI REZULTATAI', font=font(17), fill='#e8c58a')

    headings = ['AŠTUNTFINALIS', 'KETVIRTFINALIS', 'PUSFINALIS', 'FINALAS']
    xs = [50, 520, 990, 1460]
    card_w, card_h = 410, 78
    area_top, area_bottom = 225, 995
    center_y = []
    for ridx, count in enumerate((8, 4, 2, 1)):
        centers = [area_top + (i + 0.5) * (area_bottom - area_top) / count for i in range(count)]
        center_y.append(centers)
        draw.text((xs[ridx], 169), headings[ridx], font=font(24, True), fill='#f8d19b')

    # Connecting lines are drawn first, so they stay behind the cards.
    for ridx in range(3):
        for i, cy in enumerate(center_y[ridx]):
            if i >= len(center_y[ridx + 1]) * 2:
                continue
            target = center_y[ridx + 1][i // 2]
            x0, x1 = xs[ridx] + card_w, xs[ridx + 1]
            mid = (x0 + x1) // 2
            draw.line([(x0, cy), (mid, cy), (mid, target), (x1, target)], fill=(230, 195, 139, 175), width=3)

    for ridx, matches in enumerate(rounds[:4]):
        for midx, match in enumerate(matches[:len(center_y[ridx])]):
            if not isinstance(match, list) or len(match) < 2:
                continue
            x = xs[ridx]
            y = int(center_y[ridx][midx] - card_h / 2)
            # Composite the translucent card on top of the background.
            card_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            card_draw = ImageDraw.Draw(card_layer)
            card_draw.rounded_rectangle(
                (x, y, x + card_w, y + card_h), radius=11,
                fill=(12, 17, 29, 125), outline=(226, 193, 137, 185), width=2
            )
            image = Image.alpha_composite(image, card_layer)
            draw = ImageDraw.Draw(image)
            confirmed = (ridx < len(confirmations) and isinstance(confirmations[ridx], list)
                         and midx < len(confirmations[ridx]) and confirmations[ridx][midx] is True)
            scores = []
            for pidx, player in enumerate(match[:2]):
                player = player if isinstance(player, dict) else {}
                name = player.get('name') or 'Laukiama'
                score = player.get('score', '')
                scores.append(score)
                yy = y + 10 + pidx * 35
                draw.text((x + 15, yy), fit_name(draw, name, font(22, True), card_w - 100), font=font(22, True), fill='#ffffff')
                draw.text((x + card_w - 51, yy), str(score) if score != '' else '–', font=font(22, True), fill='#ffffff')
            if confirmed:
                try:
                    a, b = float(scores[0]), float(scores[1])
                    if a != b:
                        winner_row = 0 if a > b else 1
                        yy = y + 10 + winner_row * 35
                        draw.rounded_rectangle((x + card_w - 66, yy - 2, x + card_w - 12, yy + 30), radius=7, outline='#ffd36b', width=2)
                except (ValueError, TypeError):
                    pass

    draw.rounded_rectangle((45, 1010, 1875, 1064), radius=12, fill=(9, 13, 22, 205))
    draw.text((70, 1026), 'Pilna turnyro lentele: specas-deagle-turnyras.web.app', font=font(22), fill='white')
    output = BASE / 'turnyro_lentele.png'
    image.convert('RGB').save(output, optimize=True)
    print(f'Sugeneruota: {output.name}')


if __name__ == '__main__':
    main()
