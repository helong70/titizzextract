#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建 Ti 图标文件
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_ti_icon():
    """
    创建一个带有 Ti 字母的粉色图标
    """
    # 图标尺寸
    size = 32
    
    # B站粉色 #FB7299
    bilibili_pink = (251, 114, 153, 255)
    white = (255, 255, 255, 255)
    
    # 创建图像
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制圆形背景
    margin = 2
    draw.ellipse([margin, margin, size-margin, size-margin], fill=bilibili_pink)
    
    # 尝试使用系统字体绘制 Ti
    try:
        # 尝试几种常见字体
        font_names = ['arial.ttf', 'calibri.ttf', 'segoeui.ttf']
        font = None
        
        for font_name in font_names:
            try:
                font_path = f"C:/Windows/Fonts/{font_name}"
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, 18)
                    break
            except:
                continue
        
        if font is None:
            # 如果找不到TrueType字体，使用默认字体
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # 绘制文字 "Ti"
    text = "Ti"
    
    # 尝试使用 anchor='mm' 直接居中（Pillow 支持）
    cx, cy = size // 2, size // 2
    try:
        draw.text((cx, cy), text, font=font, fill=white, anchor='mm')
    except TypeError:
        # 若 Pillow 版本不支持 anchor 参数，回退到基于字体度量的计算
        try:
            ascent, descent = font.getmetrics()
            # 有些字体的 bbox 更准确
            try:
                bbox = font.getmask(text).getbbox()
                if bbox:
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                else:
                    text_width, text_height = draw.textsize(text, font=font)
            except Exception:
                text_width, text_height = draw.textsize(text, font=font)

            # 垂直使用 ascent/descent 更精确
            total_height = ascent + descent if (ascent + descent) > 0 else text_height
            x = (size - text_width) // 2
            y = (size - total_height) // 2
        except Exception:
            # 最后回退（与之前相同）
            try:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = (size - text_width) // 2
                y = (size - text_height) // 2 - 2
            except Exception:
                text_width, text_height = draw.textsize(text, font=font)
                x = (size - text_width) // 2
                y = (size - text_height) // 2 - 2

        draw.text((x, y), text, font=font, fill=white)
    
    return img

def main():
    """
    创建图标文件
    """
    try:
        print("🎨 正在创建 Ti 图标...")
        
        # 创建图标
        icon_img = create_ti_icon()
        
        # 保存为 ICO 文件
        icon_path = "titizz_icon.ico"
        icon_img.save(icon_path, format='ICO', sizes=[(32, 32)])
        
        print(f"✅ 图标创建成功: {icon_path}")
        return True
        
    except ImportError:
        print("❌ 需要安装 Pillow 库: pip install Pillow")
        return False
    except Exception as e:
        print(f"❌ 创建图标失败: {e}")
        return False

if __name__ == "__main__":
    main()