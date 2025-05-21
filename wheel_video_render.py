#!/usr/bin/env python3
# wheel_video_render.py ─ статичное Lucky Wheel → MP4 (Windows-friendly)

import colorsys, io, math
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import requests
from PIL import Image
from moviepy import ImageClip            # MoviePy ≥ 2.0

# ───────── ПАРАМЕТРЫ, которые определяют внешний вид ──────────
GROUP_NAME  = "ft-204-1"      # ← нужная группа
VIDEO_SEC   = 3               # длительность ролика

CANVAS_PX   = 1000            # размер итогового PNG (⟂ для Telegram кружка)
WHEEL_R     = 1.32            # радиус цветных секторов                   ↑
LABEL_R     = WHEEL_R * .65   # радиус подписи (чуть ближе к центру)      │
FONT_SZ     = 12              # кегль шрифта                              │
LOGO_ZOOM   = .27             # масштаб логотипа по центру                ┘

# «каёмка»: белое кольцо + тонкий серый кант ровно по тупому краю клюва
RIM_OUTSET  = .1             # расстояние от края колеса до серого канта
RIM_WIDTH   = .01            # толщина белой каймы
EDGE_COLOR  = '#d8d8d8'       # цвет тонкого канта

# клюв-указатель (острее и чуть «въезжает» внутрь)
POINTER_INSET = .025           # насколько кончик уходит ВНУТРЬ колеса
POINTER_OUT   = RIM_OUTSET    # тупой край совпадает с серым кантом
POINTER_H     = .065          # половина высоты треугольника

LOGO_PATH  = Path("static/images/wheel-logo.png")
OUT_FILE   = f"{GROUP_NAME}_wheel.mp4"

# ───────── ДАННЫЕ (из main.py) ──────────
GROUPS = { 'ft-201-1':'0','ft-201-2':'313135890','ft-202-1':'429115037',
           'ft-202-2':'1499384932','ft-203-1':'1434241927','ft-203-2':'101485156',
           'ft-204-1':'1801994266','ft-204-2':'2063966210','kn':'393945752' }
GROUPS_COUNT = {'0':14,'313135890':14,'429115037':15,'1499384932':15,
                '1434241927':13,'101485156':13,'1801994266':13,'2063966210':14,
                '393945752':4}
EXCLUDED = { "Бутовой Владислав","Гальянов Фёдор","Бархатова Алёна",
             "Пузынин Георгий","Сидорова Алёна","Одайкина Елизавета",
             "Юдин Николай","Артемьев Тимофей","Колесников Захар",
             "Печников Георгий","Сахбиев Марат","Суставов Данил Сергеевич" }

# ───────── HELPERS ──────────
def get_students(group:str):
    gid = GROUPS[group]
    url = ("https://docs.google.com/spreadsheets/d/"
           "1QyIvnpMN1H3v6Ywj6QGl59KsdRbeUrtHXcAlE45sasY/"
           f"export?format=csv&gid={gid}")
    df  = pd.read_csv(url)

    cols = [9,11,13,15,17,20,24,26,29,31,33,35]
    st=[]
    for i in range(GROUPS_COUNT[gid]):
        name=str(df.iloc[i,0]).strip()
        if not name or name in EXCLUDED: continue
        score=sum(float(str(df.iloc[i,c]).replace(',','.'))
                  if str(df.iloc[i,c]).replace(',','.').replace('.','',1).isdigit()
                  else 0 for c in cols)
        if score>0: st.append({'name':name,'score':score})
    return st

def probabilities(st):
    inv=[1/(s['score']+0.01) for s in st]
    p  =[max(v/sum(inv), 0.01/360) for v in inv]     # минимум
    total=sum(p)
    return [v/total for v in p]

def hsl(i,n):   return colorsys.hls_to_rgb((i/n)%1, 0.60, 0.70)
def trim(n,p):  return "" if p<0.02 else (n if len(n)<=24 else n[:24]+"…")

# ───────── РИСУЕМ PNG ──────────
def draw_static_wheel(group)->bytes:
    st=get_students(group)
    pr=probabilities(st)
    n=len(st)
    for i,s in enumerate(st):
        s['prob']=pr[i]; s['color']=hsl(i,n)

    sizes  =[s['prob'] for s in st]
    labels =[trim(s['name'],s['prob']) for s in st]
    colors =[s['color'] for s in st]

    fig,ax=plt.subplots(figsize=(CANVAS_PX/100,CANVAS_PX/100),
                        subplot_kw={'aspect':'equal'})

    # белая каёмка и серый кант (по тупому краю клюва)
    rim_inner = WHEEL_R + .001
    rim_outer = WHEEL_R + RIM_OUTSET - .001
    # белая
    ax.add_artist(plt.Circle((0,0), rim_outer, fc='white', ec='none', zorder=1))
    # серый кант
    ax.add_artist(plt.Circle((0,0), rim_outer, fc='none',
                             ec=EDGE_COLOR, lw=2.2, zorder=2))

    # секторы
    ax.pie(sizes, radius=WHEEL_R, labels=['']*n,
           startangle=0, counterclock=False, colors=colors,
           wedgeprops=dict(edgecolor='white', linewidth=.8))

    # подписи (по радиусу, CW)
    deg=0
    for frac,lbl in zip(sizes,labels):
        if not lbl:
            deg+=frac*360; continue
        mid=deg+frac*360/2
        theta=-math.radians(mid)
        ax.text(LABEL_R*math.cos(theta),
                LABEL_R*math.sin(theta),
                lbl, ha='center', va='center',
                rotation=-mid, rotation_mode='anchor',
                fontsize=FONT_SZ)
        deg+=frac*360

    # логотип
    if LOGO_PATH.exists():
        from matplotlib.offsetbox import OffsetImage, AnnotationBbox
        ax.add_artist(AnnotationBbox(
            OffsetImage(plt.imread(LOGO_PATH), zoom=LOGO_ZOOM),
            (0,0), frameon=False, zorder=6))

    # клюв-указатель (острее, наезжает внутрь)
    tip_r = WHEEL_R - POINTER_INSET
    base_r = WHEEL_R + POINTER_OUT
    ax.add_patch(mpatches.Polygon(
        [(tip_r,0),
         (base_r,  POINTER_H),
         (base_r, -POINTER_H)],
        closed=True, color='#e74c3c', zorder=7))

    ax.set_xlim(-1.45,1.45)
    ax.set_ylim(-1.45,1.45)
    ax.axis('off')

    buf=io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return buf.read()

# ───────── PNG → MP4 ──────────
def render_video(png:bytes, out:str, sec:int):
    img = np.asarray(Image.open(io.BytesIO(png)).convert('RGB'))
    h,w = img.shape[:2]
    if h%2 or w%2:
        img=np.pad(img, ((0,h%2),(0,w%2),(0,0)), mode='edge')
    ImageClip(img).with_duration(sec).write_videofile(
        out, fps=30, codec='libx264',
        ffmpeg_params=['-pix_fmt','yuv420p','-profile:v','baseline','-level','3.0'],
        bitrate='1M', preset='ultrafast', audio=False, logger=None)

# ───────── тест-прогон ──────────
png = draw_static_wheel(GROUP_NAME)
render_video(png, OUT_FILE, VIDEO_SEC)
print("✔ saved:", OUT_FILE)
