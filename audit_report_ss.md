# Auditoría Funcional — SpriteSheet Frame Selector

Auditoría línea por línea de todo el código del addon. Sin features nuevas; solo bugs, limitaciones y estado real.

---

## 🔴 Bugs Críticos (Crashers / Bloqueantes)

### BUG-01: Keyboard events en Visual Selector nunca se disparan
**Archivo**: [visual_selector.py:385](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/visual_selector.py#L385)
**Severidad**: 🔴 Crítico — A, D, I, Space, N no funcionan

```python
elif event.type == 'KEYBOARD':       # ← Esto NUNCA es True
    if event.value == 'PRESS':
        if event.type == 'A':         # ← Redundante, ya falló arriba
```

En Blender, `event.type` es directamente `'A'`, `'D'`, `'I'`, `'SPACE'`, `'N'`, etc. **No existe un tipo `'KEYBOARD'`**. Este bloque entero es código muerto. Ningún shortcut del Visual Selector funciona actualmente.

**Fix**: Reemplazar la estructura `elif event.type == 'KEYBOARD'` por checks directos de cada tecla.

---

### BUG-02: GPU blending no está habilitado — overlays transparentes se ven opacos
**Archivo**: [visual_selector.py:164](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/visual_selector.py#L164)
**Severidad**: 🔴 Crítico — El Visual Selector se ve roto visualmente

El `draw_callback` nunca habilita GPU alpha blending. Sin esto, las llamadas `draw_rect()` con alpha < 1.0 (background overlay, dim overlay, selection borders) se renderizan como si fueran opacos, produciendo un resultado visual incoherente.

**Fix**: Agregar al inicio de `draw_callback`:
```python
gpu.state.blend_set('ALPHA')
```
Y al final:
```python
gpu.state.blend_set('NONE')
```

---

### BUG-03: `open_visual_selector` usa `execute()` pero necesita `invoke()`
**Archivo**: [operators.py:273](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/operators.py#L273)
**Severidad**: 🔴 Crítico — El Visual Selector puede no funcionar

```python
def execute(self, context):
    bpy.ops.spritesheet.visual_selector('INVOKE_DEFAULT')
```

Llamar `bpy.ops` con `'INVOKE_DEFAULT'` desde `execute()` es problemático porque `execute()` puede correr en contextos sin `event`. El operador wrapper debería implementar `invoke()` directamente, no `execute()`, para garantizar que hay un event válido.

**Fix**: Cambiar a `invoke()` y usar `return bpy.ops.spritesheet.visual_selector('INVOKE_DEFAULT')`.

---

### BUG-04: `validate_export_settings` en `poll()` del export es costoso y puede crashear
**Archivo**: [operators.py:285-288](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/operators.py#L285-L288)
**Severidad**: 🔴 Crítico — `poll()` se ejecuta en cada redraw de UI

```python
@classmethod
def poll(cls, context):
    from .utils import validate_export_settings
    is_valid, _ = validate_export_settings(context.scene)
    return is_valid
```

`validate_export_settings` llama `os.path.exists()`, `os.makedirs()`, y accede a `resolve_blend_path()` — operaciones de I/O en cada redraw. Además, si `active_clip_index` está fuera de rango, el acceso a `scene.spritesheet_clips[clip_idx]` podría fallar antes de la validación de rango.

**Fix**: `poll()` solo debe verificar condiciones ligeras (clips existen, frames seleccionados). Mover la validación pesada a `execute()`.

---

### BUG-05: `panels.py` accede a `scene.active_clip_index` sin bounds check en varios paneles
**Archivo**: [panels.py:101, 135, 141, 185](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/panels.py#L101)
**Severidad**: 🔴 Crítico — Crash de UI si el índice queda desfasado

```python
# En SPRITESHEET_PT_preview.draw():
clip = scene.spritesheet_clips[scene.active_clip_index]  # No bounds check
```

Si `active_clip_index` apunta fuera de rango (por ejemplo tras eliminar el último clip y antes de que el índice se actualice), esto crashea el redraw del panel entero.

**Fix**: Agregar guard `0 <= scene.active_clip_index < len(scene.spritesheet_clips)` en cada `poll()` de subpanel.

---

### BUG-06: `use_fake_user = True` en previews impide limpieza
**Archivo**: [visual_selector.py:62](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/visual_selector.py#L62)
**Severidad**: 🔴 Crítico — Memory leak progresivo

```python
img.use_fake_user = True
```

`use_fake_user` marca la imagen para persistencia en el `.blend`. Si el addon crashea o el usuario cierra sin ESC, estas imágenes **se guardan permanentemente** en el archivo `.blend`, acumulándose indefinidamente.

**Fix**: Eliminar `use_fake_user = True`. Las imágenes solo necesitan existir en RAM mientras el modal está abierto.

---

### BUG-07: `composer_numpy.py` usa `check_existing=True` al cargar frames — puede reusar datos corruptos
**Archivo**: [composer_numpy.py:52](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/composer_numpy.py#L52)
**Severidad**: 🟡 Moderado — Spritesheet corrupto en ciertos escenarios

```python
frame_img = bpy.data.images.load(path, check_existing=True)
```

Si una imagen con ese path ya existe en `bpy.data.images` (de un export anterior, o de un preview), Blender reutiliza la referencia existente sin releer del disco. Si el contenido del archivo cambió (re-render), los píxeles leídos serán los del cache anterior.

**Fix**: Usar `check_existing=False` o recargar con `frame_img.reload()` después de load.

---

### BUG-08: `calculate_sheet_dimensions` retorna `(rows, w, h)` pero `ComposerBackend.calculate_dimensions` retorna `(w, h, rows)`
**Archivo**: [utils.py:65](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/utils.py#L65) vs [composer.py:42-45](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/composer.py#L42-L45)
**Severidad**: 🔴 Crítico — El compositor calcula dimensiones incorrectas

```python
# utils.py
return rows, sheet_w, sheet_h    # (rows, w, h)

# composer.py
return sheet_w, sheet_h, rows    # (w, h, rows)
```

`NumpyComposer.compose()` llama `self.calculate_dimensions()` (de `ComposerBackend`) y desempaqueta como `sheet_w, sheet_h, rows`. Esto es correcto internamente.

Pero `panels.py:210` llama `calculate_sheet_dimensions` (de `utils.py`) y desempaqueta como `rows, width, height`. **Los valores están correctos en cada uso**, pero la inconsistencia del orden de retorno es una trampa de mantenimiento y fuente de bugs futuros.

**Fix**: Unificar el orden de retorno a `(rows, sheet_w, sheet_h)` en ambos sitios.

---

## 🟡 Bugs Moderados (Funcionalidad Incorrecta)

### BUG-09: `open_visual_selector.poll()` no verifica que haya frames cacheados con archivos reales
**Archivo**: [operators.py:270](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/operators.py#L270)

El poll delega a `SPRITESHEET_OT_generate_preview.poll()`, que solo verifica que el clip exista. El usuario puede tener un clip con frames de datos (nombres, selección) pero sin archivos PNG en disco (por ejemplo tras mover el `.blend` o limpiar cache). El Visual Selector se abre pero muestra solo placeholders grises.

**Estado**: Aceptable para MVP, pero debería advertir en lugar de fallar silenciosamente.

---

### BUG-10: `add_clip` trigger update callback que marca `cache_dirty` inmediatamente
**Archivo**: [operators.py:16-17](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/operators.py#L16-L17)

```python
clip.frame_start = scene.frame_start  # Triggers on_clip_settings_change → cache_dirty = True
clip.frame_end = scene.frame_end      # Triggers again
```

No es un bug funcional (el clip nuevo no tiene cache), pero si en el futuro se agrega lógica más compleja al callback, esto podría ser problemático.

**Estado**: Aceptable. No requiere fix inmediato.

---

### BUG-11: `panels.py` línea 164 muestra `active_clip_index` como widget numérico
**Archivo**: [panels.py:164](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/panels.py#L164)

```python
row.prop(context.scene, "active_clip_index", text="") # Dummy space or just a slider
```

Esto renderiza un slider numérico del índice de clip activo, que el usuario puede modificar para cambiar el clip activo de forma confusa. No tiene relación con "Every N".

**Fix**: Eliminar esta línea dummy.

---

### BUG-12: Playback highlight se dibuja como rectángulo sólido DEBAJO del thumbnail
**Archivo**: [visual_selector.py:205-206](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/visual_selector.py#L205-L206)

El highlight dorado del playback se dibuja ANTES del thumbnail, por lo que la textura se renderiza encima y lo tapa completamente. El usuario no ve ningún feedback visual del frame activo en playback.

**Fix**: Mover el dibujo del playback highlight DESPUÉS del thumbnail.

---

### BUG-13: Scroll puede ir negativo sin clamping efectivo
**Archivo**: [visual_selector.py:378](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/visual_selector.py#L378)

```python
self.scroll_y -= 40  # No clamping here
```

El scroll se modifica directamente sin clampar. El clamp ocurre en `get_visible_frames_layout`, pero entre el evento de scroll y el siguiente redraw, `self.scroll_y` puede ser negativo, lo que causa un frame de flicker.

**Fix**: Clampar inmediatamente después de modificar.

---

### BUG-14: `render.filepath` en `render_queue.py` no termina la ruta correctamente para Blender
**Archivo**: [render_queue.py:65](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/render_queue.py#L65)

`bpy.ops.render.render(write_still=True)` usa `scene.render.filepath` pero Blender puede agregar un sufijo de frame automáticamente. Debemos asegurarnos que el formato del path sea correcto. Podríamos necesitar agregar un trailing separator o usar una convención limpia.

**Estado**: Probablemente funciona en la mayoría de los casos, pero requiere test real.

---

## 🟢 Issues Menores (UX / Cosmético)

### ISSUE-01: Header shortcuts text puede salirse de pantalla
El texto de shortcuts en el header se posiciona a `width - 400`, lo que puede ser negativo en viewports pequeños.

### ISSUE-02: `SPRITESHEET_UL_clip_list` no protege contra step=0 en el cálculo
```python
frames_count = ((item.frame_end - item.frame_start) // item.frame_step) + 1
```
`frame_step` tiene `min=1`, así que no debería llegar a 0, pero si `frame_end < frame_start` el resultado es negativo.

### ISSUE-03: El botón "Every N" dentro del Selection panel no permite configurar N
Solo tiene el operator button sin prop visible para el usuario. El N se controla solo en el popup que aparece al hacer click.

### ISSUE-04: No hay ícono `'CHECKMARK'` en Blender 5.x
**Archivo**: [panels.py:119](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/panels.py#L119)
`'CHECKMARK'` puede no existir como ícono válido. Debería ser `'CHECKBOX_HLT'` o verificarse.

### ISSUE-05: Export button tooltip no es útil cuando está deshabilitado
El error se muestra debajo pero el tooltip del botón sigue siendo el genérico. No hay forma estándar de cambiar el tooltip dinámicamente en Blender.

---

## Estado del Flujo MVP

| Paso del flujo | Estado | Notas |
|---|---|---|
| Crear clip | ✅ Funciona | Nombre auto-generado, rango de escena |
| Configurar rango/step/camera | ✅ Funciona | Update callbacks marcan cache dirty |
| Generar previews | ⚠️ Probable OK | Requiere test real con viewport |
| Abrir Visual Selector | 🔴 Bloqueado por BUG-01,02,03 | Shortcuts muertos, blending roto |
| Click toggle selección | ⚠️ Probable OK | Requiere test real |
| Drag paint selección | ⚠️ Probable OK | Requiere test real |
| Playback con Space | 🔴 Bloqueado por BUG-01 | Shortcut muerto |
| Cerrar/reabrir con persistencia | ✅ PropertyGroups persisten | Probado conceptualmente |
| Exportar spritesheet PNG | ⚠️ Probable OK | Requiere test real |
| Alpha correcta | ⚠️ Requiere verificación | Bottom-up math verificada |

---

## Estado del Export Multi-clip

> [!IMPORTANT]
> **El export multi-clip NO está implementado.**

El addon solo exporta el clip activo (`export_single_clip`). No existe operador, función, ni UI para:
- Combinar múltiples clips en un solo spritesheet/atlas
- Exportar todos los clips de una vez

**Lo que SÍ existe (infraestructura preparada)**:
- `write_metadata_json()` acepta un dict `clips_data` con múltiples entradas
- `ComposerBackend.compose()` no tiene restricción de un solo clip
- El data model soporta múltiples clips en `scene.spritesheet_clips`

**Siguiente tarea prioritaria**: Implementar `SPRITESHEET_OT_export_all_clips` que:
1. Itere sobre todos los clips
2. Renderice los frames seleccionados de cada uno
3. Concatene los paths en orden
4. Llame al compositor con la lista completa
5. Escriba el JSON con metadata de todos los clips

---

## Memory Cleanup

| Recurso | ¿Se limpia? | Problema |
|---|---|---|
| Preview images en `bpy.data.images` | 🔴 **PARCIAL** | `use_fake_user=True` (BUG-06) las persiste en .blend. Si crash → leak permanente |
| Texturas GPU (`gpu.texture.from_image`) | ⚠️ **Implícito** | Se crean en cada draw frame pero no se cachean. Posible GC pressure pero no leak real |
| Carpeta de cache de previews | ✅ OK | `clear_clip_previews()` borra con `shutil.rmtree` |
| Carpeta temporal de export | ✅ OK | `exporter.py` limpia en `finally` block |
| Renders intermedios | ✅ OK | Borrados junto con carpeta temporal |
| Compositor output image | ✅ OK | `bpy.data.images.remove(result_img)` en `finally` |
| Draw handler | ⚠️ **Frágil** | Solo se remueve en `ESC`/`RIGHTMOUSE`. Si Blender fuerza cierre del modal por otra razón, el handler queda colgado |

---

## Próximos Fixes Prioritarios

| Prioridad | Bug | Descripción | Esfuerzo |
|---|---|---|---|
| **P0** | BUG-01 | Fix keyboard events en Visual Selector | Bajo |
| **P0** | BUG-02 | Habilitar GPU alpha blending | Bajo |
| **P0** | BUG-03 | Cambiar `execute` a `invoke` en open_visual_selector | Bajo |
| **P0** | BUG-04 | Simplificar `poll()` del export | Bajo |
| **P0** | BUG-05 | Agregar bounds checks en panels | Bajo |
| **P0** | BUG-06 | Eliminar `use_fake_user` en previews | Bajo |
| **P1** | BUG-07 | Usar `check_existing=False` en compositor | Bajo |
| **P1** | BUG-08 | Unificar orden de retorno de dimensiones | Bajo |
| **P1** | BUG-11 | Eliminar widget dummy en panel Selection | Bajo |
| **P1** | BUG-12 | Reordenar dibujo de playback highlight | Bajo |
| **P1** | BUG-13 | Clampar scroll inmediatamente | Bajo |
| **P2** | Multi-clip | Implementar export de todos los clips | Medio |
