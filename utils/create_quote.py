from PIL import Image, ImageDraw, ImageFont, ImageFilter

AVATAR_SIZE = 700
INITIAL_FONT_SIZE = 120
SMALL_FONT_SIZE = 100
IMAGE_SCALE = 2
MIN_FONT_SIZE = 60
MARGIN = 200 * IMAGE_SCALE
TEXT_BOX_PADDING = 0
TEXT_BOX_RIGHT_MARGIN = 0


def make_circle(image, blur_radius=1):
    size = image.size
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))
    output = Image.new("RGBA", size, (0, 0, 0, 0))
    output.paste(image, (0, 0), mask)
    return output


def wrap_text(text, font, max_width):
    words = text.split()
    wrapped_lines = []
    current_line = []

    def split_long_word(word):
        split_word = []
        i = 1
        while i < len(word):
            if font.getbbox(word[:i + 1])[2] > max_width:
                split_word.append(word[:i] + '-')
                word = word[i:]
                i = 0
            i += 1
        split_word.append(word)
        return split_word

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = font.getbbox(test_line)
        if bbox[2] - bbox[0] <= max_width:
            current_line.append(word)
        else:
            if font.getbbox(word)[2] > max_width:
                split_words = split_long_word(word)
                for split_word in split_words:
                    if current_line:
                        wrapped_lines.append(' '.join(current_line))
                        current_line = []
                    current_line.append(split_word)
                wrapped_lines.append(' '.join(current_line))
                current_line = []
            else:
                if current_line:
                    wrapped_lines.append(' '.join(current_line))
                current_line = [word]

    if current_line:
        wrapped_lines.append(' '.join(current_line))
    return wrapped_lines


def fit_text_in_box(text, initial_font_size, font_path, max_width, max_height):
    font_size = initial_font_size
    font = ImageFont.truetype(font_path, font_size)
    wrapped_text = wrap_text(text, font, max_width)
    total_height = sum(font.getbbox(line)[3] for line in wrapped_text)

    while total_height > max_height and font_size > MIN_FONT_SIZE:
        font_size -= 5
        font = ImageFont.truetype(font_path, font_size)
        wrapped_text = wrap_text(text, font, max_width)
        total_height = sum(font.getbbox(line)[3] for line in wrapped_text)

    return font, wrapped_text


def quote(text, username, date, user_id):
    base_image = Image.open("images/background.jpg").convert("RGBA")
    base_image = base_image.resize((base_image.width * IMAGE_SCALE, base_image.height * IMAGE_SCALE), Image.LANCZOS)

    draw = ImageDraw.Draw(base_image)
    font_path = "fonts/Ubuntu-Medium.ttf"
    font_small = ImageFont.truetype(font_path, SMALL_FONT_SIZE)

    image_width, image_height = base_image.size

    avatar = Image.open(f"../user_images/{user_id}.jpg").convert("RGBA")
    avatar = avatar.resize((AVATAR_SIZE, AVATAR_SIZE), Image.LANCZOS)
    avatar_circle = make_circle(avatar, blur_radius=2)
    x_position = 50 * IMAGE_SCALE
    y_position = (image_height - avatar_circle.size[1]) // 2 - 20
    base_image.paste(avatar_circle, (x_position, y_position), avatar_circle)

    right_edge_avatar = x_position + AVATAR_SIZE
    right_edge_image = image_width

    text_box_width = right_edge_image - right_edge_avatar - TEXT_BOX_PADDING - TEXT_BOX_RIGHT_MARGIN

    text_box_height = image_height - 200 * IMAGE_SCALE
    text_box_y = 100 * IMAGE_SCALE

    text_box_x = right_edge_avatar + TEXT_BOX_PADDING

    font_large, wrapped_text = fit_text_in_box(text, INITIAL_FONT_SIZE, font_path, text_box_width - 40,
                                               text_box_height - 40)

    total_text_height = sum(font_large.getbbox(line)[3] for line in wrapped_text)
    y_text = text_box_y + (text_box_height - total_text_height) // 2

    for line in wrapped_text:
        bbox = font_large.getbbox(line)
        draw.text((text_box_x + (text_box_width - bbox[2]) // 2, y_text), line, font=font_large, fill="white")
        y_text += bbox[3] + 10

    text_below_avatar_y = y_position + avatar_circle.size[1] + 20
    text_small_x = x_position
    draw.text((text_small_x, text_below_avatar_y), username, font=font_small, fill="white")
    draw.text((text_small_x, text_below_avatar_y + font_small.getbbox("A")[3] + 10), date, font=font_small,
              fill="white")

    base_image = base_image.convert("RGB")
    return base_image
