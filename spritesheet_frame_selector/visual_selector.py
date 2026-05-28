import bpy
import gpu
import blf
import os
from gpu_extras.batch import batch_for_shader
from gpu_extras.presets import draw_texture_2d

# Centralized UI configuration and safe area settings
UI_SAFE_AREA = {
    'padding_left': 10,   # Safety padding from left region boundary
    'padding_right': 10,  # Safety padding from right region boundary
    'padding_top': 10,    # Safety padding from top region boundary
    'padding_bottom': 10  # Safety padding from bottom region boundary
}

# Centralized UI layout configuration
UI_LAYOUT = {
    'header_height_wide': 45,
    'header_height_narrow': 70,
    'footer_height': 35,
    'padding': 12,
    'grid_padding_x': 20,
    'grid_padding_y': 10,
    'cell_width': 80,
    'cell_height': 100,
    'buttons_in_header': True  # Set to False to display toolbar buttons at the bottom (footer)
}



class SPRITESHEET_OT_visual_selector(bpy.types.Operator):
    bl_idname = "spritesheet.visual_selector"
    bl_label = "Visual Frame Selector"
    bl_description = "Select animation frames visually in an interactive grid"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if len(scene.spritesheet_clips) == 0:
            return False
        clip = scene.spritesheet_clips[scene.active_clip_index]
        return len(clip.frames) > 0

    def load_previews(self, clip):
        """Loads preview images from disk into Blender images collection for drawing"""
        for frame in clip.frames:
            if frame.preview_path and os.path.exists(frame.preview_path):
                img_name = f"__spritesheet_preview_{clip.name}_{frame.frame_number}"
                # Load or reuse
                img = bpy.data.images.get(img_name)
                if not img:
                    try:
                        img = bpy.data.images.load(frame.preview_path, check_existing=True)
                        img.name = img_name
                    except Exception as e:
                        print(f"Error loading preview for frame {frame.frame_number}: {e}")
                        continue
                self.preview_images[frame.frame_number] = img

    def unload_previews(self):
        """Removes temporary preview images from Blender's memory"""
        for img in self.preview_images.values():
            if img:
                bpy.data.images.remove(img)
        self.preview_images.clear()

    def get_visible_frames_layout(self, width, height, clip, context):
        """Calculates grid layout positions for all frames based on region geometry"""
        n_frames = len(clip.frames)
        
        # 1. Identify base window region and other regions
        window_region = context.region
        for r in context.area.regions:
            if r.type == 'WINDOW':
                window_region = r
                break
                
        w_x = window_region.x
        w_y = window_region.y
        w_w = window_region.width
        w_h = window_region.height
        
        usable_x_min = 0
        usable_x_max = w_w
        usable_y_min = 0
        usable_y_max = w_h
        
        # Check overlaps of all other regions relative to WINDOW region
        for r in context.area.regions:
            if r == window_region:
                continue
            if r.width <= 1 or r.height <= 1:
                continue
                
            r_x_start = r.x - w_x
            r_x_end = r_x_start + r.width
            r_y_start = r.y - w_y
            r_y_end = r_y_start + r.height
            
            if r.type == 'UI': # N-Panel (usually on the right)
                if r_x_start > 0:
                    usable_x_max = min(usable_x_max, r_x_start)
            elif r.type == 'TOOLS': # Toolbar (usually on the left)
                if r_x_start <= 0:
                    usable_x_min = max(usable_x_min, r_x_end)
            elif r.type in {'HEADER', 'TOOL_HEADER'}:
                if r_y_start > 0:
                    usable_y_max = min(usable_y_max, r_y_start)
                else:
                    usable_y_min = max(usable_y_min, r_y_end)
            elif r.type == 'FOOTER':
                if r_y_start > 0:
                    usable_y_max = min(usable_y_max, r_y_start)
                else:
                    usable_y_min = max(usable_y_min, r_y_end)
                    
        # 2. Apply centralized UI safe area padding
        self.x_start = usable_x_min + UI_SAFE_AREA['padding_left']
        self.avail_width = max(100, usable_x_max - usable_x_min - UI_SAFE_AREA['padding_left'] - UI_SAFE_AREA['padding_right'])
        self.y_start = usable_y_min + UI_SAFE_AREA['padding_bottom']
        self.avail_height = max(100, usable_y_max - usable_y_min - UI_SAFE_AREA['padding_top'] - UI_SAFE_AREA['padding_bottom'])
        
        # 3. Dynamic header and footer sizes based on narrow/wide layout and button location
        is_narrow = (self.avail_width < 720)
        buttons_height = UI_LAYOUT['header_height_narrow'] if is_narrow else UI_LAYOUT['header_height_wide']
        simple_height = UI_LAYOUT['footer_height']
        
        if UI_LAYOUT.get('buttons_in_header', True):
            self.y_header_height = buttons_height
            self.y_footer_height = simple_height
        else:
            self.y_header_height = simple_height
            self.y_footer_height = buttons_height
        
        # Determine dynamic viewer height based on available viewport height
        if self.avail_height >= 700:
            self.y_viewer_height = 200
        elif self.avail_height >= 450:
            self.y_viewer_height = 140
        else:
            self.y_viewer_height = 0  # Collapsed / small viewport
            
        # Calculate vertical segments
        self.y_footer_start = self.y_start
        self.y_grid_start = self.y_footer_start + self.y_footer_height
        self.y_header_start = self.y_start + self.avail_height - self.y_header_height
        self.y_viewer_start = self.y_header_start - self.y_viewer_height
        self.y_grid_height = self.y_viewer_start - self.y_grid_start
        
        # Backward compatibility aliases for panels / general logic
        self.margin_top = self.y_header_height
        self.margin_bottom = self.y_footer_height
        self.viewer_height = self.y_viewer_height
            
        # Grid parameters: dynamic columns based on avail_width
        cols = max(1, (self.avail_width - 40) // (self.cell_w + self.padding))
        margin_left = self.x_start + (self.avail_width - (cols * (self.cell_w + self.padding) - self.padding)) // 2
        
        rows = (n_frames + cols - 1) // cols
        grid_h = rows * (self.cell_h + self.padding) - self.padding
        display_h = self.y_grid_height - 20
        self.max_scroll_y = max(0, grid_h - display_h)
        
        # Clamp scroll
        self.scroll_y = max(0, min(self.scroll_y, self.max_scroll_y))
        
        layout_items = []
        for i, frame in enumerate(clip.frames):
            col = i % cols
            row = i // cols
            
            x = margin_left + col * (self.cell_w + self.padding)
            # Y coord relative to available grid area start
            y = self.y_viewer_start - UI_LAYOUT['grid_padding_y'] - (row + 1) * (self.cell_h + self.padding) + self.scroll_y
            
            layout_items.append({
                'index': i,
                'frame_number': frame.frame_number,
                'selected': frame.selected,
                'x': x,
                'y': y,
                'w': self.cell_w,
                'h': self.cell_h,
            })
            
        return layout_items

    def hit_test(self, x, y, layout_items):
        """Returns the frame index under the coordinates (x, y) or -1"""
        for item in layout_items:
            if (item['x'] <= x <= item['x'] + item['w']) and (item['y'] <= y <= item['y'] + item['h']):
                # Hit-test only active within display bounds of the grid
                if hasattr(self, 'y_grid_start') and hasattr(self, 'y_grid_height'):
                    if self.y_grid_start <= y <= (self.y_grid_start + self.y_grid_height):
                        if self.x_start <= x <= (self.x_start + self.avail_width):
                            return item['index']
                else:
                    return item['index']
        return -1

    def draw_rect(self, x, y, w, h, color):
        """Draws a solid colored rectangle"""
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        vertices = ((x, y), (x + w, y), (x + w, y + h), (x, y + h))
        indices = ((0, 1, 2), (2, 3, 0))
        batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)
        shader.bind()
        shader.uniform_float("color", color)
        batch.draw(shader)

    def get_header_buttons(self, width, height, clip):
        buttons = []
        is_narrow = (self.avail_width < 720)
        
        if UI_LAYOUT.get('buttons_in_header', True):
            buttons_y_start = self.y_header_start
        else:
            buttons_y_start = self.y_footer_start
        
        # Row 1 coordinates
        y_min_1 = buttons_y_start + 40 if is_narrow else buttons_y_start + 12
        y_max_1 = buttons_y_start + 65 if is_narrow else buttons_y_start + 38
        
        # Row 2 coordinates (only if narrow)
        y_min_2 = buttons_y_start + 10
        y_max_2 = buttons_y_start + 35
        
        # Row 1 buttons: Playback & Speed Controls
        x = self.x_start + 15
        def add_btn(btn_id, text, w):
            nonlocal x
            buttons.append({'id': btn_id, 'text': text, 'x_min': x, 'x_max': x + w, 'y_min': y_min_1, 'y_max': y_max_1})
            x += w + 10
            
        play_text = "Pause" if self.is_playing else "Play"
        add_btn('PLAY_PAUSE', play_text, 65)
        add_btn('STEP_L', "< Prev", 60)
        add_btn('STEP_R', "Next >", 60)
        add_btn('SET_FPS', f"FPS: {clip.fps}", 70)
        
        # Row 2 or continuation of Row 1
        if is_narrow:
            x_2 = self.x_start + 15
            def add_btn_row2(btn_id, text, w):
                nonlocal x_2
                buttons.append({'id': btn_id, 'text': text, 'x_min': x_2, 'x_max': x_2 + w, 'y_min': y_min_2, 'y_max': y_max_2})
                x_2 += w + 10
            add_btn_row2('SELECT_ALL', "All", 45)
            add_btn_row2('DESELECT_ALL', "None", 45)
            add_btn_row2('INVERT', "Invert", 55)
            every_n_val = self._every_n_state if hasattr(self, '_every_n_state') else 2
            add_btn_row2('EVERY_N', f"Evr {every_n_val}", 65)
            # Close button anchored to right
            buttons.append({'id': 'CLOSE', 'text': "Close (X)", 'x_min': self.x_start + self.avail_width - 85, 'x_max': self.x_start + self.avail_width - 15, 'y_min': y_min_2, 'y_max': y_max_2})
        else:
            add_btn('SELECT_ALL', "All", 45)
            add_btn('DESELECT_ALL', "None", 45)
            add_btn('INVERT', "Invert", 55)
            every_n_val = self._every_n_state if hasattr(self, '_every_n_state') else 2
            add_btn('EVERY_N', f"Every {every_n_val}", 75)
            # Close button anchored to right
            buttons.append({'id': 'CLOSE', 'text': "Close (X)", 'x_min': self.x_start + self.avail_width - 95, 'x_max': self.x_start + self.avail_width - 15, 'y_min': y_min_1, 'y_max': y_max_1})
            
        return buttons

    def draw_header_buttons(self, width, height, clip):
        buttons = self.get_header_buttons(width, height, clip)
        font_id = 0
        blf.size(font_id, 12)
        
        for btn in buttons:
            is_hovered = (btn['x_min'] <= self.mouse_x <= btn['x_max']) and (btn['y_min'] <= self.mouse_y <= btn['y_max'])
            
            if btn['id'] == 'CLOSE':
                bg_color = (0.7, 0.2, 0.2, 1.0) if is_hovered else (0.5, 0.15, 0.15, 1.0)
                text_color = (1.0, 1.0, 1.0, 1.0)
            elif btn['id'] == 'PLAY_PAUSE' and self.is_playing:
                bg_color = (0.2, 0.5, 0.2, 1.0) if is_hovered else (0.15, 0.4, 0.15, 1.0)
                text_color = (1.0, 1.0, 1.0, 1.0)
            else:
                bg_color = (0.25, 0.25, 0.25, 1.0) if is_hovered else (0.18, 0.18, 0.18, 1.0)
                text_color = (0.9, 0.9, 0.9, 1.0)
                
            w = btn['x_max'] - btn['x_min']
            h = btn['y_max'] - btn['y_min']
            
            self.draw_rect(btn['x_min'], btn['y_min'], w, h, bg_color)
            
            # Subtle border
            border_color = (0.4, 0.4, 0.4, 1.0) if is_hovered else (0.25, 0.25, 0.25, 1.0)
            self.draw_rect(btn['x_min'], btn['y_min'], w, 1, border_color)
            self.draw_rect(btn['x_min'], btn['y_max'] - 1, w, 1, border_color)
            self.draw_rect(btn['x_min'], btn['y_min'], 1, h, border_color)
            self.draw_rect(btn['x_max'] - 1, btn['y_min'], 1, h, border_color)
            
            lbl_w, lbl_h = blf.dimensions(font_id, btn['text'])
            blf.color(font_id, *text_color)
            text_x = btn['x_min'] + (w - lbl_w) / 2
            text_y = btn['y_min'] + (h - lbl_h) / 2 - 1
            blf.position(font_id, text_x, text_y, 0)
            blf.draw(font_id, btn['text'])

    def execute_header_button(self, context, btn_id, clip):
        if btn_id == 'PLAY_PAUSE':
            self.toggle_playback(clip)
        elif btn_id == 'STEP_L':
            self.step_playback(clip, -1)
        elif btn_id == 'STEP_R':
            self.step_playback(clip, 1)
        elif btn_id == 'SET_FPS':
            if self.is_playing:
                self.toggle_playback(clip)
            bpy.ops.spritesheet.set_playback_fps('INVOKE_DEFAULT')
        elif btn_id == 'SELECT_ALL':
            for f in clip.frames:
                f.selected = True
            self.report({'INFO'}, "Selected all frames")
        elif btn_id == 'DESELECT_ALL':
            for f in clip.frames:
                f.selected = False
            if self.is_playing:
                self.toggle_playback(clip)
            self.report({'INFO'}, "Deselected all frames")
        elif btn_id == 'INVERT':
            for f in clip.frames:
                f.selected = not f.selected
            self.report({'INFO'}, "Inverted selection")
        elif btn_id == 'EVERY_N':
            if not hasattr(self, '_every_n_state'):
                self._every_n_state = 2
            else:
                self._every_n_state = (self._every_n_state % 5) + 1
                if self._every_n_state == 1:
                    self._every_n_state = 2
            for i, f in enumerate(clip.frames):
                f.selected = (i % self._every_n_state == 0)
            self.report({'INFO'}, f"Selected every {self._every_n_state} frames")

    def close_modal(self, context):
        """Clean close sequence of the modal operator"""
        if self.is_playing:
            self.is_playing = False
            try:
                bpy.app.timers.unregister(self.handle_playback_tick)
            except:
                pass
        if self._handle:
            try:
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            except:
                pass
            self._handle = None
        self.unload_previews()
        context.area.tag_redraw()

    def draw_header_footer(self, width, height, clip, selected_count, total_count):
        """Draws header and footer overlays with labels and shortcuts"""
        # Header (Top background)
        self.draw_rect(self.x_start, self.y_header_start, self.avail_width, self.y_header_height, (0.09, 0.09, 0.09, 0.99))
        # Divider line
        self.draw_rect(self.x_start, self.y_header_start - 1, self.avail_width, 1, (0.2, 0.2, 0.2, 1.0))
        
        # Footer (Bottom background)
        self.draw_rect(self.x_start, self.y_footer_start, self.avail_width, self.y_footer_height, (0.09, 0.09, 0.09, 0.99))
        # Divider line (above footer if buttons are in footer, otherwise at the top of footer)
        self.draw_rect(self.x_start, self.y_footer_start + self.y_footer_height, self.avail_width, 1, (0.2, 0.2, 0.2, 1.0))
        
        # Draw buttons in their designated area
        self.draw_header_buttons(width, height, clip)
        
        font_id = 0
        lbl = "Shortcuts: [Space] Play/Pause | [Left/Right] Step | [A] All | [D] None | [I] Invert | [ESC] Close"
        
        if UI_LAYOUT.get('buttons_in_header', True):
            # Header text (clip title next to controls if space permits)
            if self.avail_width >= 800:
                blf.size(font_id, 14)
                blf.color(font_id, 1, 1, 1, 1)
                title_str = f"Clip: {clip.name}"
                lbl_w, lbl_h = blf.dimensions(font_id, title_str)
                title_x = self.x_start + self.avail_width - 120 - lbl_w
                # Center title text vertically in header
                title_y = self.y_header_start + (self.y_header_height - lbl_h) / 2
                blf.position(font_id, title_x, title_y, 0)
                blf.draw(font_id, title_str)
                
            # Footer text - Shortcuts info (centered in available footer width)
            blf.size(font_id, 11)
            blf.color(font_id, 0.7, 0.7, 0.7, 1.0)
            lbl_w, lbl_h = blf.dimensions(font_id, lbl)
            text_x = self.x_start + (self.avail_width - lbl_w) / 2
            text_y = self.y_footer_start + (self.y_footer_height - lbl_h) / 2 - 1
            blf.position(font_id, text_x, text_y, 0)
            blf.draw(font_id, lbl)
        else:
            # Header text (clip title centered)
            blf.size(font_id, 14)
            blf.color(font_id, 1, 1, 1, 1)
            title_str = f"Clip: {clip.name}"
            lbl_w, lbl_h = blf.dimensions(font_id, title_str)
            title_x = self.x_start + (self.avail_width - lbl_w) / 2
            title_y = self.y_header_start + (self.y_header_height - lbl_h) / 2
            blf.position(font_id, title_x, title_y, 0)
            blf.draw(font_id, title_str)
            
            # Header text - Shortcuts info on the left of Header if space permits
            if self.avail_width >= 800:
                blf.size(font_id, 11)
                blf.color(font_id, 0.7, 0.7, 0.7, 1.0)
                _, lbl_h = blf.dimensions(font_id, lbl)
                text_x = self.x_start + 15
                text_y = self.y_header_start + (self.y_header_height - lbl_h) / 2
                blf.position(font_id, text_x, text_y, 0)
                blf.draw(font_id, lbl)

    def draw_callback(self, context):
        """Draw handler callback"""
        region = context.region
        width = region.width
        height = region.height
        
        clip = context.scene.spritesheet_clips[context.scene.active_clip_index]
        layout_items = self.get_visible_frames_layout(width, height, clip, context)
        
        # Force GPU depth test and depth mask state for 2D UI drawing
        gpu.state.depth_test_set('NONE')
        gpu.state.depth_mask_set(False)
        
        # Disable blending for the solid main background to block the 3D viewport completely
        gpu.state.blend_set('NONE')
        
        # Draw solid dark main background covering the entire selector area
        self.draw_rect(self.x_start, self.y_start, self.avail_width, self.avail_height, (0.06, 0.06, 0.06, 0.98))
        
        # Re-enable alpha blending for subsequent textured/text elements
        gpu.state.blend_set('ALPHA')
        
        # 2. Draw Grid Items
        selected_count = 0
        for item in layout_items:
            if item['selected']:
                selected_count += 1
                
            # Culling - only draw if inside visible region of the grid
            grid_bottom = self.y_grid_start
            grid_top = self.y_grid_start + self.y_grid_height
            if (item['y'] + item['h'] < grid_bottom) or (item['y'] > grid_top):
                continue
                
            # Card background
            bg_color = (0.15, 0.15, 0.15, 0.9)
            if item['index'] == self.last_hovered_idx:
                bg_color = (0.22, 0.22, 0.22, 0.9)
            self.draw_rect(item['x'], item['y'], item['w'], item['h'], bg_color)
            
            # Selection Border or Highlight
            border_w = 3
            if item['selected']:
                # Bright selection border
                self.draw_rect(item['x'], item['y'] + 20, item['w'], border_w, (0.0, 0.6, 1.0, 1.0)) # Top of thumbnail
                self.draw_rect(item['x'], item['y'] + 20, border_w, item['h'] - 20, (0.0, 0.6, 1.0, 1.0)) # Left
                self.draw_rect(item['x'] + item['w'] - border_w, item['y'] + 20, border_w, item['h'] - 20, (0.0, 0.6, 1.0, 1.0)) # Right
                self.draw_rect(item['x'], item['y'] + item['h'] - border_w, item['w'], border_w, (0.0, 0.6, 1.0, 1.0)) # Top
            else:
                # Dim overlay for unselected frames
                pass
            
            # Draw Preview Image (Thumbnail)
            img = self.preview_images.get(item['frame_number'])
            preview_sz = int(clip.preview_size)
            # Offset inside cell: center thumbnail
            thumb_w = min(item['w'] - 10, preview_sz)
            thumb_h = min(item['w'] - 10, preview_sz) # keep square
            thumb_x = item['x'] + (item['w'] - thumb_w) // 2
            thumb_y = item['y'] + 25 + (item['h'] - 25 - thumb_h) // 2
            
            # Draw solid dark background under transparent preview to enhance readability
            self.draw_rect(thumb_x, thumb_y, thumb_w, thumb_h, (0.12, 0.12, 0.12, 1.0))
            
            if img:
                try:
                    texture = gpu.texture.from_image(img)
                    # Disable writing to alpha channel to prevent transparent pixels from clearing the opaque cell background alpha
                    gpu.state.color_mask_set(True, True, True, False)
                    draw_texture_2d(texture, (thumb_x, thumb_y), thumb_w, thumb_h)
                    gpu.state.color_mask_set(True, True, True, True)
                except Exception as e:
                    # Draw placeholder gray box
                    self.draw_rect(thumb_x, thumb_y, thumb_w, thumb_h, (0.25, 0.25, 0.25, 1.0))
            else:
                # Draw placeholder box
                self.draw_rect(thumb_x, thumb_y, thumb_w, thumb_h, (0.25, 0.25, 0.25, 1.0))
                
            # Dim the thumbnail itself if not selected
            if not item['selected']:
                # Draw semi-transparent dark overlay on thumbnail
                self.draw_rect(thumb_x, thumb_y, thumb_w, thumb_h, (0.0, 0.0, 0.0, 0.55))
            
            # Playback Highlight (Golden border when playing, Blue border when paused) — drawn AFTER thumbnail so it's visible
            if item['index'] == self.playback_index:
                border = 3
                color = (1.0, 0.8, 0.0, 1.0) if self.is_playing else (0.0, 0.6, 1.0, 1.0)
                self.draw_rect(item['x'] - border, item['y'] + 20 - border, item['w'] + border * 2, border, color)
                self.draw_rect(item['x'] - border, item['y'] + 20 - border, border, item['h'] - 20 + border * 2, color)
                self.draw_rect(item['x'] + item['w'], item['y'] + 20 - border, border, item['h'] - 20 + border * 2, color)
                self.draw_rect(item['x'] - border, item['y'] + item['h'], item['w'] + border * 2, border, color)
                
            # Frame label
            font_id = 0
            blf.size(font_id, 11)
            lbl = f"Frame {item['frame_number']}"
            lbl_w, lbl_h = blf.dimensions(font_id, lbl)
            
            # Position centered at bottom of cell
            blf.position(font_id, item['x'] + (item['w'] - lbl_w) / 2, item['y'] + 6, 0)
            if item['selected']:
                blf.color(font_id, 0.0, 0.8, 1.0, 1.0)
            else:
                blf.color(font_id, 0.6, 0.6, 0.6, 1.0)
            blf.draw(font_id, lbl)
            
        # 3. Draw Playback Viewer (if enabled)
        self.draw_playback_viewer(width, height, clip)

        # 4. Draw Header/Footer (drawn last so they are on top of cells during scroll)
        self.draw_header_footer(width, height, clip, selected_count, len(clip.frames))
        
        # Restore GPU states to default
        gpu.state.depth_mask_set(True)
        gpu.state.blend_set('NONE')

    def draw_playback_viewer(self, width, height, clip):
        """Draws the large preview viewer for playback animation at the top"""
        if self.viewer_height <= 0:
            return
            
        # 1. Background box for viewer area (strictly within available width)
        viewer_y_start = self.y_viewer_start
        self.draw_rect(self.x_start, viewer_y_start, self.avail_width, self.y_viewer_height, (0.08, 0.08, 0.08, 0.99))
        # Divider line at the bottom of the viewer area
        self.draw_rect(self.x_start, viewer_y_start, self.avail_width, 1, (0.2, 0.2, 0.2, 1.0))
        
        # 2. Determine which frame to show
        preview_frame_idx = -1
        if self.is_playing:
            preview_frame_idx = self.playback_index
        elif self.last_hovered_idx != -1:
            preview_frame_idx = self.last_hovered_idx
        else:
            preview_frame_idx = self.playback_index
            
        if preview_frame_idx < 0 or preview_frame_idx >= len(clip.frames):
            selected_indices = [i for i, f in enumerate(clip.frames) if f.selected]
            if selected_indices:
                preview_frame_idx = selected_indices[0]
            else:
                preview_frame_idx = 0
                
        if not clip.frames:
            return
            
        frame_item = clip.frames[preview_frame_idx]
        
        # 3. Calculate large preview dimensions (centered in available width)
        preview_sz = 160 if self.y_viewer_height == 200 else 110
        preview_x = self.x_start + (self.avail_width - preview_sz) // 2
        preview_y = viewer_y_start + (self.y_viewer_height - preview_sz) // 2
        
        # Draw solid dark background under transparent preview to enhance readability
        self.draw_rect(preview_x, preview_y, preview_sz, preview_sz, (0.12, 0.12, 0.12, 1.0))
        
        # Draw image or gray placeholder
        img = self.preview_images.get(frame_item.frame_number)
        if img:
            try:
                texture = gpu.texture.from_image(img)
                # Disable writing to alpha channel to prevent transparent pixels from clearing the opaque viewer background alpha
                gpu.state.color_mask_set(True, True, True, False)
                draw_texture_2d(texture, (preview_x, preview_y), preview_sz, preview_sz)
                gpu.state.color_mask_set(True, True, True, True)
            except Exception as e:
                self.draw_rect(preview_x, preview_y, preview_sz, preview_sz, (0.25, 0.25, 0.25, 1.0))
        else:
            self.draw_rect(preview_x, preview_y, preview_sz, preview_sz, (0.25, 0.25, 0.25, 1.0))
            
        # Draw a frame border around the preview image (gold if playing, blue if paused)
        border_color = (1.0, 0.8, 0.0, 1.0) if self.is_playing else (0.0, 0.6, 1.0, 0.8)
        border_w = 2
        self.draw_rect(preview_x - border_w, preview_y - border_w, preview_sz + border_w * 2, border_w, border_color) # Bottom
        self.draw_rect(preview_x - border_w, preview_y + preview_sz, preview_sz + border_w * 2, border_w, border_color) # Top
        self.draw_rect(preview_x - border_w, preview_y, border_w, preview_sz, border_color) # Left
        self.draw_rect(preview_x + preview_sz, preview_y, border_w, preview_sz, border_color) # Right
        
        # 4. Draw texts
        font_id = 0
        blf.size(font_id, 12)
        
        # Draw text only if available space is wide enough to avoid overlap
        if self.avail_width >= 500:
            # Left side texts (Status & Active Frame)
            status_str = "STATUS: PLAYING" if self.is_playing else "STATUS: PAUSED"
            if self.is_playing:
                blf.color(font_id, 0.2, 0.8, 0.2, 1.0)
            else:
                blf.color(font_id, 0.6, 0.6, 0.6, 1.0)
                
            text_y_status = viewer_y_start + self.viewer_height // 2 + 10
            text_y_frame = viewer_y_start + self.viewer_height // 2 - 15
            
            blf.position(font_id, preview_x - 180, text_y_status, 0)
            blf.draw(font_id, status_str)
            
            blf.color(font_id, 0.9, 0.9, 0.9, 1.0)
            blf.position(font_id, preview_x - 180, text_y_frame, 0)
            
            src_label = " (Hover)" if (not self.is_playing and preview_frame_idx == self.last_hovered_idx) else ""
            blf.draw(font_id, f"FRAME: {frame_item.frame_number}{src_label}")
            
            # Right side texts (Selection Info & FPS)
            selected_count = sum(1 for f in clip.frames if f.selected)
            blf.position(font_id, preview_x + preview_sz + 40, text_y_status, 0)
            blf.draw(font_id, f"SELECTED: {selected_count} / {len(clip.frames)}")
            
            blf.position(font_id, preview_x + preview_sz + 40, text_y_frame, 0)
            blf.draw(font_id, f"SPEED: {clip.fps} FPS")

    def handle_playback_tick(self):
        """Timer callback for playback preview"""
        if not self.is_playing:
            return None # Stop timer
            
        clip = bpy.context.scene.spritesheet_clips[bpy.context.scene.active_clip_index]
        selected_indices = [i for i, f in enumerate(clip.frames) if f.selected]
        
        if not selected_indices:
            self.is_playing = False
            self.playback_index = 0
            return None
            
        # Advance index
        if hasattr(self, '_playback_list_pos'):
            self._playback_list_pos = (self._playback_list_pos + 1) % len(selected_indices)
        else:
            self._playback_list_pos = 0
            
        self.playback_index = selected_indices[self._playback_list_pos]
        
        # Redraw viewport to show updated index highlight
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
                
        # Return next tick time based on active clip FPS
        return 1.0 / clip.fps

    def toggle_playback(self, clip):
        """Starts or stops the timer-based playback preview"""
        if self.is_playing:
            self.is_playing = False
            if self.playback_timer:
                try:
                    bpy.app.timers.unregister(self.handle_playback_tick)
                except:
                    pass
                self.playback_timer = None
        else:
            selected_indices = [i for i, f in enumerate(clip.frames) if f.selected]
            if not selected_indices:
                return # Can't play if nothing selected
            
            self.is_playing = True
            
            # Continue from current playback_index if it is in selected_indices
            if hasattr(self, 'playback_index') and self.playback_index in selected_indices:
                try:
                    self._playback_list_pos = selected_indices.index(self.playback_index)
                except ValueError:
                    self.playback_index = selected_indices[0]
                    self._playback_list_pos = 0
            else:
                self.playback_index = selected_indices[0]
                self._playback_list_pos = 0
            
            # Register timer
            self.playback_timer = bpy.app.timers.register(self.handle_playback_tick)

    def step_playback(self, clip, direction):
        """Steps playback_index manually. direction is 1 (forward) or -1 (backward)"""
        # If playing, pause first
        if self.is_playing:
            self.toggle_playback(clip)
            
        selected_indices = [i for i, f in enumerate(clip.frames) if f.selected]
        if selected_indices:
            # Find current position in selected_indices
            if hasattr(self, '_playback_list_pos') and self.playback_index in selected_indices:
                try:
                    idx_pos = selected_indices.index(self.playback_index)
                    idx_pos = (idx_pos + direction) % len(selected_indices)
                except ValueError:
                    idx_pos = 0 if direction > 0 else len(selected_indices) - 1
            else:
                idx_pos = 0 if direction > 0 else len(selected_indices) - 1
            self._playback_list_pos = idx_pos
            self.playback_index = selected_indices[idx_pos]
        else:
            # If no frames selected, step through all frames
            n_frames = len(clip.frames)
            if n_frames > 0:
                self.playback_index = (self.playback_index + direction) % n_frames

    def invoke(self, context, event):
        if context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "Operator must be run from a 3D Viewport")
            return {'CANCELLED'}
            
        self._handle = None
        self.mouse_x = 0
        self.mouse_y = 0
        
        # Grid parameters
        self.cell_w = 80
        self.cell_h = 100
        self.padding = 12
        self.margin_top = 60
        self.margin_bottom = 60
        self.viewer_height = 0
        self.x_start = 0
        self.avail_width = 100
        self.y_start = 0
        self.avail_height = 100
        
        # Scroll offset
        self.scroll_y = 0
        self.max_scroll_y = 0
        
        # Drag selection state
        self.is_dragging = False
        self.drag_action = None # 'SELECT' or 'DESELECT'
        self.last_hovered_idx = -1
        
        # Previews references
        self.preview_images = {} # frame_number: bpy.types.Image
        
        # Playback index (used when playback is running)
        self.playback_timer = None
        self.playback_index = 0
        self.is_playing = False
        
        clip = context.scene.spritesheet_clips[context.scene.active_clip_index]
        
        # Load cached images into Blender memory
        self.load_previews(clip)
        
        # Adjust panel properties
        self.cell_w = int(clip.preview_size) + 16
        self.cell_h = int(clip.preview_size) + 32
        
        # Add draw handler
        self._handle = bpy.types.SpaceView3D.draw_handler_add(
            self.draw_callback, (context,), 'WINDOW', 'POST_PIXEL'
        )
        
        # Register modal handler
        context.window_manager.modal_handler_add(self)
        
        # Force initial redraw
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}
        
    def modal(self, context, event):
        # Force redraw on every event inside modal to keep it fluid
        context.area.tag_redraw()
        
        clip = context.scene.spritesheet_clips[context.scene.active_clip_index]
        width = context.region.width
        height = context.region.height
        layout_items = self.get_visible_frames_layout(width, height, clip, context)
        
        # Mouse movement tracking
        if event.type == 'MOUSEMOVE':
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y
            
            # Find hovered item
            hovered_idx = self.hit_test(self.mouse_x, self.mouse_y, layout_items)
            self.last_hovered_idx = hovered_idx
            
            # Paint selection/deselection on drag
            if self.is_dragging and hovered_idx != -1 and self.drag_action is not None:
                frame_item = clip.frames[hovered_idx]
                if self.drag_action == 'SELECT':
                    frame_item.selected = True
                else:
                    frame_item.selected = False
                    
            return {'RUNNING_MODAL'}
            
        # Left click
        elif event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                # Check header buttons first
                buttons = self.get_header_buttons(width, height, clip)
                for btn in buttons:
                    if (btn['x_min'] <= event.mouse_region_x <= btn['x_max']) and (btn['y_min'] <= event.mouse_region_y <= btn['y_max']):
                        if btn['id'] == 'CLOSE':
                            self.close_modal(context)
                            return {'FINISHED'}
                        self.execute_header_button(context, btn['id'], clip)
                        return {'RUNNING_MODAL'}
                        
                # Click grid items
                clicked_idx = self.hit_test(event.mouse_region_x, event.mouse_region_y, layout_items)
                if clicked_idx != -1:
                    frame_item = clip.frames[clicked_idx]
                    # Start paint drag stroke
                    self.is_dragging = True
                    # Toggle and set drag stroke action
                    frame_item.selected = not frame_item.selected
                    self.drag_action = 'SELECT' if frame_item.selected else 'DESELECT'
                else:
                    # Clicked outside cards (e.g. background)
                    pass
            elif event.value == 'RELEASE':
                self.is_dragging = False
                self.drag_action = None
            return {'RUNNING_MODAL'}
            
        # Scroll wheel (vertical scroll)
        elif event.type == 'WHEELUPMOUSE':
            self.scroll_y = max(0, self.scroll_y - 40)
            return {'RUNNING_MODAL'}
        elif event.type == 'WHEELDOWNMOUSE':
            self.scroll_y = min(self.max_scroll_y, self.scroll_y + 40)
            return {'RUNNING_MODAL'}
            
        # Keyboard shortcuts — event.type is the key itself ('A', 'D', etc.)
        elif event.type == 'A' and event.value == 'PRESS':
            for f in clip.frames:
                f.selected = True
            self.report({'INFO'}, "Selected all frames")
            return {'RUNNING_MODAL'}
            
        elif event.type == 'D' and event.value == 'PRESS':
            for f in clip.frames:
                f.selected = False
            if self.is_playing:
                self.toggle_playback(clip)
            self.report({'INFO'}, "Deselected all frames")
            return {'RUNNING_MODAL'}
            
        elif event.type == 'I' and event.value == 'PRESS':
            for f in clip.frames:
                f.selected = not f.selected
            self.report({'INFO'}, "Inverted selection")
            return {'RUNNING_MODAL'}
            
        elif event.type == 'SPACE' and event.value == 'PRESS':
            self.toggle_playback(clip)
            return {'RUNNING_MODAL'}
            
        elif event.type == 'LEFT_ARROW' and event.value == 'PRESS':
            self.step_playback(clip, -1)
            return {'RUNNING_MODAL'}
            
        elif event.type == 'RIGHT_ARROW' and event.value == 'PRESS':
            self.step_playback(clip, 1)
            return {'RUNNING_MODAL'}
            
        elif event.type == 'N' and event.value == 'PRESS':
            if not hasattr(self, '_every_n_state'):
                self._every_n_state = 2
            else:
                self._every_n_state = (self._every_n_state % 5) + 1
                if self._every_n_state == 1:
                    self._every_n_state = 2
            for i, f in enumerate(clip.frames):
                f.selected = (i % self._every_n_state == 0)
            self.report({'INFO'}, f"Selected every {self._every_n_state} frames")
            return {'RUNNING_MODAL'}
                    
        # Close modal: ESC or Right Click
        elif event.type in {'ESC', 'RIGHTMOUSE'}:
            self.close_modal(context)
            return {'FINISHED'}
            
        return {'RUNNING_MODAL'}
