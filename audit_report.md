# Auditoría Exhaustiva — SpriteSheet Frame Selector Addon

---

## 1. Resumen Ejecutivo

| Métrica | Valor |
|---|---|
| **Archivos de producción** | 10 (`.py`) + 1 manifest |
| **Líneas totales** | ~3,400 |
| **Clases registradas** | 26 (4 PropertyGroups, 15 Operators, 6 Panels/UILists, 1 Modal) |
| **Tests automatizados** | 4 archivos, 8 tests |
| **Bugs P0 (críticos)** | 3 |
| **Bugs P1 (importantes)** | 8 |
| **Issues P2 (menores/polish)** | 14 |
| **Riesgos técnicos** | 6 |

### Estado General

El addon es **funcional y estable para uso interactivo básico**. Las features principales (preview generation, visual selector, export, World Swap, Included Collections) operan correctamente en el flujo principal.

Sin embargo, existen **3 bugs críticos** que pueden causar bloqueo de la interfaz modal, degradación progresiva de rendimiento, o incompatibilidad con la versión de Blender declarada en el manifest. Además, el Visual Selector tiene un **problema de rendimiento severo** en su pipeline de dibujo GPU que escala negativamente con el número de frames visibles.

### Nivel de Riesgo

> [!WARNING]
> **MEDIO-ALTO** — El addon no está listo para distribución pública sin corregir los P0 y realizar un cleanup básico. Para uso interno/personal, es utilizable con precaución.

### ¿Listo para cleanup?

**Sí**, pero en fases. Primero P0, luego P1, luego limpieza general.

---

## 2. Bugs P0 — Bloqueantes / Críticos

### P0-1: ESC y RIGHTMOUSE no cierran el modal (PRESS es consumido)

> [!CAUTION]
> El usuario no puede cerrar el Visual Selector con ESC de forma confiable.

**Archivo**: [visual_selector.py](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/visual_selector.py)
**Líneas**: L994 vs L1070

**Causa**: El bloque `elif event.value == 'PRESS'` en L994 captura *todos* los eventos PRESS (incluyendo ESC y RIGHTMOUSE). Como ESC no tiene handler dentro de ese bloque, cae al `return {'RUNNING_MODAL'}` final en L1074. El handler de cierre en L1070 (`elif event.type in {'ESC', 'RIGHTMOUSE'}`) solo se alcanza en eventos RELEASE, lo cual es un comportamiento invertido e inconsistente.

**Impacto**: El modal puede quedarse bloqueado si Blender no genera eventos RELEASE para ESC (variación según OS/configuración). El usuario queda atrapado en el modal.

---

### P0-2: `draw_rect` crea shader + batch GPU en CADA llamada (~200+/frame)

> [!CAUTION]
> Degradación severa de rendimiento con grids grandes. Cada frame de dibujo realiza ~200+ asignaciones de memoria GPU.

**Archivo**: [visual_selector.py](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/visual_selector.py)
**Líneas**: L205–213

**Causa**: `gpu.shader.from_builtin('UNIFORM_COLOR')` y `batch_for_shader(...)` se invocan en cada llamada a `draw_rect`. Con ~200+ rectángulos por frame (background, celdas, bordes, scrollbar, header, viewer), esto genera ~200+ lookups de shader y ~200+ allocations de batch por redibujado.

**Impacto**: Framerate degradado, consumo excesivo de memoria GPU, latencia visible en trackpad/scroll con muchos frames.

---

### P0-3: `BLENDER_EEVEE` deprecado — incompatible con Blender 5.x

> [!CAUTION]
> El World Swap (Material Preview) NO funciona correctamente en Blender 4.0+ / 5.x. El identificador del motor EEVEE cambió a `BLENDER_EEVEE_NEXT`.

**Archivo**: [utils.py](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/utils.py)
**Líneas**: L374

**Causa**: `WorldSwapContext.__enter__` establece `self.scene.render.engine = 'BLENDER_EEVEE'`. En Blender 4.0+, EEVEE Legacy fue reemplazado por EEVEE Next con el identificador `'BLENDER_EEVEE_NEXT'`. El manifest declara `blender_version_min = "5.0.0"`.

**Relacionado**: `taa_render_samples` (L300-301, L375-376, L406-408) también es un atributo de EEVEE Legacy. En EEVEE Next se usa un sistema de samples diferente. Los guards `hasattr()` previenen crashes, pero la optimización de 4 samples no tiene efecto — el render usa el valor por defecto (64 o más), anulando la ventaja de velocidad del World Swap.

---

## 3. Bugs P1 — Importantes

### P1-1: Timer de playback leakea en toggling rápido

**Archivo**: [visual_selector.py](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/visual_selector.py)
**Líneas**: L718–723, L743

`bpy.app.timers.register()` retorna `None`, no un handle. Por lo tanto, `self.playback_timer` siempre es `None`, y el path de unregister en `toggle_playback()` (L718: `if self.playback_timer:`) es **código muerto**. Al togglear rápidamente play/pause, se pueden registrar múltiples timers concurrentes que compiten por actualizar `playback_index`.

---

### P1-2: `validate_export_settings` crea directorios como efecto secundario durante panel draw

**Archivo**: [utils.py](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/utils.py)
**Líneas**: L107-108

`os.makedirs(out_dir, exist_ok=True)` se ejecuta dentro de `validate_export_settings()`, que es llamada por `panels.py` L259 en cada redibujado del panel de exportación. Esto **crea directorios en disco** como efecto secundario de simplemente tener el panel visible.

---

### P1-3: WorldSwapContext no limpia World/Image temporales

**Archivo**: [utils.py](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/utils.py)
**Líneas**: L340, L349

`temp_world` y `temp_image` (HDRI) persisten en `bpy.data.worlds` / `bpy.data.images` indefinidamente. No se eliminan en `__exit__()`. Con uso repetido (diferentes HDRIs, diferentes clips), estos datablocks se acumulan en el archivo .blend, incrementando el tamaño del archivo y consumo de memoria.

---

### P1-4: Sin protección contra doble invocación del Visual Selector

**Archivo**: [visual_selector.py](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/visual_selector.py)

Si el operador se invoca dos veces rápidamente, se registran dos draw handlers, se cargan dos sets de previews, y ambos modals corren simultáneamente. Al cerrar uno, las imágenes compartidas (`check_existing=True`) se eliminan, dejando referencias dangling en el otro modal.

---

### P1-5: `NumpyComposer` — cleanup de imágenes no es resiliente

**Archivo**: [composer_numpy.py](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/composer_numpy.py)

Si `bpy.data.images.remove(img)` falla para una imagen (e.g., todavía referenciada), el error propaga y todas las imágenes restantes en `loaded_images` se quedan sin limpiar. Falta un `try/except` per-imagen.

---

### P1-6: Clips con nombres duplicados sobreescriben metadata JSON

**Archivo**: [exporter.py](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/exporter.py)

`metadata["clips"]` es un `dict` con el nombre del clip como key. Si dos clips tienen el mismo nombre, el segundo sobreescribe silenciosamente al primero en el JSON de metadata.

---

### P1-7: `__enter__` de WorldSwapContext puede dejar escena modificada si falla después del world swap

**Archivo**: [utils.py](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/utils.py)
**Líneas**: L373-383

Si una excepción ocurre en el loop de ocultamiento de luces (L380-383) después de que el world y engine ya fueron cambiados (L373-374), `__exit__` **NO se invoca** (porque `__enter__` no completó). La escena queda con el world temporal y EEVEE como motor activo.

---

### P1-8: 33 `print()` en código de producción

**Archivos**: `composer_numpy.py` (6), `exporter.py` (9), `preview_generator.py` (4), `render_queue.py` (4), `utils.py` (9), `visual_selector.py` (1)

Todos los mensajes de error/warning usan `print()` en lugar del módulo `logging` de Python o `self.report()` de Blender. Estos mensajes se pierden silenciosamente para el usuario y contaminan la consola del sistema.

---

## 4. Issues P2 — Menores / Polish / Deuda Técnica

### P2-1: `get_visible_frames_layout` se llama 2x por interacción
Una vez en `modal()` (L864) y otra en `draw_callback()` (L427). Se podría cachear el resultado.

### P2-2: `gpu.texture.from_image()` se llama por frame por celda visible
L477, L634 — Las texturas GPU se recrean en cada redibujado. Blender cachea internamente la subida a GPU, pero el overhead de objetos Python es significativo con muchas celdas.

### P2-3: `selected_count` se computa 2x por frame
L446–449 (loop en draw) y L675 (`sum()` en viewer draw). Redundante.

### P2-4: Lógica de poll duplicada
El patrón `len(scene.spritesheet_clips) > 0 and 0 <= active_clip_index < len(...)` se repite en 5+ operadores y 4+ paneles. Debería ser una función utilitaria.

### P2-5: Fórmula de frame count duplicada
`((frame_end - frame_start) // frame_step) + 1` aparece en `panels.py` L14, L137 y implícitamente en validaciones.

### P2-6: `calculate_sheet_dimensions` duplicada
Existe como función independiente en `utils.py` Y como método estático en `composer.py`. Código idéntico.

### P2-7: Sanitización de nombre de clip duplicada
La lógica `c if c.isalnum() or c in ('-', '_') else '_'` está duplicada en `get_cache_dir` y `get_temp_export_dir`.

### P2-8: `include_in_export` default=False
Los clips nuevos no están incluidos en el export por defecto. Puede sorprender a usuarios nuevos.

### P2-9: Sin validación `frame_start <= frame_end`
En `properties.py` L55-66, el usuario puede configurar `frame_end < frame_start` sin warning.

### P2-10: Bare `except:` en close_modal
L349, L353 — Capturan `BaseException` incluyendo `SystemExit` y `KeyboardInterrupt`. Deberían usar `except Exception:`.

### P2-11: Shortcuts no documentados en la barra inferior
`N`, `PAGE_UP/DOWN`, `HOME/END`, `Shift+Arrow`, `Shift+Wheel` no aparecen en el texto de shortcuts del footer.

### P2-12: `is_dragging` puede quedarse en True si se pierde el RELEASE
Si el usuario hace Alt-Tab durante un drag, el evento RELEASE nunca llega. Al regresar, el mouse mueve seleccionará/deseleccionará celdas inesperadamente.

### P2-13: Emojis Unicode en UI labels
L98, L254, L256 en `panels.py` usan `⚠️`. Pueden no renderizar correctamente en todas las plataformas/fuentes.

### P2-14: Colores hardcoded como tuples magic numbers
~30+ tuples de color inline en `visual_selector.py` sin nombres de constantes. Hace imposible tematización y dificulta consistencia visual.

---

## 5. Riesgos Técnicos

### R1: `taa_render_samples` silenciosamente ignorado en Blender 5.x
Los guards `hasattr()` previenen crashes pero la optimización de samples bajos no tiene efecto. Los renders de Material Preview tardan mucho más de lo necesario sin que el usuario lo sepa.

### R2: Temp dirs en system temp nunca se limpian (archivo .blend no guardado)
Cuando el .blend no está guardado, cache y export usan `tempfile.gettempdir()`. Estos directorios no se limpian automáticamente al cerrar Blender.

### R3: Directorio `MagicMock/` creado por tests con bpy mockeado
Los tests que mockean `bpy.data.filepath` crean directorios reales bajo `MagicMock/mock.data.filepath/...` en la raíz del proyecto. Estos son artefactos de test que persisten.

### R4: HDRI path resolution depende de estructura interna de Blender
`WorldSwapContext` busca HDRIs en paths específicos del bundle de Blender (`Resources/version/datafiles/studiolights/world`). Si Blender cambia esta estructura, el fallback falla silenciosamente.

### R5: Sin límite de dimensión máxima de spritesheet
`NumpyComposer` no valida el tamaño total del spritesheet. Un sheet de 4096×4096 RGBA float32 consume ~256 MB de RAM. Sheets más grandes pueden causar crashes por memoria.

### R6: `render_selected_frames()` y `get_temp_export_dir(clip)` posiblemente código muerto
Solo `render_multi_clip_frames()` es llamado desde `exporter.py`. `render_selected_frames()` solo es usado por `export_single_clip()`, que a su vez es un wrapper trivial de `export_multiple_clips()`.

---

## 6. Recomendaciones de Optimización

### Rendimiento GPU (Visual Selector)

| Problema | Impacto | Solución |
|---|---|---|
| Shader recreado ~200x/frame | Alto | Cachear `gpu.shader.from_builtin('UNIFORM_COLOR')` una vez en `invoke` o a nivel de clase |
| Batch recreado ~200x/frame | Alto | Cachear batch o consolidar rectángulos del mismo color |
| `get_visible_frames_layout` 2x/interacción | Medio | Cachear resultado por frame y invalidar solo en eventos relevantes |
| `gpu.texture.from_image` por celda/frame | Medio | Cachear texturas en dict por image ID, invalidar en `load_previews` |
| `selected_count` calculado 2x/frame | Bajo | Calcular una vez y pasar como parámetro |

### Memoria

| Problema | Impacto | Solución |
|---|---|---|
| Worlds temporales acumulados en .blend | Medio | Limpiar worlds huérfanos al salir del context manager o usar `do_unlink=True` |
| Images HDRI acumuladas | Bajo | Aceptable con `check_existing=True`, pero documentar |
| Preview images leakean en double-open | Medio | Agregar guard de invocación única |

### UI

| Problema | Impacto | Solución |
|---|---|---|
| Validación crea directorios en draw | Medio | Separar validación de creación de directorios |
| Colores magic numbers | Bajo | Crear diccionario de tema centralizado |

### Render/Export

| Problema | Impacto | Solución |
|---|---|---|
| EEVEE samples no optimizados en Blender 5.x | Alto | Detectar versión y usar API correcta de EEVEE Next |
| Sin límite de dimensiones de spritesheet | Medio | Agregar validación con warning al usuario |

---

## 7. Archivos que Requieren Limpieza

### Código de Producción

| Archivo | Qué Limpiar | Prioridad |
|---|---|---|
| [visual_selector.py](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/visual_selector.py) | Fix ESC bug, cachear shader, fix timer leak, guard doble invocación, extraer constantes | **P0+P1** |
| [utils.py](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/utils.py) | Fix `BLENDER_EEVEE` → detectar EEVEE Next, separar validación de side effects, cleanup WorldSwapContext | **P0+P1** |
| [composer_numpy.py](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/composer_numpy.py) | Per-image try/except en cleanup | **P1** |
| [exporter.py](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/exporter.py) | Manejar nombres de clips duplicados en JSON | **P1** |
| [operators.py](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/operators.py) | Extraer poll compartido, agregar bounds check | **P2** |
| [panels.py](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/panels.py) | No llamar validate en draw, extraer frame count formula | **P2** |
| [properties.py](file:///Users/amaruc/Documents/Documentos/Personal_Projects/Developer/spritesheet-blender/spritesheet_frame_selector/properties.py) | Validación frame_start/end, renombrar `object` param | **P2** |
| Todos los `.py` | Reemplazar 33 `print()` por `logging` | **P1** |

### Archivos del Repositorio

| Archivo/Directorio | Acción | Prioridad |
|---|---|---|
| `MagicMock/` | Eliminar — artefacto de tests | **Alta** |
| `Imagenes_test/` | Eliminar — directorio vacío (solo `.DS_Store`) | **Alta** |
| `spritesheet_frame_selector.zip` | Eliminar — build artifact en source tree | **Alta** |
| `audit_report_ss.md` | Eliminar o mover fuera del repo | **Media** |
| `implementation_plan.md` | Eliminar o mover fuera del repo | **Media** |
| `mvp.md` | Eliminar o mover fuera del repo | **Media** |
| `PROJECT_VISION.md` | Eliminar o mover fuera del repo | **Media** |
| `.DS_Store` (múltiples) | Eliminar + agregar a `.gitignore` | **Media** |
| `__pycache__/` (22+ .pyc) | Eliminar + agregar a `.gitignore` | **Media** |
| `blender_manifest.toml` | Actualizar maintainer placeholder `dev@example.com` | **Media** |

---

## 8. Próximo Plan Sugerido

### Fase 1 — Fixes P0 (Prioridad inmediata)

1. **Fix ESC/RIGHTMOUSE** — Mover el handler de cierre ANTES del bloque `event.value == 'PRESS'`, o añadir checks explícitos para ESC/RIGHTMOUSE dentro del bloque PRESS.
2. **Cachear shader GPU** — Almacenar `gpu.shader.from_builtin('UNIFORM_COLOR')` en `self._rect_shader` durante `invoke`, reutilizar en `draw_rect`.
3. **Fix `BLENDER_EEVEE`** — Detectar versión de Blender y usar `'BLENDER_EEVEE_NEXT'` para 4.0+. Actualizar referencia de samples a la API correcta de EEVEE Next.

### Fase 2 — Fixes P1 (Estabilidad)

4. **Fix timer leak** — Usar `bpy.app.timers.unregister(self.handle_playback_tick)` directamente (por referencia de función) en lugar de depender del handle de retorno.
5. **Guard doble invocación** — Agregar flag a nivel de clase para prevenir múltiples instancias del modal.
6. **Separar validación de side effects** — Extraer `os.makedirs` de `validate_export_settings`.
7. **Per-image cleanup resiliente** en `NumpyComposer`.
8. **Manejar clips con nombres duplicados** en metadata JSON.
9. **WorldSwapContext `__enter__` resiliente** — Wrap el loop de luces en try/except y restaurar estado parcial si falla.
10. **Reemplazar `print()` por `logging`** en todos los archivos.

### Fase 3 — Cleanup (Calidad de código)

11. Extraer constantes de colores, tamaños y breakpoints en dicts centralizados.
12. Extraer poll compartido en función utilitaria.
13. Eliminar duplicación: `calculate_sheet_dimensions`, sanitización de nombres, fórmula de frame count.
14. Eliminar código muerto (`render_selected_frames` si se confirma).
15. Bare `except:` → `except Exception:`.
16. Documentar shortcuts faltantes en footer.

### Fase 4 — Optimización

17. Cachear `get_visible_frames_layout` por frame.
18. Cachear texturas GPU por image ID.
19. Consolidar batches de draw (mismos colores en un solo draw call).
20. Limpieza de worlds/images temporales en `WorldSwapContext.__exit__`.

### Fase 5 — Packaging

21. Eliminar archivos de desarrollo del repositorio.
22. Configurar `.gitignore` completo.
23. Actualizar `blender_manifest.toml`.
24. Crear script de build para generar ZIP limpio.
25. Verificar instalación limpia desde ZIP.

---

## Apéndice A — Cobertura de Tests

| Área | Cubierta | No cubierta |
|---|---|---|
| Render pipeline (single clip, 3 shading modes) | ✅ | Multi-clip, error handling |
| Transparency (alpha channel) | ✅ | Opaque mode |
| State restoration (world, engine, samples, lights) | ✅ | Partial failure scenarios |
| Collection visibility (whitelist, nested) | ✅ | Deep nesting, orphans, empty whitelist |
| Composer math (dimensions) | ✅ | Pixel placement, NumpyComposer |
| JSON metadata (multi-clip) | ✅ | Duplicate names, empty clips |
| Visual Selector (modal, GPU, interaction) | ❌ | No tests (requires interactive context) |
| Operators (UI-level) | ❌ | No tests |
| Error cases (missing camera, invalid paths) | ❌ | No tests |
| Export pipeline (`export_multiple_clips`) | ❌ | No tests |
| Frame step > 1 | ❌ | No tests |
| Padding/margin in composition | ❌ | No tests |
| PNG sequence export | ❌ | No tests |

## Apéndice B — Inventario de Archivos

### Addon (`spritesheet_frame_selector/`)

| Archivo | Líneas | Bytes | Rol |
|---|---|---|---|
| `__init__.py` | 18 | 486 | Registro |
| `properties.py` | 188 | 4,909 | Modelo de datos |
| `operators.py` | 420 | 14,211 | Operadores UI |
| `panels.py` | 291 | 11,111 | Paneles N-panel |
| `utils.py` | 413 | 18,084 | Utilidades + WorldSwapContext |
| `visual_selector.py` | 1,075 | 49,310 | Modal overlay GPU |
| `preview_generator.py` | 214 | 8,508 | Generación de previews |
| `exporter.py` | 138 | 5,277 | Pipeline de exportación |
| `composer.py` | 46 | 1,782 | ABC compositor |
| `composer_numpy.py` | 115 | 4,775 | Compositor NumPy |
| `render_queue.py` | 201 | 7,612 | Cola de render |
| `blender_manifest.toml` | 12 | 389 | Manifest extensión |
| **Total** | **~3,131** | **~126,454** | |

### Tests (`tests/`)

| Archivo | Líneas | Tests | Contexto |
|---|---|---|---|
| `test_integration_render.py` | 283 | 2 | Requiere Blender |
| `test_visibility.py` | 114 | 2 | Requiere Blender |
| `test_composer.py` | 62 | 4 | Standalone (mock bpy) |
| `test_exporter.py` | 103 | 2 | Standalone (mock bpy) |
