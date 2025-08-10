#!/bin/bash

src_dir="$1"
dst_dir="$2"
DATE_NA="DATE_NA"

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
  # Извлекаем дату создания
  datetime=$(exiftool -DateTimeOriginal -d '%Y-%m-%dT%H:%M:%S' -s3 "$file")
  if [[ -z "$datetime" ]]; then
    datetime="$DATE_NA"
  fi
  
  filename=$(basename "$file")
  newname="${datetime}_${filename}"
  
  # Копируем файл, перезаписывая при коллизии
  cp -f "$file" "$dst_dir/$newname"
done

