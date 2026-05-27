from abc import ABC, abstractmethod

class ComposerBackend(ABC):
    @abstractmethod
    def compose(
        self,
        frame_paths: list[str],
        frame_width: int,
        frame_height: int,
        columns: int,
        padding: int = 0,
        margin: int = 0,
        output_path: str = "",
        transparent: bool = True,
    ) -> bool:
        """Composes a spritesheet PNG from a list of image file paths.
        
        Args:
            frame_paths: Ordered list of absolute file paths to individual frame images.
            frame_width: Resized target width of each frame on the spritesheet.
            frame_height: Resized target height of each frame on the spritesheet.
            columns: Number of columns in the spritesheet grid.
            padding: Padding pixels between adjacent frames.
            margin: Margin pixels around the entire spritesheet border.
            output_path: Absolute destination path for the composed PNG.
            transparent: Whether to compose with transparent alpha channel.
            
        Returns:
            True if composition was successful, False otherwise.
        """
        pass

    def calculate_dimensions(self, n_frames, frame_w, frame_h, columns, padding, margin):
        """Calculates rows, sheet width, and sheet height for the spritesheet grid.
        
        Blender coordinates are bottom-up, so we arrange rows starting from the top.
        """
        if n_frames <= 0 or columns <= 0:
            return 0, 0, 0
            
        rows = (n_frames + columns - 1) // columns
        sheet_w = margin * 2 + columns * frame_w + max(0, columns - 1) * padding
        sheet_h = margin * 2 + rows * frame_h + max(0, rows - 1) * padding
        
        return rows, sheet_w, sheet_h
