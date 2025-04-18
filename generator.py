from PIL import Image, ImageDraw, ImageFont
import os
from collections import defaultdict

def draw_on_image(image, text, x, y, fonttype, draw, center=False):
    try:
        normal = ImageFont.truetype("arialbd.ttf", 90)
        bold = ImageFont.truetype("arialbd.ttf", 48)
        title = ImageFont.truetype("arialbd.ttf", 350)
    except:
        normal = bold = title = ImageFont.load_default()
        print("Czcionka Arial nie została znaleziona...")

    font = {1: normal, 2: bold, 3: title}.get(fonttype, normal)

    if center:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x -= text_width // 2
        y -= text_height // 2

    draw.text((x, y), text, fill="black", font=font)

def info(plik):
    with open(plik, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]

    przystanki, godziny = [], []
    for i, line in enumerate(lines):
        if "przystanek" in line.lower() and i + 1 < len(lines):
            przystanki.append(lines[i + 1].strip())
        if "godziny" in line.lower() and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if not next_line.lower().startswith("linia"):
                godziny.append(next_line.split())
    return przystanki, godziny

def sort_and_format_hours(godziny):
    sorted_hours = []
    for hour_list in godziny:
        formatted = [(t[:2], t[2:]) for t in hour_list if len(t) == 4 and t.isdigit()]
        sorted_hours.append(sorted(formatted))
    return sorted_hours

def get_y_for_hour(hour):
    try:
        return int(hour) * 115 + 143
    except ValueError:
        return 1000

def calculate_travel_time(dep_hour, dep_min, arr_hour, arr_min):
    dep = int(dep_hour) * 60 + int(dep_min)
    arr = int(arr_hour) * 60 + int(arr_min)
    if arr < dep:
        arr += 1440
    return arr - dep

def draw_plan(draw, przystanki, current_stop, x0=800, y0=40, width=1700):
    max_width = x0 + width
    line_height = 55
    spacing = 40

    draw_on_image(None, f"{przystanki[current_stop]}", x0, y0, fonttype=1, draw=draw)
    draw_on_image(None, "TRASA:", x0, y0 + 110, fonttype=2, draw=draw)

    x, y = x0 + 200, y0 + 110
    for stop in przystanki:
        stop_text = stop + ", "
        font = ImageFont.truetype("arialbd.ttf", 48)
        text_width = font.getbbox(stop_text)[2]

        if x + text_width > max_width:
            x = x0
            y += line_height
        draw.text((x, y), stop_text, fill="black", font=font)
        x += text_width

def generate_for_stop(index, przystanki, sorted_hours, linia):
    image = Image.open("templates/easy.png")
    draw = ImageDraw.Draw(image)

    draw_on_image(image, linia, 390, 175, fonttype=3, draw=draw, center=True)

    start_y = 550
    for i, przystanek in enumerate(przystanki[index:], start=index):
        draw_on_image(image, przystanek, 150, start_y, fonttype=2, draw=draw)
        start_y += 100

    cumulative = 0
    y = 650
    for i in range(index + 1, len(przystanki)):
        dep_h, dep_m = sorted_hours[i - 1][0]
        arr_h, arr_m = sorted_hours[i][0]
        travel = calculate_travel_time(dep_h, dep_m, arr_h, arr_m)
        cumulative += travel
        draw_on_image(image, str(cumulative), 60, y - 20, fonttype=1, draw=draw)
        y += 100

    current_hours = sorted_hours[index]
    by_hour = defaultdict(list)
    for h, m in current_hours:
        by_hour[h].append(m)

    for hour, minutes in by_hour.items():
        y = get_y_for_hour(hour)
        for i, minute in enumerate(minutes):
            x = 875 + i * 125
            draw_on_image(image, minute, x + 10, y - 10, fonttype=1, draw=draw)

    draw_plan(draw, przystanki, index)

    filename = f"output/stop_{index}_{przystanki[index].replace(' ', '_')}.png"
    image.save(filename)
    print(f"Zapisano: {filename}")

if __name__ == "__main__":
    try:
        with open("dane.txt", "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
            linia = next((lines[i + 1].strip() for i in range(len(lines) - 1) if "linia" in lines[i].lower()), None)
    except FileNotFoundError:
        print("Nie znaleziono pliku dane.txt")
        exit()

    if not linia:
        print("Nie znaleziono numeru linii.")
        exit()

    przystanki, godziny = info("dane.txt")
    sorted_hours = sort_and_format_hours(godziny)

    os.makedirs("output", exist_ok=True)
    for i in range(len(przystanki)):
        generate_for_stop(i, przystanki, sorted_hours, linia)
