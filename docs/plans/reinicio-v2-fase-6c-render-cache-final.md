# Plan Fase 6c - Eliminar Render Cache Final Incompleto

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: validado

## Referencia Superior

`docs/plans/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md`

## Fuente Principal

- `docs/technical-audit.md`
- `docs/plans/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md`

## Objetivo

Cerrar el estado intermedio del render cache final ejecutando D1, ya confirmado por el usuario: para MVP se elimina el subsistema de cache final en lugar de completarlo.

El resultado esperado es que export siga renderizando a un `TemporaryDirectory` durante cada export, pero sin propiedades persistidas ni ramas de reutilizacion que aparenten una cache inexistente.

## Decisiones Confirmadas

- D1: eliminar render cache final para MVP.
- No completar cache persistente en esta fase.
- B12 desaparece como hallazgo al eliminar `render_dirty` y el estado final render persistido.

## Hallazgos Cubiertos

| ID | Severidad | Titulo | Estado En Este Subplan |
|---|---|---|---|
| A1 | alto | Subsistema de cache de render final es codigo muerto/intermedio | validado por el usuario |
| B1 | bajo | Confusion de parametros en renderer/output index | validado |
| B12 | bajo | `update_workspace_defaults_dirty` no marca `render_dirty` | no aplica; desaparece con D1 |

## Extracto Operativo De Auditoria

### A1 - Cache de render final muerto/intermedio

- Problema: `_ensure_rendered_frames` intenta reutilizar renders previos via `_existing_render_paths_for_clip` y `not clip.render_dirty`. Pero en el addon nadie escribe `frame.render_path` con una ruta real ni pone `render_dirty = False`. La rama de reutilizacion nunca se activa y cada export re-renderiza todos los clips.
- Problema adicional: `build_render_key`, `render_warning`, `count_render_references`, `count_existing_renders`, `clear_render_state` y `render_file_name` en `core/render_state.py` no tienen callers reales del addon, solo tests.
- Problema estructural: los renders se escriben dentro de `tempfile.TemporaryDirectory`, destruido al salir del export; persistir rutas de render seria inutil con el flujo actual.
- Causa: feature a medio implementar. El modelo de datos (`render_key`, `render_folder`, `render_dirty`, `last_render_note`, `frame.render_path`) y helpers existen, pero export nunca cierra el ciclo.
- Impacto: deuda persistida en `.blend`, codigo muerto, rama de export engañosa y confusion para mantenimiento.
- Solucion propuesta por auditoria: decidir explicitamente entre completar o eliminar. D1 eligio eliminar para MVP.
- Archivos/funciones afectados: `spritesheet_frame_selector/operators/export.py::_ensure_rendered_frames/_existing_render_paths_for_clip`, `spritesheet_frame_selector/core/render_state.py`, `spritesheet_frame_selector/properties.py::SpriteSheetClip/SpriteSheetFrameItem`, `spritesheet_frame_selector/core/workspace_state.py::clear_clip_render_state`.

Interpretacion del subplan:

- Eliminar propiedades persistidas de cache final:
  - `SpriteSheetFrameItem.render_path`;
  - `SpriteSheetClip.render_key`;
  - `SpriteSheetClip.render_folder`;
  - `SpriteSheetClip.render_dirty`;
  - `SpriteSheetClip.last_render_note`.
- Eliminar escrituras defensivas o `hasattr` asociadas a esas propiedades.
- Eliminar `_existing_render_paths_for_clip()` y la rama de reutilizacion en `_ensure_rendered_frames`.
- Mantener el render temporal por export como comportamiento explicito MVP.
- Mantener helpers vivos que export/render siguen usando:
  - `selected_frame_numbers`;
  - `render_file_path`;
  - `render_output_file_name`;
  - `_safe_file_prefix` si sigue siendo requerido por `render_file_path`.

### B1 - Confusion de parametro en renderer

- Problema: `render_file_path(output_folder, output_index, ...)` pasa un indice secuencial por el parametro llamado `frame_number`; el dict resultante mapea numeros de frame reales a archivos nombrados por indice. Funciona, pero el nombre del parametro engaña.
- Causa: `render_file_path` comenzo como helper de frame real y ahora tambien sirve para output index secuencial.
- Impacto: lectura confusa del codigo de render/export.
- Solucion propuesta por auditoria: renombrar el parametro o documentar el contrato.
- Archivos/funciones afectados: `spritesheet_frame_selector/render/renderer.py`, `spritesheet_frame_selector/core/render_state.py::render_file_path/render_output_file_name`.

Interpretacion del subplan:

- Renombrar en `core/render_state.py` `frame_number` a `output_index` en:
  - `render_output_file_name(output_index, sheet_name)`;
  - `render_file_path(render_folder, output_index, sheet_name="")`.
- Mantener compatibilidad de comportamiento: el archivo se nombra con indice de salida, no con frame real.
- Ajustar tests para expresar el contrato correcto.

### B12 - Defaults de workspace no marcan `render_dirty`

- Problema: `update_workspace_defaults_dirty` no marca `render_dirty`, mientras operadores analogos de colecciones default si lo hacen. Es inconsistente si existiera cache final.
- Causa: estado `render_dirty` incompleto.
- Impacto: irrelevante una vez D1 elimina cache final.
- Solucion de este subplan: eliminar `render_dirty`; B12 queda no aplicable/desaparece.

## Alcance De Implementacion

Incluir:

- Reducir `core/render_state.py` a helpers vivos:
  - `selected_frame_numbers`;
  - `render_output_file_name`;
  - `render_file_path`;
  - `_safe_file_prefix`.
- Eliminar de `core/render_state.py`:
  - `RENDER_CACHE_VERSION`;
  - `build_render_key`;
  - `render_file_name`;
  - `count_render_references`;
  - `count_existing_renders`;
  - `clear_render_state`;
  - `render_warning`;
  - `_id_key`, salvo que otro modulo lo use.
- Eliminar `_existing_render_paths_for_clip()` y su llamada en `operators/export.py`.
- Quitar `clip.last_render_note = ...` del export si desaparece la propiedad.
- Quitar propiedades de render cache final en `properties.py`.
- Quitar preservacion/limpieza de `render_path` y `clear_clip_render_state` en `core/frame_sync.py` y `core/workspace_state.py`.
- Ajustar operadores/selection/workspaces/visual_selector para no escribir `render_dirty`.
- Reescribir tests que hoy solo cubren render cache muerto:
  - mantener tests de `selected_frame_numbers`;
  - mantener/ajustar tests de naming con `output_index`;
  - eliminar tests de `build_render_key`, `render_warning`, `clear_render_state`, conteos de render refs.

Excluir:

- Cambiar comportamiento de render final o export.
- Implementar cache persistente.
- Resolver A2/A3/A5/B2/B9/B11; pertenecen a 6b/6d.
- Eliminar `original_index`; pertenece a 6e.
- Unificar sanitizadores; pertenece a 6e, salvo ajuste minimo necesario por helpers vivos.

## Archivos Esperados

- `spritesheet_frame_selector/core/render_state.py`
- `spritesheet_frame_selector/operators/export.py`
- `spritesheet_frame_selector/properties.py`
- `spritesheet_frame_selector/core/frame_sync.py`
- `spritesheet_frame_selector/core/workspace_state.py`
- `spritesheet_frame_selector/core/selection.py`
- `spritesheet_frame_selector/operators/workspaces.py`
- `spritesheet_frame_selector/operators/visual_selector.py`
- `tests/test_render_state.py`
- Otros tests que importen o afirmen `render_dirty`/`render_path`

## Validacion Automatica

- `python3 -m compileall spritesheet_frame_selector`
- `python3 -m unittest discover -s tests`
- Busquedas de contrato:
  - `rg -n "render_key|render_folder|render_dirty|last_render_note|render_path|build_render_key|render_warning|count_render|clear_render_state|_existing_render_paths_for_clip" spritesheet_frame_selector tests`
  - Resultado esperado: sin apariciones, salvo que el texto aparezca solo en docs/planes no ejecutables.
  - `rg -n "render_file_path\\(|render_output_file_name\\(" spritesheet_frame_selector tests`
  - Resultado esperado: llamadas vigentes expresan `output_index` o quedan cubiertas por tests.

## Validacion Blender GUI

- Exportar spritesheet con uno o mas clips incluidos.
- Confirmar que PNG y JSON siguen generandose.
- Confirmar que `Export Individual Frames`, si esta activo, sigue generando frames individuales numerados por indice de salida.
- Ejecutar export dos veces y aceptar que re-renderiza en MVP; no debe intentar reutilizar rutas persistidas ni depender de estado `render_dirty`.
- Reabrir un `.blend` guardado con propiedades viejas si existe uno de prueba: Blender debe tolerar ausencia de propiedades nuevas; si hay propiedades custom antiguas sin uso, no deben afectar export.

## Criterios De Aceptacion

- El codigo activo no contiene subsistema de cache final incompleto.
- Export sigue funcionando con render temporal por ejecucion.
- `render_file_path`/`render_output_file_name` expresan claramente `output_index`.
- A1 queda corregido por eliminacion.
- B1 queda corregido por renombre/documentacion de parametro.
- B12 queda no aplicable al eliminar `render_dirty`.

## Riesgos

- Borrar demasiado de `core/render_state.py` puede romper `selected_frame_numbers` o naming usado por export/render. Por eso el primer paso debe distinguir helpers vivos de helpers muertos.
- `.blend` antiguos pueden conservar propiedades ID antiguas internamente, pero al no estar registradas en el addon no deben participar en logica. Si se detecta problema real de migracion, registrar una tarea separada.
- Tests antiguos pueden estar validando codigo muerto; deben reescribirse, no conservarse artificialmente.

## Proximo Paso Si Se Aprueba

Implementar este subplan sin tocar 6b/6d/6e. Al finalizar dejar `Estado De Ejecucion: implementado`, actualizar el ledger de Fase 6 y pedir validacion Blender GUI antes de marcarlo `validado`.

## Resumen De Implementacion

- `core/render_state.py` quedo reducido a helpers vivos:
  - `selected_frame_numbers`;
  - `render_output_file_name(output_index, sheet_name)`;
  - `render_file_path(render_folder, output_index, sheet_name)`;
  - `_safe_file_prefix`.
- Se eliminaron helpers muertos de cache final: `RENDER_CACHE_VERSION`, `build_render_key`, `render_file_name`, conteos de render refs, `clear_render_state`, `render_warning` e `_id_key`.
- `operators/export.py` ya no intenta reutilizar renders con `_existing_render_paths_for_clip` ni depende de `clip.render_dirty`; cada export renderiza temporalmente de forma explicita.
- Se eliminaron propiedades persistidas de cache final:
  - `SpriteSheetFrameItem.render_path`;
  - `SpriteSheetClip.render_key`;
  - `SpriteSheetClip.render_folder`;
  - `SpriteSheetClip.render_dirty`;
  - `SpriteSheetClip.last_render_note`.
- Se retiraron preservaciones/limpiezas de `render_path` y `clear_clip_render_state`.
- Se retiraron escrituras defensivas de `render_dirty` en seleccion, workspace defaults y toggle de frame.
- `tests/test_render_state.py` ahora cubre solo contrato vivo: seleccion persistente y naming por `output_index`.
- `tests/test_selection.py` ya no espera `render_dirty`.

## Validaciones Ejecutadas

- Pasado: `python3 -m compileall spritesheet_frame_selector`.
- Pasado: `python3 -m unittest discover -s tests` con 75 tests.
- Pasado: busqueda de contrato del subsistema eliminado; no quedan propiedades/rama/helpers de cache final en codigo activo ni tests. Las apariciones restantes son los helpers vivos `render_file_path` y `render_output_file_name`.
- Pasado: busqueda de helpers vivos `render_file_path(`/`render_output_file_name(` en codigo y tests.

## Resultado De Validacion Blender GUI

Validado por el usuario:

- Export de spritesheet genera PNG/JSON correctamente.
- `Export Individual Frames` genera los frames individuales correctamente.
- Repetir export funciona bien y se acepta el re-render MVP sin cache final persistida.

La duda operativa sobre "repetir export aceptando re-render sin cache final" quedo aclarada: no exige observar internamente la ausencia de cache; basta confirmar que una segunda exportacion sigue funcionando correctamente aunque el MVP renderice de nuevo.

## Validacion Blender GUI Ejecutada

- Exportar spritesheet con uno o mas clips incluidos.
- Confirmar que PNG y JSON siguen generandose.
- Confirmar que `Export Individual Frames`, si esta activo, sigue generando frames individuales numerados por indice de salida.
- Ejecutar export dos veces y aceptar que re-renderiza en MVP; no debe intentar reutilizar rutas persistidas ni depender de estado `render_dirty`.
