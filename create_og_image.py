import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_og_banner(output_paths):
    WIDTH = 1200
    HEIGHT = 630

    # 1. Base canvas
    base = Image.new("RGBA", (WIDTH, HEIGHT), (10, 15, 29, 255))
    
    # 2. Gradient background
    grad = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(grad)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(9 + (15 - 9) * ratio)
        g = int(14 + (23 - 14) * ratio)
        b = int(26 + (42 - 26) * ratio)
        g_draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))
    base = Image.alpha_composite(base, grad)

    # 3. Soft ambient glow orbs
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)

    # Glowing indigo orb (top-left)
    for r in range(380, 0, -4):
        alpha = int(48 * (1 - r / 380)**1.8)
        glow_draw.ellipse([(140 - r, 100 - r), (140 + r, 100 + r)], fill=(79, 70, 229, alpha))

    # Glowing violet orb (bottom-right)
    for r in range(420, 0, -4):
        alpha = int(55 * (1 - r / 420)**1.8)
        glow_draw.ellipse([(960 - r, 460 - r), (960 + r, 460 + r)], fill=(124, 58, 237, alpha))

    # Glowing cyan orb (middle-right)
    for r in range(260, 0, -4):
        alpha = int(32 * (1 - r / 260)**2.0)
        glow_draw.ellipse([(700 - r, 280 - r), (700 + r, 280 + r)], fill=(6, 182, 212, alpha))

    base = Image.alpha_composite(base, glow)

    # 4. Subtle dot grid overlay
    grid = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    grid_draw = ImageDraw.Draw(grid)
    for x in range(30, WIDTH, 32):
        for y in range(30, HEIGHT, 32):
            grid_draw.ellipse([(x - 1, y - 1), (x + 1, y + 1)], fill=(255, 255, 255, 10))
    base = Image.alpha_composite(base, grid)

    # Fonts
    f_bold = "C:/Windows/Fonts/segoeuib.ttf"
    f_sb = "C:/Windows/Fonts/seguisb.ttf"
    f_reg = "C:/Windows/Fonts/segoeui.ttf"

    title_font = ImageFont.truetype(f_bold, 56)
    tagline_font = ImageFont.truetype(f_bold, 25)
    desc_font = ImageFont.truetype(f_reg, 18)
    pill_font = ImageFont.truetype(f_sb, 13)
    badge_font = ImageFont.truetype(f_sb, 14)
    card_head_font = ImageFont.truetype(f_bold, 12)
    speaker_font = ImageFont.truetype(f_bold, 13)
    speech_font = ImageFont.truetype(f_reg, 16)

    draw = ImageDraw.Draw(base)

    # Outer decorative frame
    draw.rounded_rectangle([(16, 16), (WIDTH - 16, HEIGHT - 16)], radius=22, outline=(255, 255, 255, 24), width=1)
    draw.rounded_rectangle([(18, 18), (WIDTH - 18, HEIGHT - 18)], radius=20, outline=(79, 70, 229, 35), width=1)

    # Top Eyebrow Pill
    eyebrow_x, eyebrow_y = 64, 48
    draw.rounded_rectangle([(eyebrow_x, eyebrow_y), (eyebrow_x + 295, eyebrow_y + 32)], radius=16,
                           fill=(30, 27, 75, 220), outline=(99, 102, 241, 160), width=1)
    draw.ellipse([(eyebrow_x + 14, eyebrow_y + 11), (eyebrow_x + 22, eyebrow_y + 19)], fill=(16, 185, 129))
    draw.text((eyebrow_x + 30, eyebrow_y + 7), "REAL-TIME SPEECH AI PLATFORM", fill=(199, 210, 254), font=pill_font)

    # Top Right Status Pill: "PRODUCTION READY"
    status_w = 190
    status_x = WIDTH - 64 - status_w
    draw.rounded_rectangle([(status_x, eyebrow_y), (status_x + status_w, eyebrow_y + 32)], radius=16,
                           fill=(15, 23, 42, 200), outline=(51, 65, 85, 180), width=1)
    draw.ellipse([(status_x + 14, eyebrow_y + 12), (status_x + 20, eyebrow_y + 18)], fill=(6, 182, 212))
    draw.text((status_x + 28, eyebrow_y + 7), "PRODUCTION READY", fill=(148, 163, 184), font=pill_font)

    # Brand Title Row
    brand_y = 96
    icon_box_x = 64
    icon_box_size = 64
    # Gradient icon box
    draw.rounded_rectangle([(icon_box_x, brand_y), (icon_box_x + icon_box_size, brand_y + icon_box_size)], radius=16,
                           fill=(79, 70, 229), outline=(165, 180, 252, 120), width=1)
    
    # Sharp vector mic icon inside icon box
    mx = icon_box_x + icon_box_size // 2
    my = brand_y + 16
    draw.rounded_rectangle([(mx - 7, my), (mx + 7, my + 18)], radius=7, fill=(255, 255, 255))
    draw.arc([(mx - 13, my + 6), (mx + 13, my + 24)], start=0, end=180, fill=(255, 255, 255), width=3)
    draw.line([(mx, my + 24), (mx, my + 31)], fill=(255, 255, 255), width=3)
    draw.line([(mx - 8, my + 31), (mx + 8, my + 31)], fill=(255, 255, 255), width=3)

    # Main Brand Name
    draw.text((icon_box_x + icon_box_size + 18, brand_y + 2), "VoiceSphere AI", fill=(255, 255, 255), font=title_font)
    
    # Tagline
    draw.text((64, 178), "Real-Time Speech Assistant with Live Captions", fill=(224, 231, 255), font=tagline_font)
    draw.text((64, 215), "Instant voice recognition powered by Groq Whisper Large v3 and ultra-fast Llama 3.3 70B conversational intelligence.",
              fill=(148, 163, 184), font=desc_font)

    # Interactive Mockup Card
    card_x = 64
    card_y = 265
    card_w = WIDTH - 128
    card_h = 240

    # Card background with glass effect
    card_img = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card_img)
    cd.rounded_rectangle([(0, 0), (card_w, card_h)], radius=16,
                         fill=(15, 23, 42, 225), outline=(99, 102, 241, 90), width=1)
    base.paste(card_img, (card_x, card_y), card_img)

    # Card Window Controls
    draw.ellipse([(card_x + 22, card_y + 18), (card_x + 32, card_y + 28)], fill=(244, 63, 94, 220))
    draw.ellipse([(card_x + 38, card_y + 18), (card_x + 48, card_y + 28)], fill=(245, 158, 11, 220))
    draw.ellipse([(card_x + 54, card_y + 18), (card_x + 64, card_y + 28)], fill=(16, 185, 129, 220))

    # Card Subtitle Bar Badge
    draw.rounded_rectangle([(card_x + 82, card_y + 13), (card_x + 248, card_y + 33)], radius=10,
                           fill=(30, 27, 75, 200), outline=(129, 140, 248, 100), width=1)
    draw.ellipse([(card_x + 92, card_y + 19), (card_x + 100, card_y + 27)], fill=(16, 185, 129))
    draw.text((card_x + 107, card_y + 15), "LIVE AUDIO SPECTRUM", fill=(199, 210, 254), font=card_head_font)

    # Right side of card title bar: latency badge (custom lightning symbol)
    latency_text = "Sub-Second Turnaround"
    lt_bbox = draw.textbbox((0, 0), latency_text, font=card_head_font)
    lt_w = lt_bbox[2] - lt_bbox[0]
    lt_x = card_x + card_w - lt_w - 30
    # draw glowing dot next to latency text
    draw.ellipse([(lt_x - 14, card_y + 19), (lt_x - 6, card_y + 27)], fill=(6, 182, 212))
    draw.text((lt_x, card_y + 15), latency_text, fill=(94, 234, 212), font=card_head_font)

    # Divider in card
    draw.line([(card_x + 18, card_y + 44), (card_x + card_w - 18, card_y + 44)], fill=(30, 41, 59, 200), width=1)

    # Dynamic Audio Waveform on Left Side
    wave_left = card_x + 36
    wave_cy = card_y + 144
    bars = [22, 38, 62, 95, 130, 155, 120, 85, 140, 160, 125, 90, 60, 110, 145, 95, 50, 80, 115, 70, 35, 65, 40, 20]
    bar_width = 7
    bar_gap = 5
    for i, bh in enumerate(bars):
        bx = wave_left + i * (bar_width + bar_gap)
        top = wave_cy - bh // 2
        bot = wave_cy + bh // 2
        
        # Smooth color gradient from Cyan (#06b6d4) through Indigo (#6366f1) to Violet (#a855f7)
        ratio = i / (len(bars) - 1)
        if ratio < 0.5:
            t = ratio / 0.5
            cr = int(6 + (99 - 6) * t)
            cg = int(182 + (102 - 182) * t)
            cb = int(212 + (241 - 212) * t)
        else:
            t = (ratio - 0.5) / 0.5
            cr = int(99 + (168 - 99) * t)
            cg = int(102 + (85 - 102) * t)
            cb = int(241 + (247 - 241) * t)
            
        draw.rounded_rectangle([(bx, top), (bx + bar_width, bot)], radius=3, fill=(cr, cg, cb, 240))

    # Dialogue / Live Subtitles on Right Side
    dialogue_x = wave_left + len(bars) * (bar_width + bar_gap) + 36
    dialogue_w = card_x + card_w - dialogue_x - 30

    # User message bubble
    u_bubble_y = card_y + 60
    u_bubble_h = 72
    draw.rounded_rectangle([(dialogue_x, u_bubble_y), (dialogue_x + dialogue_w, u_bubble_y + u_bubble_h)], radius=12,
                           fill=(30, 41, 59, 180), outline=(51, 65, 85, 180), width=1)
    
    # Speaker tag
    draw.rounded_rectangle([(dialogue_x + 16, u_bubble_y + 12), (dialogue_x + 68, u_bubble_y + 32)], radius=6,
                           fill=(15, 23, 42, 220))
    draw.text((dialogue_x + 25, u_bubble_y + 14), "USER", fill=(203, 213, 225), font=speaker_font)
    draw.text((dialogue_x + 80, u_bubble_y + 14), "Voice Input (Auto Language Detect)", fill=(148, 163, 184), font=pill_font)
    draw.text((dialogue_x + 16, u_bubble_y + 40), '"How does Whisper large v3 achieve near real-time voice streaming?"',
              fill=(241, 245, 249), font=speech_font)

    # AI response bubble
    ai_bubble_y = card_y + 144
    ai_bubble_h = 76
    draw.rounded_rectangle([(dialogue_x, ai_bubble_y), (dialogue_x + dialogue_w, ai_bubble_y + ai_bubble_h)], radius=12,
                           fill=(49, 46, 129, 140), outline=(99, 102, 241, 150), width=1)
    
    # Speaker tag
    draw.rounded_rectangle([(dialogue_x + 16, ai_bubble_y + 12), (dialogue_x + 122, ai_bubble_y + 32)], radius=6,
                           fill=(67, 56, 202, 220))
    draw.text((dialogue_x + 24, ai_bubble_y + 14), "VOICESPHERE", fill=(255, 255, 255), font=speaker_font)
    draw.text((dialogue_x + 134, ai_bubble_y + 14), "Groq LPU Acceleration • 750 tokens/sec", fill=(199, 210, 254), font=pill_font)
    draw.text((dialogue_x + 16, ai_bubble_y + 42), '"Whisper runs on Groq LPUs for sub-second transcription with Llama 3.3."',
              fill=(224, 231, 255), font=speech_font)

    # Bottom Pill Badges - perfectly sized and centered
    badges = [
        ("Groq Whisper Large v3", (99, 102, 241)),
        ("Llama 3.3 70B", (168, 85, 247)),
        ("Web Audio Spectrum", (6, 182, 212)),
        ("Multi-Language TTS", (16, 185, 129)),
        ("Embeddable Widget", (245, 158, 11)),
    ]

    total_badge_w = 0
    badge_widths = []
    for text, _ in badges:
        bbox = draw.textbbox((0, 0), text, font=badge_font)
        bw = (bbox[2] - bbox[0]) + 38  # padding + dot
        badge_widths.append(bw)
        total_badge_w += bw
    
    gap = (card_w - total_badge_w) // (len(badges) - 1)
    curr_x = card_x
    by = 538
    bh = 38

    for (text, col), bw in zip(badges, badge_widths):
        draw.rounded_rectangle([(curr_x, by), (curr_x + bw, by + bh)], radius=19,
                               fill=(15, 23, 42, 230), outline=(*col, 130), width=1)
        # Colored dot
        draw.ellipse([(curr_x + 14, by + 14), (curr_x + 22, by + 22)], fill=col)
        draw.text((curr_x + 28, by + 9), text, fill=(241, 245, 249), font=badge_font)
        curr_x += bw + gap

    # Save to all requested target paths
    for p in output_paths:
        os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
        base.save(p, "PNG", optimize=True)
        print(f"Generated {p} ({WIDTH}x{HEIGHT})")

if __name__ == "__main__":
    paths = [
        "static/og-image.png",
        "static/opengraph-image.png",
        "frontend/public/og-image.png",
        "frontend/app/opengraph-image.png",
        "public/og-image.png",
    ]
    create_og_banner(paths)
