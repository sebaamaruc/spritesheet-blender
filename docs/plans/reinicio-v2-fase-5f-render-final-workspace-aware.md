# Plan Fase 5f - Render Final Workspace-Aware

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: implementado

## Referencia Superior

`docs/plans/reinicio-v2-master-plan.md`

## Plan Rector

`docs/plans/reinicio-v2-fase-5-workspace-root-vertical-slices.md`

## Fases Previas Requeridas

- `docs/plans/reinicio-v2-fase-5a-workspace-data-model-persistencia.md`: validado.
- `docs/plans/reinicio-v2-fase-5b-workspace-clip-management.md`: validado.
- `docs/plans/reinicio-v2-fase-5c-workspace-preview-cache.md`: validado.
- `docs/plans/reinicio-v2-fase-5d-visual-selector-minimo.md`: validado.
- `docs/plans/reinicio-v2-fase-5e-playback-preview.md`: validado.
- `docs/plans/reinicio-v2-fase-5e1-selector-playback-ux.md`: validado.

## Documentacion Fuente Usada

- `docs/specs/mvp_v2.md`
- `docs/architecture/addon_architecture.md`
- `docs/specs/validation_plan.md`
- `docs/specs/workspace_root_decisions.md`
- `docs/design/visual_selector_strategy.md`

## Interpretacion Operativa

Esta fase no implementa export spritesheet completo. Su objetivo es crear el backend de render final workspace-aware que produce frames renderizados confiables para el clip activo, usando la misma resolucion de contexto que preview:

```text
Scene.spritesheet_state -> workspace activo -> clip activo
```

El resultado de esta fase debe ser una secuencia de imagenes finales renderizadas por frame seleccionado, guardadas como artefactos derivados en una carpeta administrada. La composicion en spritesheet, atlas multi-clip, metadata JSON y export final pertenecen a la fase siguiente.

## Objetivo

Implementar render final por clip activo, respetando:

- camara efectiva: override del clip si existe; si no, default del workspace;
- collections efectivas: override del clip si existe; si no, default collections del workspace;
- seleccion persistente de frames del clip;
- settings de export del workspace activo para dimensiones, transparencia y base de salida;
- restauracion completa del estado temporal de Blender despues de renderizar.

## Alcance

Incluir:

- Backend de render final en `spritesheet_frame_selector/render/`.
- Operadores en `spritesheet_frame_selector/operators/render.py`:
  - `SPRITESHEET_OT_render_final_frames`
- Helpers de validacion de render en `spritesheet_frame_selector/core/validation.py` o modulo equivalente.
- Escritura directa de PNG finales en `workspace.export_settings.output_folder`.
- Estado persistente minimo para referenciar render final si es necesario:
  - preferido: `SpriteSheetFrameItem.render_path`;
  - alternativa aceptable: estado derivado por clip con `render_folder`, `render_key`, `render_dirty`, `last_render_note`.
- UI compacta en panel para:
  - ejecutar render final del clip activo;
  - limpiar render final derivado;
  - mostrar estado breve de frames renderizados.
- Tests unitarios para validacion pura y path/key de render cuando sea posible.
- Validacion Blender background del render final si el entorno lo permite.

Excluir:

- Composicion de spritesheet.
- Export PNG final de spritesheet.
- Atlas multi-clip.
- JSON metadata.
- ZIP distribuible.
- Render de todos los clips incluidos del workspace.
- UI avanzada de cola de render.
- Render incremental inteligente basado en cambios complejos de escena.
- Edicion de materiales, world, compositor o engines no documentados.

## Reglas De Implementacion

- No usar `scene.camera` como fallback silencioso cuando hay workspace activo.
- Si falta camara efectiva, cancelar con warning claro.
- Si faltan collections efectivas, cancelar con warning claro.
- Si hay collections borradas con nombre historico, cancelar con warning claro.
- Renderizar solo frames seleccionados del clip activo.
- Si no hay frames seleccionados, cancelar sin crear archivos.
- Si el rango de frames es invalido o no sincronizado, reportar error controlado.
- No modificar seleccion persistente del clip.
- No generar previews ni tocar preview cache.
- No componer spritesheet.
- No escribir archivos desde `draw()`.
- Crear carpetas solo dentro del operador de render final.
- Guardar outputs finales en la carpeta destino elegida en `Export Settings > Folder`.
- Si falta carpeta destino, cancelar con warning claro.
- Restaurar siempre con `try/finally`:
  - frame actual;
  - camara de escena;
  - resolucion;
  - filepath de render;
  - transparencia;
  - engine/settings tocados si se modifican;
  - visibilidad de collections/layer collections.
- Reutilizar el modulo de visibilidad ya validado en preview workspace-aware.
- El render final debe producir imagenes a `workspace.export_settings.frame_width` x `frame_height`.
- `transparent` debe respetar `workspace.export_settings.transparent`.
- El nombre de archivo por frame debe ser estable y no depender solo del nombre visible del clip.
- Las rutas de frames renderizados se actualizan al ejecutar `Render Final Frames`.

## Diseno Tecnico Propuesto

### Modulos

Crear o actualizar:

- `spritesheet_frame_selector/core/render_state.py`
  - `build_render_key(workspace, clip, camera, collections, export_settings)`
  - `count_rendered_frames(clip)`
  - helpers puros para nombre de archivo por frame.
- `spritesheet_frame_selector/core/validation.py`
  - `validate_active_clip_render_context(workspace, clip)`
  - validacion de selected frames, camera, collections, settings.
- `spritesheet_frame_selector/core/paths.py`
  - helpers para carpeta de render final administrada.
- `spritesheet_frame_selector/render/renderer.py`
  - `render_clip_frames(context, workspace, clip, camera, collections, output_folder, frame_numbers, settings)`
  - aplica/restaura contexto Blender.
- `spritesheet_frame_selector/operators/render.py`
  - operadores Blender.
- `spritesheet_frame_selector/ui/panels.py`
  - seccion compacta `Final Render`.
- `spritesheet_frame_selector/registration.py`
  - registro de operadores nuevos.

### Modelo Persistente Minimo

Agregar a `SpriteSheetFrameItem`:

- `render_path: StringProperty(default="")`

Motivo:

- Cada frame ya contiene seleccion y `preview_path`.
- La fase siguiente de composer/export necesita una lista ordenada de imagenes finales sin recalcular estado global.
- Mantener `render_path` por frame separa preview de render final y evita reutilizar cache de thumbnails.

Agregar a `SpriteSheetClip` solo si hace falta para UX/validacion:

- `render_key: StringProperty(default="")`
- `render_folder: StringProperty(default="")` como ultima carpeta destino usada.
- `render_dirty: BoolProperty(default=True)`
- `last_render_note: StringProperty(default="")`

Si se agregan estos campos, deben tratarse como referencias derivadas a renders finales regenerables.

## Flujo De Usuario En Esta Fase

1. Usuario selecciona workspace activo.
2. Usuario selecciona clip activo.
3. Usuario genera previews y selecciona frames, o ya tiene seleccion persistente.
4. Usuario revisa/ajusta export settings basicos del workspace:
   - frame width;
   - frame height;
   - transparencia.
5. Usuario ejecuta `Render Final Frames`.
6. Addon renderiza frames seleccionados del clip activo.
7. Panel muestra conteo de frames finales renderizados.
8. Usuario revisa los PNG generados en la carpeta destino.

## UI Propuesta

Agregar seccion compacta:

```text
Final Render
  Render Final Frames
  Rendered: N / Selected: M
  Last note / warning breve
```

Reglas:

- No mostrar rutas largas en panel principal.
- No duplicar informacion de `Preview Status`.
- No agregar boton `Export Spritesheet` todavia.
- Si se requiere exponer rutas, dejarlo para panel debug futuro o tooltip.

## Validaciones Automaticas

Ejecutar:

- `python3 -m compileall spritesheet_frame_selector`
- `python3 -m unittest discover -s tests`
- Busqueda legacy:
  - no `spritesheet_state.clips`;
  - no `spritesheet_state.active_clip_index`;
  - no uso de `scene.camera` como fallback silencioso;
  - no referencias a codigo V1.

Tests unitarios sugeridos:

- `build_render_key` cambia con:
  - workspace id;
  - clip id;
  - frame range/step;
  - selected frame list si se incluye en key;
  - frame width/height;
  - transparencia;
  - camara efectiva;
  - collections efectivas.
- `build_render_key` no depende de `workspace.name` ni `clip.name`.
- Validacion falla si no hay camara efectiva.
- Validacion falla si no hay collections efectivas.
- Validacion falla si no hay frames seleccionados.
- Clear logico de render conserva seleccion y previews.

## Validaciones Blender Background

Si Blender background funciona:

1. Importar addon.
2. Ejecutar doble ciclo `register()` / `unregister()`.
3. Crear escena minima con camera, cube/light y collection.
4. Crear workspace con default camera y default collection.
5. Crear clip con rango corto, por ejemplo frames `1-3`.
6. Sincronizar frames y seleccionar algunos.
7. Ejecutar `bpy.ops.spritesheet.render_final_frames()`.
8. Confirmar:
   - existen archivos renderizados para frames seleccionados;
   - no existen archivos para frames no seleccionados;
   - `render_path` se poblo solo donde corresponde;
   - `render_dirty=False` si se implementa ese campo;
   - `last_render_note` indica conteo correcto.
9. Confirmar que frame actual, camera, resolucion, filepath, transparencia y visibilidad se restauran.
10. Confirmar que no se registra ni muestra operador de clear cache para render final.
11. Guardar/reabrir `.blend` temporal fuera del repo y confirmar persistencia de referencias de render si se decide persistirlas.

Si Blender background sigue fallando en el entorno local:

- documentar el fallo;
- mantener compile/unit tests como validacion automatica;
- dejar validacion manual GUI obligatoria antes de cerrar la fase.

## Validacion Manual GUI

En Blender GUI:

1. Activar addon.
2. Crear workspace con camera y collection default.
3. Crear clip y generar previews.
4. Seleccionar subconjunto de frames.
5. Ejecutar `Render Final Frames`.
6. Confirmar que la escena visible/renderizada respeta solo las collections efectivas.
7. Confirmar que se usa la camara efectiva correcta.
8. Confirmar que los outputs tienen la resolucion configurada en `Export Settings`.
9. Confirmar transparencia si `transparent=True`.
10. Cambiar de clip/workspace y confirmar que los nombres de output no se mezclan si `sheet_name` es distinto.
11. Desactivar/reactivar addon sin errores.

## Riesgos

### Mutacion De Escena

Riesgo:

- Render final puede dejar frame, camera, filepath, resolucion o visibilidad modificados.

Mitigacion:

- Un solo contexto `try/finally` para guardar/restaurar estado.
- Tests Blender background o manuales que comparen estado antes/despues.

### Diferencias De Engine Blender 5.x

Riesgo:

- Engines o settings pueden cambiar entre Workbench/EEVEE Next.

Mitigacion:

- Usar render nativo sin hacks de world/material.
- Tocar el minimo de settings.
- No reintroducir `WorldSwapContext`.

### Archivos Derivados

Riesgo:

- Renders finales pueden quedar dentro del repo o mezclarse entre clips.

Mitigacion:

- Paths centralizados administrados.
- Carpeta por workspace id, clip id y render key.
- `.gitignore` ya debe cubrir outputs derivados.

### Alcance

Riesgo:

- Convertir 5f en export/composer completo.

Mitigacion:

- 5f solo genera frames renderizados.
- 5g se encargara de composer/export spritesheet/atlas/metadata.

## PCS Y Criterio De Termino

Al aprobar y ejecutar esta fase:

- Cambiar este plan a:
  - `Estado: aprobado`;
  - `Autoridad: usuario`;
  - `Modo de ejecucion: ejecutar sin replanificar`.
- Marcar `Estado De Ejecucion: validado` solo si pasan:
  - compile;
  - unit tests;
  - validacion Blender background aplicable o justificacion documentada;
  - validacion manual GUI minima si background no cubre render real;
  - limpieza de residuos.
- Actualizar `.context/agent_context.md`, `.context/index.md`, `.context/handoff.md` y `.context/worklog.jsonl`.
- Dejar como siguiente paso preparar `docs/plans/reinicio-v2-fase-5g-composer-export-spritesheet.md`.

Criterio final:

- El clip activo puede renderizar frames finales seleccionados.
- El render usa camera y collections efectivas.
- El render respeta settings basicos del workspace.
- La escena queda restaurada despues del render.
- Los archivos derivados viven en carpeta administrada.
- No hay composer/export spritesheet/atlas/metadata implementados en esta fase.

## Supuestos

- 5e1 esta validada y los ajustes menores de UI no bloquean render final.
- `include_in_export` existe pero 5f renderiza el clip activo; el filtrado de multiples clips incluidos queda para 5g.
- La fase 5g consumira los frames renderizados por 5f para componer spritesheet/export.
- El backend inicial puede usar `bpy.ops.render.render(write_still=True)` siempre que restaure estado correctamente.

## Resultado De Ejecucion

Estado: implementado, pendiente de validacion Blender/manual.

Cambios implementados:

- Modelo persistente extendido con `SpriteSheetFrameItem.render_path` y estado derivado de render por clip.
- Helpers puros de render final en `spritesheet_frame_selector/core/render_state.py`.
- Validacion de contexto render workspace-aware en `spritesheet_frame_selector/core/validation.py`.
- Escritura directa de renders finales en `workspace.export_settings.output_folder`.
- Backend de render final en `spritesheet_frame_selector/render/renderer.py`.
- Operador `SPRITESHEET_OT_render_final_frames`.
- Registro centralizado actualizado.
- Seccion compacta `Final Render` en el panel principal.
- Cambios de seleccion invalidan el render final derivado con `render_dirty=True`.
- Tests unitarios nuevos en `tests/test_render_state.py`.

Validaciones ejecutadas:

- `python3 -m compileall spritesheet_frame_selector`: pasa.
- `python3 -m unittest discover -s tests`: pasa, 45 tests.
- Busqueda legacy `spritesheet_state.clips`, `spritesheet_state.active_clip_index`, `WorldSwapContext` y uso de `scene.camera`: sin contratos legacy; `scene.camera` solo aparece en guardado/restauracion/asignacion explicita.

Validaciones pendientes:

- Blender background/GUI para confirmar render real, restauracion de escena y outputs en carpeta destino.
- No se marco esta fase como validada porque el entorno bloqueo la preparacion del script temporal de validacion Blender.

## Correcciones Posteriores De UI Y Contrato

Estado: implementado, pendiente de validacion Blender/manual.

Correcciones aplicadas:

- `Final Render` fue movido debajo de `Export Settings`.
- `Export Settings` ahora muestra `output_folder` y agrega boton con file browser para elegir carpeta destino.
- La lista de clips ya no muestra rango `start-end`; muestra cantidad de frames seleccionados.
- Al crear un clip se sincronizan sus frames iniciales desde el rango por defecto, todos seleccionados.
- `Default Collections` se degrado en UI a `Default Collection`: solo se puede agregar un slot por workspace.
- Preview/render ahora reportan error si un workspace legado contiene mas de un default collection sin override de clip.

Nota operativa:

- `Render Final Frames` ahora escribe PNGs directamente en `workspace.export_settings.output_folder`. No existe clear cache para render final.

Validaciones ejecutadas despues de estas correcciones:

- `python3 -m compileall spritesheet_frame_selector`: pasa.
- `python3 -m unittest discover -s tests`: pasa, 47 tests.
- Busqueda legacy `spritesheet_state.clips`, `spritesheet_state.active_clip_index`, `WorldSwapContext`: sin coincidencias.

## Correccion De Contrato Para Export JSON

Estado: implementado, pendiente de validacion Blender/manual.

Decision aplicada:

- No se permiten nombres duplicados de clips dentro de un mismo workspace.
- Si el usuario escribe un nombre ya usado, el addon agrega sufijo numerico incremental (`Run`, `Run 2`, `Run 3`, etc.).
- Esta regla permite que el JSON multi-clip use nombres visibles de clip como keys sin sobrescritura silenciosa.

Validaciones ejecutadas:

- `python3 -m compileall spritesheet_frame_selector`: pasa.
- `python3 -m unittest discover -s tests`: pasa, 48 tests.

## Correccion De Naming De Frames Renderizados

Estado: implementado, pendiente de validacion Blender/manual.

Decision aplicada:

- Los PNG renderizados usan indice de salida continuo segun el orden de seleccion.
- El numero en el nombre de archivo no conserva el frame original de Blender.
- Ejemplo: si se renderizan frames originales `3`, `5` y `6`, los archivos son `*_frame_000001.png`, `*_frame_000002.png`, `*_frame_000003.png`.
- `frame.render_path` sigue enlazando cada frame original con su archivo de salida correspondiente.

Validaciones ejecutadas:

- `python3 -m compileall spritesheet_frame_selector`: pasa.
- `python3 -m unittest discover -s tests`: pasa, 48 tests.
