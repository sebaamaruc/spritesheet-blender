import bpy
import numpy as np
import os
from .composer import ComposerBackend

class NumpyComposer(ComposerBackend):
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
        if not frame_paths:
            print("NumpyComposer: No frame paths provided.")
            return False
            
        n_frames = len(frame_paths)
        rows, sheet_w, sheet_h = self.calculate_dimensions(
            n_frames, frame_width, frame_height, columns, padding, margin
        )
        
        if sheet_w <= 0 or sheet_h <= 0:
            print(f"NumpyComposer: Invalid calculated dimensions: {sheet_w}x{sheet_h}")
            return False
            
        # Allocate flat array for the final sheet (float32, RGBA)
        # Blender's image pixels are flat float arrays normalized [0.0, 1.0]
        sheet_pixels = np.zeros(sheet_h * sheet_w * 4, dtype=np.float32)
        if not transparent:
            # Set alpha channel to 1.0 for all pixels
            sheet_pixels[3::4] = 1.0
            
        # Reshape to 3D grid: (height, width, RGBA)
        sheet = sheet_pixels.reshape((sheet_h, sheet_w, 4))
        
        success = True
        loaded_images = []
        
        try:
            for idx, path in enumerate(frame_paths):
                if not os.path.exists(path):
                    print(f"NumpyComposer: Frame path does not exist: {path}")
                    success = False
                    break
                    
                # Load frame image
                frame_img = bpy.data.images.load(path, check_existing=False)
                loaded_images.append(frame_img)
                
                # Check dimensions
                img_w, img_h = frame_img.size
                
                # Retrieve pixel buffer from Blender image
                # NumPy foreach_get is extremely fast (C-level copy)
                frame_buf = np.empty(img_w * img_h * 4, dtype=np.float32)
                frame_img.pixels.foreach_get(frame_buf)
                frame_grid = frame_buf.reshape((img_h, img_w, 4))
                
                # Handle resize if dimensions mismatch (safety fallback)
                if img_w != frame_width or img_h != frame_height:
                    print(f"NumpyComposer: Warning - frame dimensions mismatch. Expected {frame_width}x{frame_height}, got {img_w}x{img_h}.")
                    # If mismatch, we try to slice/crop or stretch it. Let's crop/pad or just slice
                    # as safety fallback. Usually they will match because we render them at frame_width/frame_height.
                    temp_grid = np.zeros((frame_height, frame_width, 4), dtype=np.float32)
                    copy_w = min(img_w, frame_width)
                    copy_h = min(img_h, frame_height)
                    temp_grid[0:copy_h, 0:copy_w, :] = frame_grid[0:copy_h, 0:copy_w, :]
                    frame_grid = temp_grid
                
                # Calculate grid coordinates
                col = idx % columns
                row = idx // columns
                
                x = margin + col * (frame_width + padding)
                # Blender coordinates are bottom-up, invert Row mapping
                y = sheet_h - margin - (row + 1) * frame_height - row * padding
                
                # Paste frame pixels into spritesheet buffer
                sheet[y : y + frame_height, x : x + frame_width, :] = frame_grid
                
        except Exception as e:
            print(f"NumpyComposer: Error during composition: {e}")
            success = False
        finally:
            # Clean up loaded images to free memory
            for img in loaded_images:
                bpy.data.images.remove(img)
                
        if not success:
            return False
            
        # Write sheet buffer back to a new Blender image block to save it properly
        result_img = bpy.data.images.new("SPRITESHEET_COMPOSED_OUTPUT", width=sheet_w, height=sheet_h, alpha=True)
        try:
            # Flatten array back and set
            result_img.pixels.foreach_set(sheet.ravel())
            result_img.update()
            
            # Setup path and save
            result_img.filepath_raw = output_path
            result_img.file_format = 'PNG'
            result_img.save()
            return True
        except Exception as e:
            print(f"NumpyComposer: Error saving output image: {e}")
            return False
        finally:
            # Clean up output image block
            bpy.data.images.remove(result_img)
