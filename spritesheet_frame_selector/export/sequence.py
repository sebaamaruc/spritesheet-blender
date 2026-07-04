"""Individual frame sequence export helpers."""

from __future__ import annotations

import os
import re
import shutil


def export_individual_frames(
    frame_paths: list[str],
    sequence_folder: str,
    sheet_name: str,
) -> None:
    os.makedirs(sequence_folder, exist_ok=True)
    clear_previous_individual_frames(sequence_folder, sheet_name)
    for output_index, source_path in enumerate(frame_paths, start=1):
        if output_index > 999:
            raise ValueError("Individual frame export supports up to 999 frames")
        target_path = os.path.join(
            sequence_folder,
            individual_frame_file_name(sheet_name, output_index),
        )
        if os.path.abspath(source_path) == os.path.abspath(target_path):
            continue
        shutil.copyfile(source_path, target_path)


def clear_previous_individual_frames(sequence_folder: str, sheet_name: str) -> None:
    pattern = re.compile(rf"^{re.escape(sheet_name)}_frame_(\d{{3}}|\d{{6}})\.png$")
    for file_name in os.listdir(sequence_folder):
        if pattern.match(file_name):
            os.remove(os.path.join(sequence_folder, file_name))


def individual_frame_file_name(sheet_name: str, frame_index: int) -> str:
    return f"{sheet_name}_frame_{frame_index:03d}.png"
