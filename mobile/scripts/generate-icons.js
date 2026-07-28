const fs = require("node:fs");
const path = require("node:path");
const { PNG } = require("pngjs");

const SIZE = 1024;
const output = path.join(__dirname, "..", "assets");

function color(hex, alpha = 255) {
  const value = hex.replace("#", "");
  return [0, 2, 4].map((offset) => Number.parseInt(value.slice(offset, offset + 2), 16)).concat(alpha);
}

function pixel(image, x, y, rgba) {
  if (x < 0 || y < 0 || x >= image.width || y >= image.height) return;
  const index = (Math.floor(y) * image.width + Math.floor(x)) * 4;
  const alpha = rgba[3] / 255;
  const inverse = 1 - alpha;
  image.data[index] = Math.round(rgba[0] * alpha + image.data[index] * inverse);
  image.data[index + 1] = Math.round(rgba[1] * alpha + image.data[index + 1] * inverse);
  image.data[index + 2] = Math.round(rgba[2] * alpha + image.data[index + 2] * inverse);
  image.data[index + 3] = Math.round((alpha + (image.data[index + 3] / 255) * inverse) * 255);
}

function circle(image, cx, cy, radius, rgba) {
  for (let y = Math.max(0, Math.floor(cy - radius)); y <= Math.min(SIZE - 1, Math.ceil(cy + radius)); y += 1) {
    for (let x = Math.max(0, Math.floor(cx - radius)); x <= Math.min(SIZE - 1, Math.ceil(cx + radius)); x += 1) {
      if ((x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2) pixel(image, x, y, rgba);
    }
  }
}

function ellipse(image, cx, cy, radiusX, radiusY, rgba) {
  for (let y = Math.max(0, Math.floor(cy - radiusY)); y <= Math.min(SIZE - 1, Math.ceil(cy + radiusY)); y += 1) {
    for (let x = Math.max(0, Math.floor(cx - radiusX)); x <= Math.min(SIZE - 1, Math.ceil(cx + radiusX)); x += 1) {
      if (((x - cx) / radiusX) ** 2 + ((y - cy) / radiusY) ** 2 <= 1) pixel(image, x, y, rgba);
    }
  }
}

function line(image, fromX, fromY, toX, toY, width, rgba) {
  const radius = width / 2;
  const deltaX = toX - fromX;
  const deltaY = toY - fromY;
  const lengthSquared = deltaX ** 2 + deltaY ** 2;
  for (let y = Math.floor(Math.min(fromY, toY) - radius); y <= Math.ceil(Math.max(fromY, toY) + radius); y += 1) {
    for (let x = Math.floor(Math.min(fromX, toX) - radius); x <= Math.ceil(Math.max(fromX, toX) + radius); x += 1) {
      const projection = Math.max(0, Math.min(1, ((x - fromX) * deltaX + (y - fromY) * deltaY) / lengthSquared));
      const nearestX = fromX + projection * deltaX;
      const nearestY = fromY + projection * deltaY;
      if ((x - nearestX) ** 2 + (y - nearestY) ** 2 <= radius ** 2) pixel(image, x, y, rgba);
    }
  }
}

function background(image) {
  const base = color("#070b10");
  const glow = color("#20281d");
  for (let y = 0; y < SIZE; y += 1) {
    for (let x = 0; x < SIZE; x += 1) {
      const distance = Math.min(1, Math.hypot(x - 470, y - 390) / 720);
      const index = (y * SIZE + x) * 4;
      for (let channel = 0; channel < 3; channel += 1) image.data[index + channel] = Math.round(glow[channel] * (1 - distance) + base[channel] * distance);
      image.data[index + 3] = 255;
    }
  }
}

function crescent(image, cx, cy, radius, scale) {
  const gold = color("#e5c86b");
  const cutX = cx + 82 * scale;
  const cutY = cy - 52 * scale;
  const cutRadius = radius * 0.83;
  for (let y = Math.floor(cy - radius); y <= Math.ceil(cy + radius); y += 1) {
    for (let x = Math.floor(cx - radius); x <= Math.ceil(cx + radius); x += 1) {
      const outer = (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2;
      const cut = (x - cutX) ** 2 + (y - cutY) ** 2 <= cutRadius ** 2;
      if (outer && !cut) pixel(image, x, y, gold);
    }
  }
}

function mark(image, scale = 1) {
  const green = color("#68d39f");
  crescent(image, 465, 430, 245 * scale, scale);
  circle(image, 710, 300, 25 * scale, color("#f3dc91"));
  circle(image, 760, 360, 11 * scale, color("#f3dc91", 190));
  line(image, 600, 715, 600, 520, 30 * scale, green);
  ellipse(image, 532, 548, 82 * scale, 44 * scale, green);
  ellipse(image, 678, 508, 88 * scale, 46 * scale, green);
  circle(image, 600, 520, 18 * scale, color("#17382b"));
}

function create(withBackground, scale) {
  const image = new PNG({ width: SIZE, height: SIZE, colorType: 6 });
  if (withBackground) background(image);
  mark(image, scale);
  return PNG.sync.write(image);
}

fs.mkdirSync(output, { recursive: true });
fs.writeFileSync(path.join(output, "icon.png"), create(true, 1));
fs.writeFileSync(path.join(output, "adaptive-icon.png"), create(false, 0.76));
fs.writeFileSync(path.join(output, "splash-icon.png"), create(false, 0.7));
