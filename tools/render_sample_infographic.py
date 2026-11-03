from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


FONT_PATHS = (
    Path(r"C:\Windows\Fonts\YuGothM.ttc"),
    Path(r"C:\Windows\Fonts\msgothic.ttc"),
)
NAVY = (23, 42, 64)
TEAL = (22, 105, 102)
MINT = (224, 242, 235)
CREAM = (250, 248, 242)
WHITE = (255, 255, 255)
INK = (34, 48, 58)
MUTED = (89, 107, 114)
GOLD = (207, 155, 72)
PALE = (239, 245, 241)


def font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_PATHS:
        if path.is_file():
            return ImageFont.truetype(str(path), size=size)
    raise FileNotFoundError("Japanese font not found; install or configure a Japanese TrueType font.")


def text_width(draw: ImageDraw.ImageDraw, value: str, selected_font: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), value, font=selected_font)
    return box[2] - box[0]


def paragraph(
    draw: ImageDraw.ImageDraw,
    value: str,
    origin: tuple[int, int],
    width: int,
    selected_font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int] = INK,
    line_gap: int = 10,
) -> int:
    x, y = origin
    line_height = selected_font.size + line_gap
    for paragraph_text in value.split("\n"):
        line = ""
        for character in paragraph_text:
            candidate = line + character
            if line and text_width(draw, candidate, selected_font) > width:
                draw.text((x, y), line, font=selected_font, fill=fill)
                y += line_height
                line = character
            else:
                line = candidate
        if line:
            draw.text((x, y), line, font=selected_font, fill=fill)
            y += line_height
    return y


def card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: tuple[int, int, int] = WHITE) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=28, fill=fill, outline=(222, 230, 226), width=2)
    draw.rounded_rectangle((x0 + 22, y0 + 22, x0 + 32, y0 + 76), radius=5, fill=TEAL)


def card_title(draw: ImageDraw.ImageDraw, x: int, y: int, value: str, color: tuple[int, int, int] = NAVY) -> None:
    draw.text((x, y), value, font=font(34), fill=color)


def contain(base: Image.Image, image_path: Path, box: tuple[int, int, int, int]) -> None:
    with Image.open(image_path) as opened:
        image = opened.convert("RGBA")
    x, y, width, height = box
    image.thumbnail((width, height), Image.Resampling.LANCZOS)
    base.alpha_composite(image, (x + (width - image.width) // 2, y + (height - image.height) // 2))


def make_logo(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGBA", (520, 116), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((2, 2, 518, 114), radius=24, fill=(23, 42, 64, 244))
    draw.text((24, 15), "HADA", font=font(48), fill=(255, 255, 255, 255))
    draw.text((205, 42), "CONTENT STUDIO", font=font(28), fill=(222, 242, 235, 255))
    image.save(path, format="PNG", optimize=False, compress_level=9)


def make_infographic(root: Path, output: Path) -> None:
    fullbody = root / "projects/fantasy/content-studio-feature-tour/productions/infographic/exports/cute-elf-fullbody-website.png"
    chibi = root / "projects/fantasy/content-studio-feature-tour/productions/infographic/exports/cute-elf-chibi-v2-website.png"
    for required in (fullbody, chibi):
        if not required.is_file():
            raise FileNotFoundError(f"Create the accepted, watermarked character derivative first: {required}")
    width, height = 1600, 2320
    canvas = Image.new("RGBA", (width, height), CREAM + (255,))
    draw = ImageDraw.Draw(canvas)

    draw.rectangle((0, 0, width, 306), fill=NAVY)
    draw.text((78, 42), "HADA CONTENT STUDIO  /  VERSION 0.1.0", font=font(24), fill=(179, 224, 210))
    draw.text((78, 88), "情報を、信頼できる", font=font(58), fill=WHITE)
    draw.text((78, 158), "一枚のインフォグラフィックへ", font=font(58), fill=WHITE)
    draw.text((82, 246), "知識・キャラクター・画像を、安全な制作フローにつなぐ", font=font(27), fill=(219, 231, 228))
    contain(canvas, chibi, (1292, 18, 250, 275))

    margin = 72
    gap = 30
    column = (width - margin * 2 - gap) // 2
    left_x = margin
    right_x = margin + column + gap

    card(draw, (left_x, 340, left_x + column, 680))
    card_title(draw, left_x + 54, 370, "01  分野ごとのミニプロジェクト")
    paragraph(draw, "高校入試、バイク、趣味。分野ごとに目的・対象・範囲を分け、広いテーマを小さな制作単位で見通します。", (left_x + 54, 438), column - 100, font(26))
    draw.rounded_rectangle((left_x + 54, 585, left_x + column - 38, 643), radius=18, fill=MINT)
    draw.text((left_x + 74, 599), "目的  /  読者  /  含める範囲  /  扱わない範囲", font=font(22), fill=TEAL)

    card(draw, (right_x, 340, right_x + column, 680))
    card_title(draw, right_x + 54, 370, "02  根拠のある知識を再利用")
    paragraph(draw, "事実・経験・判断を分け、出典と検証状態を記録。知識モジュールを複数のミニプロジェクトから参照できます。", (right_x + 54, 438), column - 100, font(26))
    draw.rounded_rectangle((right_x + 54, 585, right_x + column - 38, 643), radius=18, fill=PALE)
    draw.text((right_x + 74, 599), "出典  →  主張  →  確認  →  制作へ適用", font=font(23), fill=TEAL)

    card(draw, (margin, 712, width - margin, 1280))
    card_title(draw, margin + 54, 742, "03  同じキャラクター。変わる頭身。共有できるアイテム。")
    contain(canvas, fullbody, (margin + 44, 800, 300, 425))
    contain(canvas, chibi, (margin + 315, 842, 232, 343))
    draw.text((margin + 72, 1220), "基本の外見", font=font(22), fill=MUTED)
    draw.text((margin + 356, 1220), "ちびキャラ", font=font(22), fill=MUTED)
    info_x = margin + 590
    paragraph(draw, "同じ character_id のまま、頭身や画風を変更。耳・緑の瞳・髪色・葉の髪飾りを、人物を見分けるアンカーとして記録します。", (info_x, 820), 720, font(26))
    draw.line((info_x, 1005, width - margin - 46, 1005), fill=(221, 230, 225), width=2)
    paragraph(draw, "衣装・乗り物・武器は独立した Item に。1つの Item を複数キャラクターへリンクでき、衣装セットは Outfit として組み合わせられます。", (info_x, 1032), 720, font(26))
    draw.rounded_rectangle((info_x, 1160, width - margin - 44, 1236), radius=18, fill=MINT)
    draw.text((info_x + 22, 1177), "Character ID  ↔  Item ID  ↔  Character ID", font=font(25), fill=TEAL)

    card(draw, (margin, 1312, width - margin, 1660), fill=(246, 250, 247))
    card_title(draw, margin + 54, 1342, "04  プロンプトは層で組み、使った内容を残す")
    groups = [
        ("共通", 83), ("分野", 312), ("媒体", 541),
        ("プロジェクト", 770), ("キャラ / アイテム", 999), ("今回の指示", 1228),
    ]
    box_y = 1415
    box_w = 195
    for index, (label, x) in enumerate(groups):
        draw.rounded_rectangle((x, box_y, x + box_w, box_y + 66), radius=16, fill=NAVY if index in (0, 5) else MINT)
        color = WHITE if index in (0, 5) else TEAL
        label_font = font(19 if len(label) > 7 else 23)
        draw.text((x + 16, box_y + 18), label, font=label_font, fill=color)
        if index < len(groups) - 1:
            draw.text((x + box_w + 6, box_y + 18), "→", font=font(24), fill=GOLD)
    paragraph(draw, "解決済みの全文、参照画像、各レイヤーとハッシュを sidecar に保存。あとから確認できます。プロンプトだけで画像の同一再生成は保証しません。", (margin + 56, 1510), width - margin * 2 - 112, font(25))
    draw.text((margin + 56, 1604), "shared → domain → medium → project → entity → request", font=font(21), fill=MUTED)

    card(draw, (margin, 1692, width - margin, 2205))
    card_title(draw, margin + 54, 1722, "05  原画は保管。外部向け画像はPythonで別に書き出す")
    flow = [
        ("生成原画", "非公開マスター"),
        ("Python処理", "ロゴ透かし"),
        ("検査", "メタデータ"),
        ("人が確認", "公開可否を判断"),
        ("SNS / Web", "手動で投稿"),
    ]
    flow_x = margin + 42
    flow_y = 1800
    flow_w = 245
    for index, (headline, detail) in enumerate(flow):
        x = flow_x + index * 275
        draw.rounded_rectangle((x, flow_y, x + flow_w, flow_y + 110), radius=18, fill=MINT if index < 4 else NAVY)
        primary = TEAL if index < 4 else WHITE
        secondary = MUTED if index < 4 else (222, 242, 235)
        draw.text((x + 16, flow_y + 18), headline, font=font(25), fill=primary)
        draw.text((x + 16, flow_y + 63), detail, font=font(19), fill=secondary)
        if index < len(flow) - 1:
            draw.text((x + flow_w + 8, flow_y + 38), "→", font=font(23), fill=GOLD)
    draw.rounded_rectangle((margin + 46, 1940, width - margin - 46, 2035), radius=18, fill=(247, 245, 237))
    draw.text((margin + 68, 1957), "SNS  720px以内  /  JPEG圧縮  /  ロゴ透かし", font=font(23), fill=NAVY)
    draw.text((margin + 68, 1999), "Web  元の寸法を保持  /  PNG  /  ロゴ透かし", font=font(23), fill=NAVY)
    paragraph(draw, "生成原画の直接公開は禁止。投稿先・日時・derivative ID は投稿後に記録します。このSample自体は未投稿です。", (margin + 58, 2070), width - margin * 2 - 116, font(23), fill=MUTED)

    draw.text((margin, 2250), "Content Studio 0.1.0   •   Base minimum 0.1.0   •   Storyと共有コアIDを再利用", font=font(22), fill=NAVY)
    canvas.convert("RGB").save(output, format="PNG", optimize=False, compress_level=9)
    print(f"RENDERED {output} {width}x{height}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--make-logo", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.make_logo:
        make_logo(root / "assets/branding/watermark.png")
    output = args.output if args.output.is_absolute() else root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    make_infographic(root, output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
