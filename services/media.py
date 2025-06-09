import os
import logging
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("zoo_bot.media")

MAX_TELEGRAM_PHOTO_SIZE = 10485760  # 10MB
JPEG_QUALITY_START = 95
JPEG_QUALITY_MIN = 70


async def generate_image(
        image_path: str,
        animal_name: str,
        user_name: str
) -> str:
    try:
        base = Image.open(image_path).convert("RGBA")
    except Exception:
        logger.exception(f"Не удалось открыть изображение {image_path}")
        raise

    draw = ImageDraw.Draw(base)
    margin = 20

    fonts_dir = "media/fonts"
    bold_path = os.path.join(fonts_dir, "ALS_Story_2.0_B.otf")
    regular_path = os.path.join(fonts_dir, "ALS_Story_2.0_R.otf")

    try:
        font_bold = ImageFont.truetype(bold_path, 48)
    except Exception:
        logger.warning(f"Не удалось загрузить шрифт {bold_path}, используем дефолт")
        font_bold = ImageFont.load_default()

    try:
        font_regular = ImageFont.truetype(regular_path, 36)
    except Exception:
        logger.warning(f"Не удалось загрузить шрифт {regular_path}, используем дефолт")
        font_regular = ImageFont.load_default()

    draw.text((margin, margin), animal_name, font=font_bold, fill="white")

    caption = f"{user_name}, это ты!"
    bbox = draw.textbbox((0, 0), caption, font=font_regular)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = margin
    y = base.height - margin - text_height
    draw.text((x, y), caption, font=font_regular, fill="white")

    logo_path = "media/logo/MZoo-logo-circle-mono-black.png"
    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo_width = base.width // 5
            logo = logo.resize(
                (logo_width, int(logo_width * logo.height / logo.width)),
                Image.Resampling.LANCZOS
            )
            pos = (base.width - logo.width - margin, base.height - logo.height - margin)
            base.alpha_composite(logo, dest=pos)
        except Exception:
            logger.exception(f"Не удалось вставить логотип {logo_path}")
    else:
        logger.warning(f"Логотип не найден по пути {logo_path}")

    out_dir = "media/generated"
    os.makedirs(out_dir, exist_ok=True)
    filename = f"{user_name}_{animal_name}.png"
    output_path = os.path.join(out_dir, filename)
    try:
        base.save(output_path)
        logger.info(f"Сгенерирована картинка результата: {output_path}")
    except Exception:
        logger.exception(f"Не удалось сохранить изображение {output_path}")
        raise

    return output_path


async def compress_image_if_needed(image_path: str) -> str:
    if os.path.getsize(image_path) <= MAX_TELEGRAM_PHOTO_SIZE:
        return image_path

    logger.warning(f" Размер лого {os.path.getsize(image_path)} превышает Telegram limit. Сжатие...")

    img = Image.open(image_path)
    compressed_path = image_path.replace(".png", ".jpg")

    quality = JPEG_QUALITY_START
    while quality >= JPEG_QUALITY_MIN:
        img.convert("RGB").save(compressed_path, format="JPEG", quality=quality)
        if os.path.getsize(compressed_path) <= MAX_TELEGRAM_PHOTO_SIZE:
            logger.info(f"Compressed image to {os.path.getsize(compressed_path)} bytes at quality={quality}")
            return compressed_path
        quality -= 5

    logger.warning("Неудалось сжать изображение. Отправка без фото.")
    return None
