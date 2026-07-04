# Plan Fase 5e1 - Selector Modal Y Playback UX

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: validado
Referencia superior: `docs/plans/reinicio-v2-master-plan.md`
Plan rector: `docs/plans/reinicio-v2-fase-5-workspace-root-vertical-slices.md`
Spike previo: `docs/plans/reinicio-v2-fase-5e1-spike-selector-modal-preview-modes.md`
Especificacion tecnica: `docs/specs/selector_modal_preview_modes_spike.md`

## Resumen

Corregir la experiencia real de selector/playback antes de avanzar a render final.

La Fase 5d/5e dejo un selector funcional pero insuficiente para inspeccion visual: thumbnails demasiado pequenos, mucho texto por celda y playback sin visor grande del resultado. Esta fase reemplaza la superficie nativa temporal por un selector modal/custom, agrega preview modes persistentes, ajusta `preview_size` a limites definidos por el usuario y reorganiza el panel principal sin eliminar controles importantes.

## Decisiones Cerradas

- El selector debe avanzar a superficie modal/custom.
- `selector_mode` debe vivir en `.blend`.
- `preview_size` debe tener:
  - minimo: `32`;
  - default: `64`;
  - preset visible: `128`;
  - maximo: `256`.
- Preview modes requeridos:
  - `SOLID`;
  - `MATERIAL`;
  - `RENDERED`.
- El playback debe mostrar una vista grande del frame actual.
- La grilla del selector no debe depender de texto ni checkbox por celda.
- Seleccion y playback se comunican con contornos visuales.
- Modo `EDIT`: click alterna inclusion del frame en spritesheet.
- Modo `PLAY`: click cambia frame actual/punto de inicio sin alterar seleccion.

## Precondiciones

- Fase 5a workspace-root validada.
- Fase 5b workspace-root validada.
- Fase 5c workspace-root preview cache validada.
- Fase 5d selector visual minimo validada.
- Fase 5e playback preview validada.
- Spike `docs/plans/reinicio-v2-fase-5e1-spike-selector-modal-preview-modes.md` validado.

## Fuentes Operativas

- `docs/specs/selector_modal_preview_modes_spike.md`
- `docs/design/visual_selector_strategy.md`
- `docs/specs/mvp_v2.md`
- `docs/architecture/addon_architecture.md`
- `docs/specs/validation_plan.md`
- `docs/plans/reinicio-v2-fase-5-workspace-root-vertical-slices.md`
- `docs/plans/reinicio-v2-fase-5d-visual-selector-minimo.md`
- `docs/plans/reinicio-v2-fase-5e-playback-preview.md`

## Alcance

Incluir:

- Agregar `selector_mode` persistente en `SpriteSheetWorkspace`.
- Agregar preview modes persistentes:
  - default por workspace;
  - override opcional por clip.
- Agregar resolucion efectiva de preview mode.
- Incluir preview mode efectivo en cache key.
- Ajustar `preview_size`:
  - `min=32`;
  - `default=64`;
  - `max=256`;
  - presets UI `32`, `64`, `128`, `256`.
- Reemplazar selector visual nativo por superficie modal/custom.
- Dibujar visor grande del frame actual.
- Dibujar grilla de thumbnails grandes.
- Dibujar contorno de seleccionado y contorno de frame actual/playback.
- Eliminar checkbox y texto repetitivo por celda.
- Mantener numero de frame pequeno como overlay.
- Implementar modo `EDIT` y modo `PLAY`.
- Reordenar panel principal para reducir friccion sin esconder configuracion necesaria.
- Mantener Play/Pause/Stop integrados.
- Mantener acciones globales de seleccion.
- Cleanup robusto de draw handlers, timers, imagenes/texturas y estado runtime.

Excluir:

- Render final.
- Composer.
- Export PNG.
- Atlas multi-clip.
- JSON metadata.
- Drag select.
- Box select.
- Shift range.
- Scrubbing avanzado.
- Zoom/pan sofisticado.
- Packing irregular.

## Modelo Persistente

### Workspace

Actualizar `SpriteSheetWorkspace`:

- `selector_mode: EnumProperty`
  - `EDIT`
  - `PLAY`
  - default: `EDIT`

Motivo:

- El modo del selector pertenece a la forma de trabajar dentro del workspace.
- El modo de preview no pertenece al workspace: es una decision bajo demanda por clip al generar cache.

### Clip

Actualizar `SpriteSheetClip`:

- `preview_mode: EnumProperty`
  - `SOLID`
  - `MATERIAL`
  - `RENDERED`
  - default: `SOLID`
- `preview_size: IntProperty`
  - default: `64`
  - min: `32`
  - max: `256`

Motivo:

- Algunos clips pueden requerir textura o luz distinta segun lo que se quiera inspeccionar al generar preview.
- El tamano de preview sigue siendo por clip porque diferentes clips pueden requerir distinto nivel de inspeccion.

## Preview Mode Efectivo

Agregar helper en `spritesheet_frame_selector/core/workspace_state.py` o modulo dedicado:

- `effective_preview_mode(workspace, clip)`.

Regla:

```text
usar clip.preview_mode
```

Actualizar cache:

- `build_preview_cache_key(...)` debe incluir `effective_preview_mode`.
- Cambiar preview mode debe marcar `cache_dirty=True`.
- Cambiar `preview_size` debe seguir marcando `cache_dirty=True`.

## Backend Preview

Actualizar `spritesheet_frame_selector/preview/generator.py` para aceptar `preview_mode`.

Contrato:

- `SOLID`: usar viewport/OpenGL cuando haya contexto UI.
- `MATERIAL`: usar viewport/OpenGL cuando haya contexto UI.
- `RENDERED`: usar render still nativo con `BLENDER_EEVEE` o engine activo compatible.
- En background:
  - OpenGL no funciona;
  - validar ruta `RENDERED` con `bpy.ops.render.render(write_still=True)`;
  - no fingir que `SOLID/MATERIAL` estan validados en background.

Reglas:

- No reintroducir `WorldSwapContext`.
- No usar fallback silencioso a `scene.camera`.
- Respetar camera efectiva y collections efectivas.
- Restaurar frame, camera, render settings y visibilidad con `try/finally`.
- No generar previews desde el selector modal; solo desde operadores `Generate/Refresh Preview`.

## Selector Modal/Custom

Crear o reemplazar modulo:

- `spritesheet_frame_selector/ui/visual_selector.py`

Estructura recomendada:

```text
Modal controller
  workspace_id
  clip_id
  area
  draw_handler
  loaded_images/textures
  layout_rects
  current_hover
  current_frame
```

Usar:

- `bpy.types.Operator` modal.
- `SpaceView3D.draw_handler_add(..., 'WINDOW', 'POST_PIXEL')`.
- `gpu`, `blf`, `gpu_extras.batch`.

Requisitos:

- Abrir solo una instancia.
- Cerrar con `ESC`, `RIGHTMOUSE` y boton/accion visible.
- Cerrar o invalidar si cambia workspace/clip.
- No escribir seleccion en el clip equivocado.
- Remover draw handler siempre.
- Detener playback o invalidarlo al cerrar.
- Liberar imagenes/texturas temporales.
- Cleanup desde `unregister()`.

## Layout Selector

Layout objetivo:

```text
Header compacto:
  Workspace / Clip / Mode / Preview Mode / Preview Size

Visor grande:
  Frame actual o frame bajo playback

Controles compactos:
  Edit/Play mode
  Play / Pause / Stop
  Select All / Deselect / Invert / Every N
  Close

Grilla:
  thumbnails grandes
  borde seleccionado
  borde frame actual
  numero pequeno de frame
```

Reglas visuales:

- No checkbox por celda.
- No texto `Selected/Skipped` por celda.
- Numero de frame pequeno y discreto.
- Seleccionado: contorno estable.
- Frame actual/playback: contorno distinto.
- Seleccionado + actual: doble contorno o contorno principal + marca secundaria.
- Preview faltante: placeholder tecnico simple.
- Cache stale: warning global, no bloqueo.

## Comportamiento Por Modo

### EDIT

- Click sobre celda alterna `frame.selected`.
- Acciones globales disponibles.
- Play/Pause/Stop visibles pero secundarios.
- El visor grande puede mostrar frame hover/current.

### PLAY

- Click sobre celda cambia frame actual o punto de inicio.
- Click no cambia `frame.selected`.
- Play/Pause/Stop prioritarios.
- El playback usa solo frames seleccionados.
- El visor grande muestra el frame actual de playback.

## Panel Principal

Reordenar sin reducir funcionalidad:

1. Workspace
   - selector/lista;
   - nombre;
   - camera default;
   - collections default.
2. Clip
   - lista;
   - nombre;
   - rango;
   - FPS;
   - `preview_size`;
   - overrides de camera/collections/preview mode.
3. Preview Cache
   - preview mode efectivo;
   - Generate;
   - Refresh;
   - Clear;
   - warnings.
4. Selector / Playback
   - Open Selector;
   - selector mode;
   - selected count;
   - Play/Pause/Stop compacto si aplica.
5. Export Settings
   - mantener visible, compacto, sin introducir export en esta fase.

Reglas:

- `draw()` no debe mutar indices.
- `draw()` no debe crear carpetas.
- `draw()` no debe renderizar.
- No duplicar warnings extensos si se pueden resumir.

## Operadores

Actualizar o crear:

- `SPRITESHEET_OT_visual_selector_open`
- `SPRITESHEET_OT_visual_selector_close` si aplica
- `SPRITESHEET_OT_visual_selector_set_mode`
- `SPRITESHEET_OT_preview_size_preset`
- `SPRITESHEET_OT_frame_toggle_selection` adaptado para modal
- Operadores playback existentes si necesitan integracion con frame actual del modal

Reglas:

- Operadores validan workspace/clip activo.
- Operadores toleran sin frames/previews.
- Operadores no generan previews salvo `Generate/Refresh Preview`.

## Registro Y Cleanup

Actualizar `registration.py`:

- registrar nuevas clases/operators;
- llamar cleanup del selector modal en `unregister()`;
- llamar cleanup de playback en `unregister()`;
- mantener doble ciclo `register()`/`unregister()`.

## Tests Automaticos

Agregar/actualizar tests unitarios:

- `effective_preview_mode` usa `clip.preview_mode`.
- cache key cambia al cambiar preview mode.
- cache key cambia al cambiar preview size.
- `preview_size` helper/preset respeta 32/64/128/256.
- valores fuera de rango se clamped/rechazan segun implementacion.
- modo `EDIT` permite toggle.
- modo `PLAY` no cambia seleccion en helpers puros si se extrae logica.

Validaciones automaticas:

- `python3 -m compileall spritesheet_frame_selector`
- `python3 -m unittest discover -s tests`
- busqueda legacy:
  - no `spritesheet_state.clips`;
  - no `spritesheet_state.active_clip_index`;
  - no `spritesheet_state.export_settings`.

## Validaciones Blender Background

Validar:

- import addon;
- doble ciclo `register()` / `unregister()`;
- persistencia de:
  - `workspace.selector_mode`;
  - `clip.preview_mode`;
  - `clip.preview_size`.
- cache key cambia con preview mode.
- preview `RENDERED` puede generarse con render still en background.
- selector modal no debe intentar dibujar GPU en background; debe cancelar o reportar contexto no disponible sin traceback.
- cleanup en unregister no falla sin modal activo.

## Validacion Manual GUI Obligatoria

En Blender GUI:

1. Activar addon.
2. Crear workspace y clip.
3. Configurar `preview_size=64`, generar preview y confirmar que es pequeño.
4. Configurar `preview_size=128`, refresh y confirmar mejora.
5. Configurar `preview_size=256`, refresh y confirmar limite maximo.
6. Probar `SOLID`, `MATERIAL`, `RENDERED` segun disponibilidad.
7. Abrir selector modal.
8. Confirmar visor grande del frame actual.
9. Confirmar grilla con thumbnails grandes.
10. Confirmar contorno seleccionado.
11. Confirmar contorno de frame actual/playback.
12. En `EDIT`, click alterna seleccion.
13. En `PLAY`, click no altera seleccion y cambia frame actual/punto de inicio.
14. Ejecutar Play/Pause/Stop y confirmar que el visor grande muestra la animacion.
15. Cerrar con `ESC`, `RIGHTMOUSE` y control visible.
16. Abrir/cerrar varias veces sin handlers duplicados.
17. Cambiar workspace/clip mientras esta abierto y confirmar cierre/invalidez controlada.
18. Desactivar/reactivar addon sin errores.

## Riesgos

### GPU/Draw Handler

Riesgo:

- fuga de handler o texturas.

Mitigacion:

- cleanup centralizado;
- unregister defensivo;
- validacion manual de abrir/cerrar repetido.

### Preview Modes

Riesgo:

- `SOLID/MATERIAL` dependen de contexto viewport y no son validables en background.

Mitigacion:

- background valida modelo y `RENDERED`;
- manual GUI valida OpenGL/viewport.

### Alcance

Riesgo:

- convertir esta fase en rediseño total de UI/export.

Mitigacion:

- no implementar render/export/composer;
- panel solo se reordena;
- selector se enfoca en inspeccion, seleccion y playback.

## PCS Y Criterio De Termino

Al aprobar y ejecutar esta fase:

- Cambiar este plan a:
  - `Estado: aprobado`;
  - `Autoridad: usuario`;
  - `Modo de ejecucion: ejecutar sin replanificar`.
- Marcar `Estado De Ejecucion: validado` solo si pasan:
  - compile;
  - unit tests;
  - Blender background aplicable;
  - limpieza de residuos;
  - validacion manual GUI minima.
- Actualizar `.context/agent_context.md`, `.context/index.md`, `.context/handoff.md` y `.context/worklog.jsonl`.
- Dejar como siguiente paso preparar `docs/plans/reinicio-v2-fase-5f-render-final-workspace-aware.md`.

Criterio final:

- El selector modal/custom permite inspeccion visual real.
- Playback muestra vista grande del frame actual.
- `EDIT` y `PLAY` funcionan sin modificar seleccion accidentalmente.
- Preview size queda limitado a 32-256 con default 64 y presets visibles.
- Preview mode queda persistente y participa en cache.
- No hay render final/export/composer implementado.

## Resultado De Ejecucion

Estado: validado
Fecha: 2026-07-03

Cambios implementados:

- `SpriteSheetWorkspace.selector_mode`.
- `SpriteSheetClip.preview_mode`.
- `SpriteSheetClip.preview_size` limitado a `32..256`, default `64`.
- Cache key incluye preview mode efectivo.
- Preview backend recibe preview mode y usa `RENDERED` por render still.
- Presets de preview size `32`, `64`, `128`, `256`.
- Selector visual reemplazado por superficie modal/custom con draw handler 2D.
- Selector modal dibuja visor grande, grilla, contorno seleccionado y contorno de frame actual.
- Modo `EDIT` alterna seleccion por click.
- Modo `PLAY` cambia frame activo sin alterar seleccion.
- Panel principal reordenado por workspace, clip, preview cache, selector/playback y export settings.
- Cleanup del selector modal se mantiene en `unregister()`.

Correccion posterior por validacion manual GUI:

- El selector modal ya no dibuja un fondo de pantalla completa sobre todo el viewport.
- La superficie modal queda acotada a un panel flotante con margenes seguros para no cubrir toolbar/header del View3D.
- La grilla de thumbnails solo dibuja las celdas que caben dentro del panel.
- Los controles del selector se compactaron en filas para evitar overflow vertical.
- El visor grande preserva el aspect ratio de la imagen y evita estirar el preview.
- El selector modal ahora usa todo el espacio util disponible del View3D, sin limite maximo artificial.
- `preview_size` se movio desde `Clip` a la seccion `Selector`.
- Los controles de playback se retiraron del panel principal; quedan dentro del selector modal.
- Los botones `Edit` / `Play` se retiraron de `Workspace` y se movieron a `Selector`.
- El modo de preview quedo como propiedad directa del clip en `Preview Cache`; se eliminaron el default por workspace y el override porque la generacion de preview es bajo demanda por clip.
- `Preview Cache` quedo enfocado en acciones: modo, Generate, Refresh y Clear.
- La informacion de cache se separo en `Preview Status` para reducir ruido visual.
- `Include in Export` se mantiene como metadata futura y se etiqueta como `Include in Export (future)` mientras export no exista.
- El selector modal reserva el ancho del panel lateral `N` cuando esta visible, porque el draw handler del View3D no puede dibujar por encima de esa region UI global.

Validaciones ejecutadas:

- `python3 -m compileall spritesheet_frame_selector`: OK.
- `python3 -m unittest discover -s tests`: OK, 38 tests.
- Busqueda de contrato legacy en `spritesheet_frame_selector` y `tests`: OK, sin coincidencias.

Validaciones pendientes:

- Blender background no pudo completarse dentro del sandbox: Blender 5.1.1 crashea antes de ejecutar Python con `exit code 139`.
- La ejecucion fuera del sandbox fue rechazada por politica del entorno actual.
- La limpieza automatica de `__pycache__` generados por `compileall` fue rechazada por la politica de aprobacion del entorno; no se intento una via alternativa.
- La validacion manual GUI fue aceptada por el usuario para avanzar: quedan cambios menores de UI no bloqueantes.
- No avanzar a implementar esos ajustes menores dentro de 5e1 salvo que el usuario lo pida explicitamente; capturarlos en una fase futura de pulido UI si siguen siendo relevantes.
