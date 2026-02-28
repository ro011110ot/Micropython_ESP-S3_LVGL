import lvgl as lv

lv.lodepng_init()

f = open("/icons_png/01n.png", "rb")
png_bytes = bytearray(f.read())
f.close()
print("PNG Groesse:", len(png_bytes), "bytes")

scr = lv.screen_active()

# Test 1: Direkt via S: Pfad
img1 = lv.image(scr)
img1.set_pos(10, 50)
img1.set_src("S:/icons_png/01n.png")
print("Test 1: oben links - S: Pfad")

# Test 2: image_dsc_t RAW_ALPHA
img_dsc1 = lv.image_dsc_t(
    {
        "header": {
            "magic": lv.IMAGE_HEADER_MAGIC,
            "cf": lv.COLOR_FORMAT.RAW_ALPHA,
            "w": 100,
            "h": 100,
        },
        "data_size": len(png_bytes),
        "data": memoryview(png_bytes),
    }
)
img2 = lv.image(scr)
img2.set_pos(120, 50)
img2.set_src(img_dsc1)
print("Test 2: oben rechts - RAW_ALPHA")

# Test 3: image_dsc_t RAW
img_dsc2 = lv.image_dsc_t(
    {
        "header": {
            "magic": lv.IMAGE_HEADER_MAGIC,
            "cf": lv.COLOR_FORMAT.RAW,
            "w": 100,
            "h": 100,
        },
        "data_size": len(png_bytes),
        "data": memoryview(png_bytes),
    }
)
img3 = lv.image(scr)
img3.set_pos(10, 160)
img3.set_src(img_dsc2)
print("Test 3: unten links - RAW")

lv.refr_now(lv.display_get_default())
print("Welcher der 3 Tests zeigt ein echtes Icon?")
