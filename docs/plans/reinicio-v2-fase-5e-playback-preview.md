# Plan Fase 5e Workspace-Root - Playback Preview

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: validado
Referencia superior: `docs/plans/reinicio-v2-master-plan.md`
Plan rector: `docs/plans/reinicio-v2-fase-5-workspace-root-vertical-slices.md`

## Resumen

Implementar playback preview para el clip activo del workspace activo, usando exclusivamente previews cacheados y la seleccion persistente creada en fases anteriores.

El objetivo es que el usuario pueda reproducir rapidamente los frames seleccionados, en orden temporal y respetando el FPS del clip, sin renderizar, sin generar previews, sin modificar cache y sin exportar.

Esta fase debe trabajar exclusivamente sobre:

```text
Scene.spritesheet_state.workspaces -> active_workspace -> clips -> active_clip -> frames
```

## Precondiciones

- Fase 5a workspace-root validada.
- Fase 5b workspace-root validada.
- Fase 5c workspace-root preview cache validada.
- Fase 5d selector visual minimo validada.
- El selector visual puede consumir `clip.frames` y `frame.preview_path`.
- La seleccion persistente vive en `SpriteSheetFrameItem.selected`.

## Fuentes Operativas

- `docs/plans/reinicio-v2-fase-5-workspace-root-vertical-slices.md`
- `docs/specs/mvp_v2.md`
- `docs/architecture/addon_architecture.md`
- `docs/design/visual_selector_strategy.md`
- `docs/specs/validation_plan.md`
- `docs/plans/reinicio-v2-fase-5d-visual-selector-minimo.md`

## Objetivo De Producto

Permitir que el usuario valide timing e inclusion de frames antes del render/export final.

El playback debe ser feedback de seleccion, no una segunda fuente de verdad. La seleccion sigue perteneciendo al modelo persistente del clip; el estado de playback es runtime y descartable.

## Alcance

Incluir:

- Reproducir solo frames seleccionados del clip activo.
- Reproducir en orden temporal segun `frame_number`.
- Respetar `clip.fps`.
- Controles `Play`, `Pause` y `Stop`.
- Loop simple si no compromete estabilidad.
- Indicador de frame actual durante playback.
- Feedback visible dentro del selector visual y/o panel.
- Validacion de previews faltantes antes de reproducir.
- Limpieza explicita de timers al detener, cerrar selector, cambiar estado o desactivar addon.
- Tests unitarios para helpers puros de secuencia de playback.
- Validacion Blender background de operadores y limpieza.

Excluir:

- Render final.
- Generacion o refresh de previews.
- Clear cache.
- Export PNG.
- Composer.
- Atlas multi-clip.
- JSON metadata.
- Scrubbing avanzado.
- Timeline alternativo.
- Audio.
- Drag select, box select o shift range.
- Persistir estado runtime `playing`, `paused` o `current_frame`.

## Decision Tecnica Propuesta

Implementar playback como una capa runtime independiente:

- Helpers puros para calcular la secuencia reproducible.
- Controlador runtime en `spritesheet_frame_selector/playback/controller.py`.
- Operadores Blender como adaptadores UI.
- UI pasiva que solo consulta estado runtime y dibuja controles.

No se debe guardar `current_frame`, `is_playing` ni timers dentro de `PropertyGroup`, porque esos datos no pertenecen al `.blend`.

Loop puede manejarse como opcion runtime del operador `Play`. Si durante implementacion se decide persistir una preferencia `loop` por clip, debe justificarse dentro del plan ejecutado y no debe mezclarse con estado runtime.

## Cambios Clave

### Helpers Puros

Agregar `spritesheet_frame_selector/playback/sequence.py` o modulo equivalente con funciones testeables fuera de Blender:

- `selected_playback_frames(clip)`;
- `playback_frame_numbers(clip)`;
- `playback_preview_paths(clip)`;
- `playback_interval_seconds(fps)`;
- `next_playback_index(current_index, frame_count, loop)`;
- `playback_ready_summary(clip)`.

Reglas:

- No usar `bpy.context`.
- No importar `bpy` si se puede evitar.
- No tocar filesystem.
- No modificar seleccion.
- No modificar cache.
- Ordenar por `frame_number` para evitar depender del orden accidental de la collection.
- Rechazar `fps <= 0` de forma controlada.
- Ignorar o reportar frames seleccionados sin `preview_path`, segun contrato del helper.

Contrato recomendado:

- `selected_playback_frames(clip)` devuelve solo frames seleccionados.
- `playback_ready_summary(clip)` reporta:
  - frames seleccionados;
  - frames seleccionados con preview path;
  - frames seleccionados sin preview path;
  - si la secuencia puede reproducirse.
- El operador `Play` cancela si no hay al menos un frame seleccionado con preview path.

### Controlador Runtime

Agregar `spritesheet_frame_selector/playback/controller.py`.

Responsabilidades:

- Mantener una unica sesion activa de playback.
- Guardar snapshot runtime:
  - `workspace_id`;
  - `clip_id`;
  - `frame_numbers`;
  - `preview_paths`;
  - `fps`;
  - `loop`;
  - `current_index`;
  - `status`.
- Iniciar timer de Blender para avanzar frames.
- Evitar timers duplicados.
- Pausar sin perder indice actual.
- Detener y limpiar sesion.
- Exponer estado de solo lectura para UI:
  - `is_playing()`;
  - `is_paused()`;
  - `current_frame_number()`;
  - `current_preview_path()`;
  - `active_session_summary()`.
- Limpiar timer en `unregister()`.

Reglas:

- No renderizar.
- No generar previews.
- No escribir seleccion.
- No crear carpetas ni archivos.
- No depender de `scene.camera`.
- No asumir que el selector sigue abierto.
- Si el workspace o clip activo cambia, el playback debe detenerse o invalidarse de forma controlada.
- Si se elimina el clip/workspace durante playback, no debe haber traceback.
- Si un preview path desaparece durante playback, debe saltarse o detenerse con estado claro, no romper el timer.
- El callback del timer debe retornar `None` al terminar o al invalidarse.

### Operadores

Agregar `spritesheet_frame_selector/operators/playback.py` con:

- `SPRITESHEET_OT_playback_play`;
- `SPRITESHEET_OT_playback_pause`;
- `SPRITESHEET_OT_playback_stop`.

Opcional si simplifica UI:

- `SPRITESHEET_OT_playback_toggle`;
- `SPRITESHEET_OT_playback_step_next`;
- `SPRITESHEET_OT_playback_step_previous`.

Reglas:

- Operadores actuan sobre workspace activo y clip activo.
- Validan:
  - sin escena;
  - sin `spritesheet_state`;
  - sin workspace activo;
  - sin clip activo;
  - clip sin frames;
  - sin frames seleccionados;
  - frames seleccionados sin previews;
  - `fps <= 0`;
  - playback ya activo para otro workspace/clip.
- Reportan errores con `self.report()`.
- `Play` debe crear una sesion nueva o reanudar si esta pausada para el mismo workspace/clip.
- `Pause` no debe fallar si no hay playback activo.
- `Stop` debe ser idempotente.

### UI Del Selector Visual

Actualizar `spritesheet_frame_selector/ui/visual_selector.py`.

Agregar:

- Controles `Play`, `Pause`, `Stop`.
- Indicador de estado:
  - stopped;
  - playing;
  - paused.
- Indicador de frame actual.
- Highlight visual simple del frame actual dentro de la grilla si esta visible.
- Warning si hay seleccion pero faltan previews para algunos frames.
- Warning si no hay frames seleccionados.

Reglas:

- `draw()` no debe iniciar ni detener timers.
- `draw()` no debe mutar seleccion.
- `draw()` no debe crear carpetas ni archivos.
- La carga de iconos/preview thumbnails debe seguir usando la infraestructura existente de Fase 5d.
- Si el selector se cierra, la implementacion debe detener playback o dejarlo detenido por el operador de cierre/lifecycle definido.

### Panel Principal

Actualizar `spritesheet_frame_selector/ui/panels.py`.

Agregar una seccion `Playback Preview` o controles dentro de la seccion actual del selector:

- `Play`;
- `Pause`;
- `Stop`;
- contador de frames seleccionados;
- indicador de frame actual si playback esta activo;
- warning si faltan previews o seleccion.

Reglas:

- El panel solo dibuja estado y dispara operadores.
- No debe escribir indices activos durante `draw()`.
- No debe crear, borrar ni leer carpetas de cache directamente.

### Registro Y Cleanup

Actualizar `spritesheet_frame_selector/registration.py`.

Agregar:

- Registro de operadores de playback despues de preview/visual selector.
- Cleanup de playback en `unregister()`.

Reglas:

- `unregister()` debe llamar cleanup aunque el registro haya sido parcial.
- Cleanup debe tolerar no tener timer activo.
- Doble ciclo `register()` / `unregister()` debe seguir funcionando.

## Reglas De Implementacion

- No copiar codigo V1 como base estructural.
- No reintroducir modelo legacy `Scene.spritesheet_state.clips`.
- No implementar render/export/composer.
- No generar previews.
- No crear cache folders nuevas.
- No crear outputs, ZIPs ni archivos de prueba dentro del repo.
- No usar `bpy.context` dentro de helpers puros.
- No mutar estado complejo desde `draw()`.
- No dejar timers activos tras stop, unregister o cierre del selector.
- No usar nombres visibles como identificadores de sesion.
- El playback debe usar ids estables de workspace y clip.
- El playback debe consumir `frame.preview_path` existente.
- La seleccion persistente no debe cambiar durante playback.

## Plan De Ejecucion

1. Verificar `git status --short --ignored`.
2. Leer implementacion vigente de:
   - `spritesheet_frame_selector/ui/visual_selector.py`;
   - `spritesheet_frame_selector/operators/visual_selector.py`;
   - `spritesheet_frame_selector/core/selection.py`;
   - `spritesheet_frame_selector/core/workspace_state.py`;
   - `spritesheet_frame_selector/registration.py`.
3. Confirmar que el selector actual no renderiza ni genera previews.
4. Implementar helpers puros de secuencia de playback.
5. Implementar controlador runtime de playback.
6. Implementar operadores `Play`, `Pause` y `Stop`.
7. Integrar controles en selector visual.
8. Integrar estado minimo en panel principal.
9. Registrar operadores y cleanup en unregister.
10. Agregar tests unitarios para helpers puros.
11. Agregar tests unitarios o pruebas de controlador con dobles simples cuando sea viable sin Blender.
12. Ejecutar validaciones automaticas.
13. Ejecutar validacion Blender background de lifecycle, operadores y cleanup.
14. Verificar que no se agregaron render/export/cache outputs.
15. Limpiar residuos generados por validacion.
16. Actualizar el plan y PCS solo si las validaciones aplicables pasan.

## Validaciones Automaticas

Ejecutar:

- `python3 -m compileall spritesheet_frame_selector`
- `python3 -m unittest discover -s tests`

Busqueda de contrato legacy:

- no debe aparecer `spritesheet_state.clips`;
- no debe aparecer `spritesheet_state.active_clip_index`;
- no debe aparecer `spritesheet_state.export_settings`.

Tests unitarios recomendados:

- secuencia usa solo frames seleccionados;
- secuencia queda ordenada por `frame_number`;
- frames no seleccionados no se reproducen;
- `fps=12` produce intervalo esperado;
- `fps <= 0` se rechaza;
- `next_playback_index` avanza normal;
- `next_playback_index` respeta loop;
- sin loop termina de forma controlada;
- resumen detecta frames seleccionados sin preview;
- helpers no modifican seleccion ni cache.

## Validaciones Blender Background

Usar `/Applications/Blender.app/Contents/MacOS/Blender` si existe.

Validar:

- importar addon;
- doble ciclo `register()` / `unregister()`;
- crear workspace, clip y frames;
- marcar algunos frames seleccionados y otros no;
- asignar `preview_path` controlado a frames seleccionados;
- ejecutar `bpy.ops.spritesheet.playback_play`;
- confirmar que existe sesion activa;
- confirmar que el frame actual avanza o que el controlador puede avanzar por tick controlado si timers no corren en background;
- ejecutar `pause` y confirmar estado pausado;
- ejecutar `play` de nuevo y confirmar reanudacion o reinicio controlado;
- ejecutar `stop` dos veces y confirmar idempotencia;
- ejecutar `unregister()` durante o despues de playback y confirmar cleanup sin traceback;
- confirmar que seleccion no cambio;
- confirmar que no se crearon previews, cache folders, renders, exports ni ZIPs.

Si el entorno background no permite observar avance de timers, la validacion debe documentarlo y validar:

- creacion de sesion;
- tick manual del controlador si existe;
- pause/stop;
- cleanup en unregister.

## Validaciones Manuales En Blender

1. Instalar o recargar el addon.
2. Crear workspace y clip.
3. Generar previews con Fase 5c.
4. Abrir selector visual.
5. Seleccionar frames alternados.
6. Presionar `Play`.
7. Confirmar que se reproducen solo frames seleccionados.
8. Confirmar que el orden es temporal.
9. Cambiar `fps` del clip y repetir.
10. Confirmar que `Pause` conserva el frame actual.
11. Confirmar que `Stop` vuelve a estado detenido.
12. Cerrar selector durante playback y confirmar que no queda reproduciendo.
13. Cambiar de workspace o clip durante playback y confirmar detencion/invalidez controlada.
14. Desactivar/reactivar addon y confirmar que no quedan timers vivos.

## Riesgos

### Timers De Blender

Riesgo: dejar timers vivos al cerrar dialogo, cambiar clip o desactivar addon.

Mitigacion:

- controlador centralizado;
- sesion unica;
- cleanup en `Stop`;
- cleanup en `unregister()`;
- callbacks que retornan `None` al invalidarse.

### UI Nativa Y Redraw

Riesgo: el dialogo nativo no redibuja con fluidez en todos los contextos.

Mitigacion:

- usar `area.tag_redraw()` de forma defensiva desde el controlador;
- mantener playback correcto aunque el feedback visual sea minimo;
- si el redraw resulta insuficiente en validacion manual, registrar limitacion y proponer subfase tecnica antes de sofisticar UI.

### Preview Paths Faltantes

Riesgo: frames seleccionados sin preview provocan playback incompleto.

Mitigacion:

- resumen previo;
- warning claro;
- no intentar generar preview automaticamente.

### Cambio De Workspace O Clip

Riesgo: reproducir frames del clip anterior despues de cambiar contexto.

Mitigacion:

- sesion usa `workspace_id` y `clip_id`;
- al detectar mismatch, detener o invalidar playback.

## No Alcance Confirmado

Esta fase no debe avanzar a:

- Fase 5f render final;
- composer;
- export individual;
- atlas multi-clip;
- JSON;
- empaquetado distribuible.

## PCS Y Criterio De Termino

Al aprobar y ejecutar esta fase:

- Guardar este plan como aprobado:
  - `Estado: aprobado`;
  - `Autoridad: usuario`;
  - `Modo de ejecucion: ejecutar sin replanificar`.
- Marcar `Estado De Ejecucion: validado` solo si pasan compile, unit tests, Blender background aplicable y limpieza de residuos.
- Actualizar `.context/agent_context.md`, `.context/index.md`, `.context/handoff.md` y `.context/worklog.jsonl`.
- Dejar como siguiente paso preparar el plan de render final workspace-aware, probablemente `docs/plans/reinicio-v2-fase-5f-render-final-workspace-aware.md`.

Criterio final:

- El usuario puede reproducir frames seleccionados del clip activo.
- Playback usa solo previews cacheados existentes.
- FPS del clip afecta playback.
- Play/Pause/Stop funcionan sin traceback.
- Timers se limpian al detener, cerrar, desactivar o recargar.
- Seleccion persistente no cambia durante playback.
- No hay render/export/cache generation en esta fase.

## Resultado De Ejecucion

Estado: validado
Fecha: 2026-07-03

Cambios implementados:

- `spritesheet_frame_selector/playback/sequence.py` con helpers puros de secuencia.
- `spritesheet_frame_selector/playback/controller.py` con controlador runtime y timer unico.
- `spritesheet_frame_selector/operators/playback.py` con operadores `Play`, `Pause` y `Stop`.
- Integracion de controles y estado de playback en selector visual y panel principal.
- Cleanup de playback en `unregister()`.
- `tests/test_playback_sequence.py` con cobertura de helpers puros.

Validaciones ejecutadas:

- `python3 -m compileall spritesheet_frame_selector`: OK.
- `python3 -m unittest discover -s tests`: OK, 36 tests.
- Busqueda de contrato legacy en `spritesheet_frame_selector` y `tests`: OK, sin coincidencias.
- Blender background 5.1.1 fuera del sandbox: OK con `SFS_5E_PLAYBACK_OK`.
- Limpieza de `__pycache__`: OK.

Limitacion pendiente:

- Falta validacion manual GUI de fluidez real del playback dentro del dialogo nativo.

## Supuestos

- El selector visual de Fase 5d se mantiene como superficie principal del feedback de playback.
- Si la UI nativa no permite feedback suficientemente fluido, el controlador runtime sigue siendo valido y se podra mejorar la superficie visual en una subfase posterior.
- Los previews son derivados y descartables; playback no depende de que el cache sea perfecto, pero si de `preview_path` existente para mostrar imagen.
- La validacion manual GUI sigue siendo necesaria para juzgar fluidez real.
