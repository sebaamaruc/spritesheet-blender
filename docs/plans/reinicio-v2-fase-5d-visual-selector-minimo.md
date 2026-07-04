# Plan Fase 5d Workspace-Root - Selector Visual Minimo

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: validado
Referencia superior: `docs/plans/reinicio-v2-master-plan.md`
Plan rector: `docs/plans/reinicio-v2-fase-5-workspace-root-vertical-slices.md`

## Resumen

Implementar un selector visual minimo para el clip activo del workspace activo, consumiendo previews cacheados ya generados por Fase 5c.

El objetivo es que el usuario pueda abrir una superficie visual mas amplia que el sidebar, ver una grilla/contact sheet de frames con thumbnails, alternar seleccion por click y ejecutar acciones globales de seleccion, sin renderizar, generar previews, reproducir playback, exportar ni modificar cache.

Esta fase debe trabajar exclusivamente sobre:

```text
Scene.spritesheet_state.workspaces -> active_workspace -> clips -> active_clip -> frames
```

## Precondiciones

- Fase 5a workspace-root validada.
- Fase 5b workspace-root validada.
- Fase 5c workspace-root preview cache validada.
- El clip activo puede tener `clip.frames` sincronizado y `preview_path` por frame.
- La seleccion persistente vive en `SpriteSheetFrameItem.selected`.

## Fuentes Operativas

- `docs/plans/reinicio-v2-fase-5-workspace-root-vertical-slices.md`
- `docs/specs/mvp_v2.md`
- `docs/architecture/addon_architecture.md`
- `docs/design/visual_selector_strategy.md`
- `docs/specs/validation_plan.md`
- `docs/plans/reinicio-v2-fase-5c-workspace-preview-cache.md`

## Alcance

Incluir:

- Operador para abrir selector visual minimo.
- Superficie visual tipo popup/modal o fallback UI nativo mas amplio que sidebar.
- Grid/contact sheet de thumbnails cacheados.
- Numero de frame visible por celda.
- Estado seleccionado visible.
- Estado no seleccionado atenuado.
- Click toggle de seleccion.
- Acciones globales:
  - Select All;
  - Deselect All;
  - Invert Selection;
  - Select Every N Frames.
- Contadores de frames totales, previews disponibles y seleccionados.
- Mensajes claros si faltan previews, workspace activo, clip activo o datos cacheados.
- Cierre confiable con boton y/o `ESC`.
- Proteccion contra doble invocacion.
- Limpieza explicita de recursos si se usan draw handlers, timers, previews cargadas o recursos GPU.

Excluir:

- Playback preview. Queda para `docs/plans/reinicio-v2-fase-5e-playback-preview.md`.
- Render final.
- Composer.
- Export.
- Generacion o refresh de previews.
- Creacion de carpetas, cache u outputs.
- Zoom/pan sofisticados.
- Drag select.
- Box select.
- Shift range select.
- Shortcuts extensos.

## Decision Tecnica Esperada

La implementacion debe elegir la superficie mas robusta en Blender 5.x para este primer slice:

Opcion preferida:

- `Operator` modal con draw handler en viewport o popup custom suficiente para mostrar thumbnails, siempre que cleanup y doble invocacion sean controlables.

Fallback aceptable:

- UI nativa temporal mas amplia que el sidebar, siempre que muestre thumbnails/contact sheet visual y permita seleccion por frame sin depender de una lista textual pura.

No aceptable:

- Selector solamente textual.
- Selector que renderiza o genera previews al abrir.
- Selector que depende de una lista global `Scene.spritesheet_state.clips`.
- Modal que puede quedar duplicado o dejar handlers/timers vivos al cerrar.

Si durante implementacion se confirma que un modal/draw handler robusto requiere investigacion tecnica adicional, detener la fase antes de implementar una superficie fragil y proponer un spike especifico.

## Cambios Clave

### Helpers Puros

Agregar helpers en `spritesheet_frame_selector/core/selection.py` o modulo equivalente:

- `selected_frame_count(clip)`;
- `preview_ready_count(clip)`;
- `set_all_frames_selected(clip, selected)`;
- `invert_frame_selection(clip)`;
- `select_every_n_frames(clip, n)`;
- `frame_selection_summary(clip)`.

Reglas:

- No usar `bpy.context` en helpers puros.
- No tocar filesystem.
- No modificar `preview_path`, `cache_key`, `cache_folder` ni `cache_dirty`.
- `select_every_n_frames` debe validar `n >= 1`.

### Operadores De Seleccion

Agregar `spritesheet_frame_selector/operators/visual_selector.py` con:

- `SPRITESHEET_OT_visual_selector_open`;
- `SPRITESHEET_OT_frame_select_all`;
- `SPRITESHEET_OT_frame_deselect_all`;
- `SPRITESHEET_OT_frame_invert_selection`;
- `SPRITESHEET_OT_frame_select_every_n`;
- operador o mecanismo interno para toggle de frame por indice/frame number si la superficie visual lo requiere.

Reglas:

- Operadores actuan sobre workspace activo y clip activo.
- Manejan sin traceback:
  - sin escena;
  - sin `spritesheet_state`;
  - sin workspace activo;
  - sin clip activo;
  - clip sin frames;
  - previews faltantes;
  - indices fuera de rango.
- No generan previews.
- No limpian cache.
- No crean carpetas ni archivos.

### Superficie Visual

Crear modulo recomendado `spritesheet_frame_selector/ui/visual_selector.py` o `spritesheet_frame_selector/preview/selector.py`, segun encaje con la arquitectura.

Requisitos minimos:

- Recibe workspace id y clip id o valida que workspace/clip activo no cambie mientras esta abierto.
- Muestra thumbnails desde `frame.preview_path`.
- Tolera archivos faltantes con placeholder tecnico simple.
- Muestra numero de frame.
- Muestra estado seleccionado/no seleccionado.
- Permite click toggle.
- Muestra contadores y acciones globales.
- Cierra sin perder seleccion persistente.
- Previene doble apertura.

Si usa draw handlers:

- registrar handler al abrir;
- remover handler al cerrar;
- remover handler en `unregister()`;
- proteger acceso a imagenes/GPU con `try/finally`;
- liberar imagenes cargadas si son temporales;
- invalidar o cerrar al cambiar workspace/clip.

Si usa UI nativa:

- mantener el codigo preparado para reemplazar la superficie por modal/draw handler en una fase posterior;
- no mezclar helpers de seleccion con layout UI.

### Panel

Actualizar `spritesheet_frame_selector/ui/panels.py`:

- boton `Open Visual Selector`;
- mensaje si no hay previews;
- contador de frames seleccionados;
- no abrir selector automaticamente;
- no generar preview desde el selector.

### Registro

Actualizar `spritesheet_frame_selector/registration.py`:

- registrar operadores de visual selector despues de preview/operators existentes;
- registrar clases UI auxiliares si existen;
- limpiar handlers/timers/resources en `unregister()` si el selector los usa.

## Reglas De Implementacion

- No copiar codigo V1 como base estructural.
- No mantener modelo dual legacy/workspace.
- No buscar clips en `Scene.spritesheet_state.clips`.
- No generar previews.
- No renderizar.
- No implementar playback.
- No exportar.
- No crear outputs, ZIPs ni caches.
- No hacer IO desde `draw`.
- No bloquear cierre del modal/popup.
- No dejar handlers, timers, images ni recursos GPU vivos tras cerrar o desactivar addon.
- La seleccion se escribe solo en `SpriteSheetFrameItem.selected`.
- El selector debe tolerar cache incompleto o stale con warning, no traceback.

## Plan De Ejecucion

1. Verificar `git status --short --ignored`.
2. Revisar implementacion vigente de 5a/5b/5c workspace-root.
3. Confirmar que el selector consumira `clip.frames` y `frame.preview_path`, no cache folders directamente salvo lectura pasiva.
4. Implementar helpers puros de seleccion.
5. Implementar operadores de acciones globales.
6. Implementar operador de apertura del selector.
7. Implementar superficie visual minima o fallback UI visual aceptable.
8. Integrar boton y estado en panel.
9. Actualizar registro/unregister y cleanup.
10. Agregar tests unitarios para helpers de seleccion.
11. Ejecutar validaciones automaticas.
12. Ejecutar validacion Blender background para operadores y persistencia de seleccion.
13. Si existe forma viable de prueba UI/manual asistida, documentar pasos; no forzar GUI automatizada si Blender background no puede validar clicks visuales.
14. Limpiar residuos.
15. Actualizar plan y PCS solo si las validaciones aplicables pasan.

## Validaciones Automaticas

- `python3 -m compileall spritesheet_frame_selector`.
- `python3 -m unittest discover -s tests`.
- Busqueda de contrato legacy:
  - no debe aparecer `spritesheet_state.clips`;
  - no debe aparecer `spritesheet_state.active_clip_index`;
  - no debe aparecer `spritesheet_state.export_settings`.

Tests unitarios recomendados:

- select all selecciona todos los frames;
- deselect all deselecciona todos;
- invert invierte seleccion mixta;
- select every N mantiene solo cada N frames esperado;
- `n <= 0` se rechaza de forma controlada;
- contador de seleccion y previews funciona con paths vacios;
- helpers no modifican `preview_path`, `cache_key`, `cache_folder` ni `cache_dirty`.

## Validaciones Blender Background

Usar `/Applications/Blender.app/Contents/MacOS/Blender` si existe.

Validar:

- import del addon;
- doble ciclo `register()` / `unregister()`;
- crear workspace, camera, collection y clip;
- generar previews con 5c o crear frames con `preview_path` controlado si no se necesita render en esta fase;
- ejecutar operadores globales:
  - select all;
  - deselect all;
  - invert;
  - select every N;
- confirmar que `SpriteSheetFrameItem.selected` cambia y persiste en `.blend`;
- ejecutar operador de apertura del selector y confirmar que cancela o finaliza sin traceback en background, segun limitacion tecnica;
- confirmar que no crea previews, cache folders nuevas ni outputs;
- unregister limpia recursos sin errores.

## Validaciones Manuales Posteriores

- Abrir Blender UI.
- Crear workspace y clip.
- Generar previews con Fase 5c.
- Abrir selector visual.
- Confirmar grilla/contact sheet con thumbnails.
- Toggle por click en varios frames.
- Usar Select All, Deselect All, Invert Selection y Select Every N.
- Confirmar contador seleccionado.
- Cerrar con boton y `ESC`.
- Reabrir selector y confirmar seleccion persistente.
- Intentar abrir dos veces rapidamente y confirmar que no quedan dos selectores activos.
- Cambiar workspace/clip mientras esta abierto y confirmar cierre o invalidacion segura.
- Desactivar/reactivar addon y confirmar que no quedan handlers/timers.

## Validaciones De No Alcance

- Confirmar que no se agrego playback.
- Confirmar que no se agrego render final.
- Confirmar que no se agrego composer.
- Confirmar que no se agrego export.
- Confirmar que no se generan previews desde el selector.
- Confirmar que no quedan `__pycache__`, `*.pyc`, `.DS_Store`, ZIPs ni outputs nuevos dentro del repo.

## Riesgos

- Blender background no puede validar interacciones visuales reales de click/draw handler.
- Draw handlers y recursos GPU son sensibles a reload/unregister.
- Un modal fragil puede degradar Blender si no limpia bien handlers/timers.
- UI nativa puede ser menos visual que el objetivo final; si se usa fallback, debe quedar una ruta clara hacia grilla modal mejor.
- Cargar muchas thumbnails puede afectar rendimiento; el MVP debe ser simple y acotado.

## PCS Y Criterio De Termino

Al ejecutar la fase:

- Guardar este plan como aprobado solo si el usuario lo aprueba explicitamente.
- Marcar `Estado De Ejecucion: validado` solo si pasan compile, unit tests, Blender background aplicable, limpieza de residuos y revision manual documentada cuando corresponda.
- Actualizar `.context/agent_context.md`, `.context/index.md`, `.context/handoff.md` y `.context/worklog.jsonl`.
- Dejar como siguiente paso preparar `docs/plans/reinicio-v2-fase-5e-playback-preview.md`.

Criterio final:

- El usuario puede abrir un selector visual minimo desde el panel.
- El selector muestra previews existentes y estado seleccionado/no seleccionado.
- El usuario puede cambiar seleccion con click o fallback visual aceptable.
- Acciones globales funcionan y persisten.
- El selector cierra sin fugas conocidas.
- No hay playback/render/export implementado en esta fase.

## Supuestos

- Playback se implementara en Fase 5e para mantener 5d acotada y verificable.
- La primera version prioriza robustez, cleanup y persistencia sobre interacciones avanzadas.
- El selector puede empezar con una superficie visual simple si mantiene ruta tecnica clara hacia una grilla modal mas rica.

## Resultado De Ejecucion

Validado el 2026-07-03.

Decision tecnica aplicada:

- Se implemento un fallback visual nativo robusto mediante dialogo ancho (`invoke_props_dialog`) con grilla/contact sheet de thumbnails cargados desde `frame.preview_path`.
- No se uso draw handler ni timer en esta fase; esto reduce riesgo de fugas en reload/unregister.
- La ruta queda preparada para reemplazar la superficie por un modal/draw handler mas rico en una fase posterior sin cambiar helpers de seleccion ni persistencia.

Cambios implementados:

- Nuevo helper puro `spritesheet_frame_selector/core/selection.py`:
  - conteo de seleccion;
  - conteo de previews;
  - select all;
  - deselect all;
  - invert selection;
  - select every N;
  - resumen de seleccion.
- Nueva superficie visual `spritesheet_frame_selector/ui/visual_selector.py`:
  - grilla/contact sheet con thumbnails existentes;
  - frame number visible;
  - estado seleccionado/no seleccionado;
  - placeholders/warnings para previews faltantes;
  - cleanup de preview collection.
- Nuevos operadores `spritesheet_frame_selector/operators/visual_selector.py`:
  - `SPRITESHEET_OT_visual_selector_open`;
  - `SPRITESHEET_OT_frame_select_all`;
  - `SPRITESHEET_OT_frame_deselect_all`;
  - `SPRITESHEET_OT_frame_invert_selection`;
  - `SPRITESHEET_OT_frame_select_every_n`;
  - `SPRITESHEET_OT_frame_toggle_selection`.
- Panel actualizado en `spritesheet_frame_selector/ui/panels.py` con boton `Open Visual Selector`.
- Registro centralizado actualizado en `spritesheet_frame_selector/registration.py`, incluyendo cleanup del selector en `unregister()`.
- Tests unitarios agregados en `tests/test_selection.py`.

Validaciones ejecutadas:

- `python3 -m compileall spritesheet_frame_selector`: OK.
- `python3 -m unittest discover -s tests`: OK, 25 tests.
- Busqueda de contrato legacy `spritesheet_state.clips`, `spritesheet_state.active_clip_index`, `spritesheet_state.export_settings`, `state.clips`, `state.active_clip_index`, `state.export_settings`: OK, sin resultados en codigo/tests.
- Blender background con `/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup`: OK, `SFS_5D_VISUAL_SELECTOR_OK`.
- Validacion Blender confirmo:
  - doble ciclo `register()` / `unregister()`;
  - operadores select all, deselect all, invert, select every N y toggle;
  - persistencia de seleccion save/reopen;
  - operador de apertura del selector sin traceback en background.
- Limpieza de residuos: OK, sin `__pycache__`, `*.pyc`, `.DS_Store` ni temporales 5d dentro del repo.

Limitacion:

- Blender background no valida clicks reales sobre el dialogo visual. La validacion manual posterior debe confirmar grilla, thumbnails y toggle por click en UI.

Proximo paso recomendado:

- Preparar `docs/plans/reinicio-v2-fase-5e-playback-preview.md`.
