import asyncio
import requests
import os
from pyppeteer import launch
from pyppeteer.page import Page
import colorsys

layer_keys = [
    'mini_base', 'pet', 'cloak', 'off_hand', 'body', 'hair', 'face', 'legs',
    'feet', 'chest', 'head', 'head_2', 'waist', 'hands', 'main_hand', 'horns', 'wings',
    'tattoo', 'ears', 'tail',
]

url = "https://api.reroll.co/api/characters/Strackeror/1836070"

os.makedirs("./output", exist_ok=True)

data = requests.get(url).json()
layers = data["layers_visibility"]
name = data["name"]

render_tasks = []

for key in layer_keys:
  if key not in data or data[key] is None:
    continue
  layer_entry = data[key]

  hsl = {}
  if "hsl" in layer_entry:
    hsl = layer_entry["hsl"]
  elif f"{key}_hsl" in data:
    hsl = data[f"{key}_hsl"]

  tint = {}
  if "tint" in layer_entry:
    tint = layer_entry["tint"]
  elif f"{key}_tint" in data:
    tint = data[f"{key}_tint"]

  tint["rgb"] = colorsys.hls_to_rgb(tint["h"] / 360, 0.5, 1)
  tint["rgb"] = [c * tint["b"] for c in tint["rgb"]]

  index = 0
  if key in layers:
    index = layers[key]["index"]

  image_url = ""
  if "image_url" in layer_entry:
    image_url = layer_entry["image_url"]
  elif "asset" in layer_entry and "image_url" in layer_entry["asset"]:
    image_url = layer_entry["asset"]["image_url"]
  if not image_url:
    continue

  render_html= f"""
  <div>
    <div style="
      filter: hue-rotate({hsl["h"]}deg) saturate({hsl["s"]}) brightness({hsl["l"]}); 
      background-image: url(&quot;{image_url}&quot;);
    ">
    </div>
    <div>
      <div style="
        filter: grayscale({tint["s"]}) invert({tint["invert"]}) url(&quot;#tint_head_289_1_1&quot;); opacity: {tint["o"]}; 
        background-image: url(&quot;{image_url}&quot;);
      "/>
      <svg>
        <filter id="tint_head_289_1_1" color-interpolation-filters="sRGB" x="0" y="0" height="100%"
          width="100%">
          <feComponentTransfer>
            <feFuncR tableValues="{tint["rgb"][0]} 1" type="table"></feFuncR>
            <feFuncG tableValues="{tint["rgb"][1]} 1" type="table"></feFuncG>
            <feFuncB tableValues="{tint["rgb"][2]} 1" type="table"></feFuncB>
          </feComponentTransfer>
        </filter>
      </svg>
    </div>
  </div>
  <style>
    div div {{
      width: 512px;
      height: 512px;
      position:absolute
    }}
  </style>
  """
  path = f"./output/{name}_{index}_{key}.png"
  render_tasks.append([path, render_html])


async def output_image(page: Page, path, render_html):
  await page.goto(f"data:text/html,{render_html}", waitUntil="networkidle0")
  await page.screenshot(path=path, clip={"width":540, "height":540, "x":0, "y":0}, omitBackground=True)
  print(f"wrote to {path}")

async def output_all(render_tasks):
  browser = await launch()
  page = await browser.newPage()
  for taks in render_tasks:
    await output_image(page, taks[0], taks[1])
  await browser.close()

asyncio.run(output_all(render_tasks))
