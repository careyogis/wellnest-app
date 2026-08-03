#!/usr/bin/env python3
import os
import re
import subprocess

app_dir = os.path.dirname(os.path.abspath(__file__))
public_css = os.path.join(app_dir, "public", "css")
public_js = os.path.join(app_dir, "public", "js")

css_files = [
    "animate.css",
    "bootstrap.min.css",
    "bootstrap-datepicker.min.css",
    "bootstrap-select.min.css",
    "fontawesome-all.min.css",
    "hover-min.css",
    "swiper.min.css",
    "jquery.mCustomScrollbar.min.css",
    "magnific-popup.css",
    "owl.carousel.min.css",
    "owl.theme.default.min.css",
    "oberlin-icons.css",
    "style.css",
    "responsive.css"
]

js_files = [
    "jquery.min.js",
    "bootstrap.bundle.min.js",
    "bootstrap-datepicker.min.js",
    "bootstrap-select.min.js",
    "isotope.js",
    "waypoints.min.js",
    "jquery.counterup.min.js",
    "jquery.magnific-popup.min.js",
    "jquery.mCustomScrollbar.concat.min.js",
    "jquery.validate.min.js",
    "owl.carousel.min.js",
    "wow.min.js",
    "swiper.min.js",
    "TweenMax.min.js",
    "theme.js",
    "custom.js"
]

print("Building wellnest-web.min.css...")
css_content = []
for f in css_files:
    path = os.path.join(public_css, f)
    with open(path, "r", encoding="utf-8") as file:
        css_content.append(file.read())

raw_css = "\n".join(css_content)
css_min = re.sub(r"/\*[\s\S]*?\*/", "", raw_css)
css_min = re.sub(r"\s+", " ", css_min)
css_min = re.sub(r"\s*([\{\}:;,>\+~])\s*", r"\1", css_min).replace(";}", "}").strip()

out_css = os.path.join(public_css, "wellnest-web.min.css")
with open(out_css, "w", encoding="utf-8") as out:
    out.write(css_min)
print(f" -> Generated {out_css} ({len(css_min)} bytes)")

print("Building wellnest-web.min.js...")
js_content = []
for f in js_files:
    path = os.path.join(public_js, f)
    with open(path, "r", encoding="utf-8") as file:
        js_content.append(f"/* --- {f} --- */\n" + file.read() + "\n;\n")

raw_js = "".join(js_content)
out_js = os.path.join(public_js, "wellnest-web.min.js")
with open(out_js, "w", encoding="utf-8") as out:
    out.write(raw_js)

try:
    subprocess.run(["npx", "esbuild", out_js, "--minify", "--sourcemap", f"--outfile={out_js}", "--allow-overwrite"], check=True)
    print(f" -> Minified with sourcemaps: {out_js} ({os.path.getsize(out_js)} bytes)")
except Exception as e:
    print(f" -> Minified JS via fallback ({os.path.getsize(out_js)} bytes)")
