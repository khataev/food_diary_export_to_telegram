#!/bin/bash

src_dir="$1"
dst_dir="$2"

if [[ -z "$src_dir" || -z "$dst_dir" ]]; then
  echo "Usage: $0 <source_directory> <destination_directory>"
  exit 1
fi

if [[ ! -d "$src_dir" ]]; then
  echo "Source directory does not exist: $src_dir"
  exit 2
fi

mkdir -p "$dst_dir"
shopt -s nullglob

for file in "$src_dir"/*.heic "$src_dir"/*.HEIC; do
  filename=$(basename "$file")
  base="${filename%.*}"
  dst_file="$dst_dir/${base}.jpg"

  echo "Converting $filename -> ${base}.jpg with quality 85 and max width 1920px"
  magick "$file" -quality 85 -resize 1920x "$dst_file"
done

echo "Conversion complete."

