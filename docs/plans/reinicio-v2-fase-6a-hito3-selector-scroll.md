# Plan Fase 6a Hito 3 - Scroll Del Selector Visual

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: implementado

## Referencia Superior

`docs/plans/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md`

## Fuente Principal

`docs/technical-audit.md`

## Objetivo

Corregir el bug detectado durante validacion GUI: cuando la cantidad de thumbnails supera la capacidad visible del selector, los frames restantes quedan ocultos e inaccesibles desde el overlay.

Este plan cubre M6 de la auditoria y sigue la direccion propuesta por la auditoria: agregar offset de scroll/paginacion en la sesion y manejar rueda dentro del panel sin romper el `PASS_THROUGH` fuera del panel corregido en C1.

## Hallazgos De Auditoria Cubiertos

| ID | Severidad | Titulo | Estado En Este Subplan |
|---|---|---|---|
| M6 | medio | El selector visual no tiene scroll: los frames que no caben son inseleccionables desde el overlay | implementado; validacion GUI pendiente |

## Extracto Operativo De Auditoria

### M6 - El selector visual no tiene scroll

- Problema: el grid dibuja `max_visible = columns * rows` celdas y muestra `Showing X / Y frames`; no hay paginacion ni rueda de raton para alcanzar el resto. Los frames que no caben solo pueden afectarse con acciones globales como Select All, Invert o Every-2, no con seleccion visual individual.
- Causa: `VisualSelectorSession.draw()` calcula `visible_frames = clip.frames[:max_visible]` y `handle_visual_selector_event()` no usa `WHEELUPMOUSE/WHEELDOWNMOUSE` dentro del panel para desplazar el grid.
- Impacto: clips largos quedan parcialmente inaccesibles desde la herramienta principal de seleccion visual.
- Solucion propuesta por la auditoria: agregar offset de scroll en la sesion manejando `WHEELUPMOUSE/WHEELDOWNMOUSE`. Encaja con C1: la rueda dentro del panel debe servir al selector; fuera del panel debe pasar al viewport.
- Archivos/funciones afectados: `spritesheet_frame_selector/ui/visual_selector.py::VisualSelectorSession.draw`, `spritesheet_frame_selector/ui/visual_selector.py::handle_visual_selector_event`.
- Aspectos no verificados en runtime: comportamiento de rueda dentro/fuera del panel y seleccion de frames que inicialmente no caben.

## Interpretacion Del Subplan

- Decision: adoptar la solucion de auditoria con offset persistente por sesion.
- Argumento: no hace falta redisenar el selector ni crear paginacion discreta con botones; la rueda es el gesto esperado y ya participa en C1. Mantener la rueda fuera del panel como `RUNNING_MODAL + PASS_THROUGH` preserva la correccion de lifecycle.
- Riesgos: el scroll puede desalinear indices si `FrameCell.index` sigue representando indice visible en vez de indice real del clip. El subplan debe corregir esto explicitamente.
- Dependencias con otros hallazgos: C1 ya esta implementado y permite distinguir eventos dentro/fuera del panel. Este plan no cubre B7 undo, M9 thumbnails obsoletos, M10 perfilado GPU ni M3 redraw selectivo.

## Alcance De Implementacion

- Incluir:
  - Agregar estado de sesion para offset de grid, por ejemplo `grid_offset`.
  - Calcular `max_visible`, `columns`, `rows` y clamplear `grid_offset` contra `len(clip.frames) - max_visible`.
  - Cambiar `visible_frames = clip.frames[:max_visible]` por una ventana `clip.frames[grid_offset:grid_offset + max_visible]`.
  - Guardar en cada `FrameCell` el indice real del frame dentro de `clip.frames`, no el indice relativo visible.
  - Manejar `WHEELUPMOUSE` y `WHEELDOWNMOUSE` dentro del panel/grid para desplazar una fila por evento, usando `columns` como paso.
  - Mantener `WHEEL*`, `MIDDLEMOUSE`, trackpad y NDOF fuera del panel como `{"RUNNING_MODAL", "PASS_THROUGH"}`.
  - Actualizar texto de estado a algo como `Showing A-B / N frames` para indicar ventana visible.
  - Redibujar tras scroll sin cambiar seleccion ni playback por si mismo.
- Excluir:
  - Scroll horizontal.
  - Barra de scroll visual.
  - Virtualizacion compleja o cache GPU.
  - Cambios de layout del selector no necesarios para scroll.
  - Undo de clicks de celdas (B7).
  - Recarga de thumbnails obsoletos (M9).
  - Perfilado/caching de `gpu.texture.from_image` (M10).
- Archivos esperados:
  - `spritesheet_frame_selector/ui/visual_selector.py`.
  - Tests nuevos o ajustados si se extrae logica pura de clamp/ventana de frames.

## Validacion

- Validaciones automaticas:
  - Pasado: `python3 -m compileall spritesheet_frame_selector`.
  - Pasado: `python3 -m unittest discover -s tests` con 70 tests.
  - Pasado: helper puro cubre offset inicial 0, clamp al final, scroll por filas usando `columns`, conversion de indice visible a indice real y direccion de scroll por rueda/trackpad.
- Validaciones Blender GUI:
  - Crear clip con mas frames que celdas visibles en el selector.
  - Abrir selector y confirmar que se muestra una ventana inicial, por ejemplo `Showing 1-<max> / N frames`.
  - Usar rueda dentro del grid/panel y confirmar que aparecen frames posteriores.
  - Usar trackpad dentro del grid/panel y confirmar que aparecen frames posteriores/anteriores.
  - Seleccionar/togglear un frame que inicialmente estaba oculto y confirmar que cambia el frame correcto.
  - Usar rueda fuera del panel y confirmar que el evento sigue pasando al viewport, sin mover el grid.
  - Cambiar tamano de ventana o preview size y confirmar que el offset se clamplea y no deja grid vacio.
- Criterio de aceptacion:
  - Todos los frames del clip son accesibles visualmente desde el selector.
  - No se rompe C1: eventos fuera del panel siguen pasando a Blender.
  - No se cambia seleccion/playback salvo accion explicita del usuario sobre una celda o boton.

## Hallazgos Relacionados No Cubiertos

| ID | Motivo |
|---|---|
| B7 | Undo del overlay requiere enrutar click por operador; se mantiene fuera para no mezclar scroll con contrato de undo. |
| M9 | Recarga de thumbnails obsoletos afecta cache de imagenes, no navegacion del grid. |
| M10 | Perfilado de `gpu.texture.from_image` debe medirse antes de agregar cache GPU. |
| M3 | Redraw selectivo de playback no es necesario para que el grid tenga scroll. |

## Proximo Paso Recomendado

Validar en Blender GUI que la rueda dentro del panel desplaza el grid y que la rueda fuera del panel sigue pasando al viewport. Despues resolver el estado de `docs/plans/reinicio-v2-fase-6a-validacion-hito1-selector-modal-lifecycle.md`.

## Resumen De Implementacion

- `VisualSelectorSession` ahora guarda `grid_offset`, `grid_columns` y `grid_max_visible`.
- El grid muestra una ventana de frames basada en `grid_offset` y clamplea el offset contra el tamano actual del clip/layout.
- `FrameCell.index` ahora guarda el indice real del frame en `clip.frames`, para que clicks sobre frames desplazados modifiquen el frame correcto.
- La rueda dentro del panel desplaza una fila por evento; la rueda fuera del panel conserva `{"RUNNING_MODAL", "PASS_THROUGH"}`.
- `TRACKPADPAN` dentro del panel tambien desplaza el grid usando `mouse_y - mouse_prev_y`; fuera del panel sigue pasando al viewport.
- El texto inferior muestra rango visible `Showing A-B / N frames`.

## Correccion Tras Validacion GUI

El primer intento solo manejaba `WHEELUPMOUSE/WHEELDOWNMOUSE` y exigia `event.value == "PRESS"`, por lo que no respondia a trackpad. Se corrigio para manejar `TRACKPADPAN` dentro del panel y para no depender de `PRESS` en eventos de rueda.
