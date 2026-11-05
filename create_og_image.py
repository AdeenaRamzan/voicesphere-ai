import os
from PIL import Image, ImageDraw, ImageFont

def create_og_banner(output_paths):
    WIDTH = 1200
    HEIGHT = 630

    # 1. Base canvas - Crisp clean off-white / light studio surface
    base = Image.new("RGBA", (WIDTH, HEIGHT), (250, 250, 252, 255))
    
    # 2. Subtle soft vertical gradient for depth
    grad = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(grad)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        # Smooth transition from pure crisp off-white (#fafbfc) to subtle cool light gray (#f1f3f6)
        r = int(252 - 12 * ratio)
        g = int(253 - 12 * ratio)
        b = int(255 - 11 * ratio)
        g_draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))
    base = Image.alpha_composite(base, grad)

    # 3. Very subtle neutral dot grid (minimalist tech texture)
    grid = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    grid_draw = ImageDraw.Draw(grid)
    for x in range(32, WIDTH, 32):
        for y in range(32, HEIGHT, 32):
            grid_draw.ellipse([(x - 1, y - 1), (x + 1, y + 1)], fill=(15, 23, 42, 10))
    base = Image.alpha_composite(base, grid)

    # Fonts
    f_bold = "C:/Windows/Fonts/segoeuib.ttf"
    f_sb = "C:/Windows/Fonts/seguisb.ttf"
    f_reg = "C:/Windows/Fonts/segoeui.ttf"

    title_font = ImageFont.truetype(f_bold, 56)
    tagline_font = ImageFont.truetype(f_bold, 24)
    desc_font = ImageFont.truetype(f_reg, 17)
    pill_font = ImageFont.truetype(f_sb, 13)
    badge_font = ImageFont.truetype(f_sb, 14)
    card_head_font = ImageFont.truetype(f_bold, 12)
    speaker_font = ImageFont.truetype(f_bold, 13)
    speech_font = ImageFont.truetype(f_reg, 16)

    draw = ImageDraw.Draw(base)

    # Outer decorative minimalist frame
    draw.rounded_rectangle([(16, 16), (WIDTH - 16, HEIGHT - 16)], radius=22, outline=(226, 232, 240, 255), width=1)
    draw.rounded_rectangle([(18, 18), (WIDTH - 18, HEIGHT - 18)], radius=20, outline=(241, 245, 249, 255), width=1)

    # Top Eyebrow Pill: "VOICESPHERE AI PLATFORM"
    eyebrow_x, eyebrow_y = 64, 48
    draw.rounded_rectangle([(eyebrow_x, eyebrow_y), (eyebrow_x + 285, eyebrow_y + 32)], radius=16,
                           fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=1)
    # Neutral slate dot
    draw.ellipse([(eyebrow_x + 14, eyebrow_y + 11), (eyebrow_x + 22, eyebrow_y + 19)], fill=(15, 23, 42, 255))
    draw.text((eyebrow_x + 30, eyebrow_y + 7), "REAL-TIME SPEECH AI PLATFORM", fill=(30, 41, 59, 255), font=pill_font)

    # Top Right Status Pill: "MINIMALIST LIGHT"
    status_w = 175
    status_x = WIDTH - 64 - status_w
    draw.rounded_rectangle([(status_x, eyebrow_y), (status_x + status_w, eyebrow_y + 32)], radius=16,
                           fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=1)
    draw.ellipse([(status_x + 14, eyebrow_y + 12), (status_x + 20, eyebrow_y + 18)], fill=(100, 116, 139, 255))
    draw.text((status_x + 28, eyebrow_y + 7), "PRODUCTION READY", fill=(71, 85, 105, 255), font=pill_font)

    # Brand Title Row
    brand_y = 96
    icon_box_x = 64
    icon_box_size = 64
    
    # Sleek matte black icon box
    draw.rounded_rectangle([(icon_box_x, brand_y), (icon_box_x + icon_box_size, brand_y + icon_box_size)], radius=16,
                           fill=(15, 23, 42, 255), outline=(15, 23, 42, 255), width=1)
    
    # Sharp white vector mic icon inside icon box
    mx = icon_box_x + icon_box_size // 2
    my = brand_y + 16
    draw.rounded_rectangle([(mx - 7, my), (mx + 7, my + 18)], radius=7, fill=(255, 255, 255))
    draw.arc([(mx - 13, my + 6), (mx + 13, my + 24)], start=0, end=180, fill=(255, 255, 255), width=3)
    draw.line([(mx, my + 24), (mx, my + 31)], fill=(255, 255, 255), width=3)
    draw.line([(mx - 8, my + 31), (mx + 8, my + 31)], fill=(255, 255, 255), width=3)

    # Main Brand Name - Crisp Deep Black
    draw.text((icon_box_x + icon_box_size + 18, brand_y + 2), "VoiceSphere AI", fill=(15, 23, 42, 255), font=title_font)
    
    # Tagline - Deep charcoal
    draw.text((64, 178), "Real-Time Speech Assistant with Live Captions", fill=(30, 41, 59, 255), font=tagline_font)
    # Subtitle - Neutral Slate
    draw.text((64, 214), "Instant voice recognition powered by Groq Whisper Large v3 and ultra-fast Llama 3.3 70B conversational intelligence.",
              fill=(100, 116, 139, 255), font=desc_font)

    # Interactive Mockup Card - Crisp white with subtle border and neutral drop shadow
    card_x = 64
    card_y = 262
    card_w = WIDTH - 128
    card_h = 244

    # Drop shadow
    shadow = Image.new("RGBA", (card_w + 20, card_h + 20), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    s_draw.rounded_rectangle([(10, 10), (card_w + 10, card_h + 10)], radius=18, fill=(15, 23, 42, 12))
    base.paste(shadow, (card_x - 10, card_y - 6), shadow)

    # Card background - Pure White
    draw.rounded_rectangle([(card_x, card_y), (card_x + card_w, card_y + card_h)], radius=16,
                           fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=1)

    # Card Window Controls - Subtle Monochrome Grays
    draw.ellipse([(card_x + 22, card_y + 18), (card_x + 32, card_y + 28)], fill=(226, 232, 240))
    draw.ellipse([(card_x + 38, card_y + 18), (card_x + 48, card_y + 28)], fill=(203, 213, 225))
    draw.ellipse([(card_x + 54, card_y + 18), (card_x + 64, card_y + 28)], fill=(148, 163, 184))

    # Card Subtitle Bar Badge
    draw.rounded_rectangle([(card_x + 82, card_y + 13), (card_x + 244, card_y + 33)], radius=10,
                           fill=(248, 250, 252), outline=(226, 232, 240), width=1)
    draw.ellipse([(card_x + 92, card_y + 19), (card_x + 100, card_y + 27)], fill=(15, 23, 42))
    draw.text((card_x + 107, card_y + 15), "LIVE AUDIO SPECTRUM", fill=(51, 65, 85), font=card_head_font)

    # Right side of card title bar: latency text
    latency_text = "Sub-Second Turnaround"
    lt_bbox = draw.textbbox((0, 0), latency_text, font=card_head_font)
    lt_w = lt_bbox[2] - lt_bbox[0]
    lt_x = card_x + card_w - lt_w - 30
    draw.ellipse([(lt_x - 14, card_y + 19), (lt_x - 6, card_y + 27)], fill=(100, 116, 139))
    draw.text((lt_x, card_y + 15), latency_text, fill=(71, 85, 105), font=card_head_font)

    # Divider in card
    draw.line([(card_x + 18, card_y + 44), (card_x + card_w - 18, card_y + 44)], fill=(241, 245, 249), width=1)

    # Monochrome Audio Waveform on Left Side
    wave_left = card_x + 36
    wave_cy = card_y + 144
    bars = [22, 38, 62, 95, 130, 155, 120, 85, 140, 160, 125, 90, 60, 110, 145, 95, 50, 80, 115, 70, 35, 65, 40, 20]
    bar_width = 7
    bar_gap = 5
    for i, bh in enumerate(bars):
        bx = wave_left + i * (bar_width + bar_gap)
        top = wave_cy - bh // 2
        bot = wave_cy + bh // 2
        
        # Monochrome gradient from deep charcoal (#0f172a) to slate gray (#64748b)
        ratio = i / (len(bars) - 1)
        # Symmetrical shade variation (darker at peaks)
        peak_ratio = bh / 160.0
        shade = int(15 + (120 - 15) * (1 - peak_ratio))
        draw.rounded_rectangle([(bx, top), (bx + bar_width, bot)], radius=3, fill=(shade, shade + 5, shade + 12, 240))

    # Dialogue / Live Subtitles on Right Side
    dialogue_x = wave_left + len(bars) * (bar_width + bar_gap) + 36
    dialogue_w = card_x + card_w - dialogue_x - 30

    # User message bubble - crisp clean white with subtle border
    u_bubble_y = card_y + 58
    u_bubble_h = 74
    draw.rounded_rectangle([(dialogue_x, u_bubble_y), (dialogue_x + dialogue_w, u_bubble_y + u_bubble_h)], radius=12,
                           fill=(248, 250, 252), outline=(226, 232, 240), width=1)
    
    # Speaker tag
    draw.rounded_rectangle([(dialogue_x + 16, u_bubble_y + 12), (dialogue_x + 68, u_bubble_y + 32)], radius=6,
                           fill=(226, 232, 240))
    draw.text((dialogue_x + 25, u_bubble_y + 14), "USER", fill=(51, 65, 85), font=speaker_font)
    draw.text((dialogue_x + 80, u_bubble_y + 14), "Voice Input (Auto Language Detect)", fill=(100, 116, 139), font=pill_font)
    draw.text((dialogue_x + 16, u_bubble_y + 41), '"How does Whisper large v3 achieve near real-time voice streaming?"',
              fill=(15, 23, 42), font=speech_font)

    # AI response bubble - subtle cool gray with slate border
    ai_bubble_y = card_y + 144
    ai_bubble_h = 78
    draw.rounded_rectangle([(dialogue_x, ai_bubble_y), (dialogue_x + dialogue_w, ai_bubble_y + ai_bubble_h)], radius=12,
                           fill=(241, 245, 249), outline=(203, 213, 225), width=1)
    
    # Speaker tag
    draw.rounded_rectangle([(dialogue_x + 16, ai_bubble_y + 12), (dialogue_x + 122, ai_bubble_y + 32)], radius=6,
                           fill=(15, 23, 42))
    draw.text((dialogue_x + 24, ai_bubble_y + 14), "VOICESPHERE", fill=(255, 255, 255), font=speaker_font)
    draw.text((dialogue_x + 134, ai_bubble_y + 14), "Groq LPU Acceleration • 750 tokens/sec", fill=(71, 85, 105), font=pill_font)
    draw.text((dialogue_x + 16, ai_bubble_y + 42), '"Whisper runs on Groq LPUs for sub-second transcription with Llama 3.3."',
              fill=(15, 23, 42), font=speech_font)

    # Bottom Pill Badges - Clean Monochrome White & Slate
    badges = [
        "Groq Whisper Large v3",
        "Llama 3.3 70B",
        "Web Audio Spectrum",
        "Multi-Language TTS",
        "Embeddable Widget",
    ]

    total_badge_w = 0
    badge_widths = []
    for text in badges:
        bbox = draw.textbbox((0, 0), text, font=badge_font)
        bw = (bbox[2] - bbox[0]) + 38
        badge_widths.append(bw)
        total_badge_w += bw
    
    gap = (card_w - total_badge_w) // (len(badges) - 1)
    curr_x = card_x
    by = 538
    bh = 38

    for text, bw in zip(badges, badge_widths):
        # White pill with subtle border
        draw.rounded_rectangle([(curr_x, by), (curr_x + bw, by + bh)], radius=19,
                               fill=(255, 255, 255), outline=(226, 232, 240), width=1)
        # Slate dot
        draw.ellipse([(curr_x + 14, by + 14), (curr_x + 22, by + 22)], fill=(30, 41, 59))
        draw.text((curr_x + 28, by + 9), text, fill=(15, 23, 42), font=badge_font)
        curr_x += bw + gap

    # Save to all target paths
    for p in output_paths:
        os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
        base.save(p, "PNG", optimize=True)
        print(f"Generated Minimalist Light OG banner: {p} ({WIDTH}x{HEIGHT})")

if __name__ == "__main__":
    paths = [
        "static/og-image.png",
        "static/opengraph-image.png",
        "frontend/public/og-image.png",
        "frontend/app/opengraph-image.png",
        "public/og-image.png",
    ]
    create_og_banner(paths)
