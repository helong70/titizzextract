#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成多尺寸 ICO（256/128/64/48/32/16），提高在 Windows 上显示图标的兼容性
"""
from PIL import Image, ImageDraw, ImageFont
import os

OUT = "titizz_icon_full.ico"

def make_icon():
    sizes = [256, 128, 64, 48, 32, 16]
    images = []
    bilibili_pink = (251, 114, 153, 255)
    white = (255, 255, 255, 255)
    for size in sizes:
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        margin = max(2, size // 16)
        draw.ellipse([margin, margin, size - margin - 1, size - margin - 1], fill=bilibili_pink)
        # draw 'Ti'
        font = None
        try:
            # scale font size proportionally
            font_size = max(10, int(size * 0.45))
            for fn in ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/calibri.ttf"]:
                if os.path.exists(fn):
                    try:
                        font = ImageFont.truetype(fn, font_size)
                        break
                    except:
                        pass
        except Exception:
            font = None
        if font is None:
            try:
                font = ImageFont.load_default()
            except:
                font = None
        text = "Ti"
        if font:
            cx, cy = size // 2, size // 2
            try:
                # Pillow 支持 anchor='mm' 时可以直接居中
                draw.text((cx, cy), text, font=font, fill=white, anchor='mm')
            except TypeError:
                # 回退到基于 bbox 的度量
                try:
                    bbox = draw.textbbox((0,0), text, font=font)
                    w = bbox[2] - bbox[0]
                    h = bbox[3] - bbox[1]
                except Exception:
                    w, h = draw.textsize(text, font=font)
                x = (size - w) // 2
                y = (size - h) // 2 - max(1, size // 32)
                draw.text((x, y), text, font=font, fill=white)
        else:
            # fallback simple shapes
            draw.rectangle([size*0.2, size*0.3, size*0.5, size*0.35], fill=white)
            draw.rectangle([size*0.35, size*0.35, size*0.45, size*0.7], fill=white)
            draw.ellipse([size*0.65- (size*0.04), size*0.28, size*0.65 + (size*0.04), size*0.28 + (size*0.04)], fill=white)
            draw.rectangle([size*0.6, size*0.35, size*0.7, size*0.7], fill=white)
        images.append(img)
    # Save using the largest image and pass sizes
    if os.path.exists(OUT):
        os.remove(OUT)
    try:
        images[0].save(OUT, format='ICO', sizes=[(s,s) for s in sizes])
    except Exception as e:
        # Try saving via temporary PNG as fallback
        tmp = 'tmp_icon_256.png'
        images[0].save(tmp, format='PNG')
        im = Image.open(tmp)
        im.save(OUT, format='ICO', sizes=[(s,s) for s in sizes])
        try:
            os.remove(tmp)
        except:
            pass
    if os.path.exists(OUT):
        print(f"✅ 生成图标: {OUT} ({os.path.getsize(OUT)} bytes)")
        return True
    else:
        print("❌ 未生成图标")
        return False

if __name__ == '__main__':
    make_icon()