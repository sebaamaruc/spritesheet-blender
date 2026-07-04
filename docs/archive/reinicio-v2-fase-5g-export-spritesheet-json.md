# Plan Fase 5g - Export Spritesheet Y JSON

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: validado

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
- `docs/plans/reinicio-v2-fase-5f-render-final-workspace-aware.md`: implementado; requiere validacion manual final antes de cerrar 5g.

## Documentacion Fuente Usada

- `docs/specs/mvp_v2.md`
- `docs/specs/product_requirements.md`
- `docs/architecture/addon_architecture.md`
- `docs/specs/validation_plan.md`
- `docs/specs/workspace_root_decisions.md`
- Ejemplo externo compartido por el usuario: `shading_back_player_soccer.json`.

## Interpretacion Operativa

Esta fase implementa el flujo principal de export del MVP:

```text
workspace activo -> clips incluidos -> frames seleccionados -> renders finales -> spritesheet PNG -> JSON
```

El usuario compartio un ejemplo de metadata donde un solo spritesheet contiene varios clips:

```json
{
  "sheet": "shading_back_player_soccer",
  "frameWidth": 128,
  "frameHeight": 128,
  "columns": 16,
  "clips": {
    "shoot": { "start": 0, "end": 32, "count": 33, "fps": 12 },
    "run": { "start": 33, "end": 45, "count": 13, "fps": 18 },
    "idle": { "start": 46, "end": 134, "count": 89, "fps": 12 }
  }
}
```

Por esta razon, 5g debe cubrir PNG final + JSON para uno o varios clips incluidos del workspace activo. La fase 5h queda reservada para mejoras avanzadas de atlas si aparecen despues, no para el contrato basico de JSON.

## Objetivo

Implementar `Export Spritesheet` para generar:

- un PNG final de spritesheet;
- un JSON con el mismo nombre base;
- frames ordenados por clips incluidos del workspace activo;
- metadata compatible con el formato de ejemplo;
- render final previo opcional como paso interno si faltan PNGs finales.

## Alcance

Incluir:

- Backend composer reemplazable en `spritesheet_frame_selector/export/` o modulo equivalente.
- Operador principal:
  - `SPRITESHEET_OT_export_spritesheet`
- Helpers puros para:
  - calcular layout de spritesheet;
  - calcular indice `start/end/count` por clip;
  - construir JSON de metadata;
  - validar nombres, carpeta destino, dimensiones y frames disponibles.
- UI en panel:
  - boton `Export Spritesheet`;
  - estado breve del ultimo export;
  - warning si faltan renders, carpeta, camera o collections.
- Escritura de archivos:
  - `<sheet_name>.png`
  - `<sheet_name>.json`
- Export PNG final con alpha.
- Soporte multi-clip usando clips con `include_in_export=True` dentro del workspace activo.
- Reutilizacion del render final 5f cuando existan `render_path` validos.
- Render final automatico previo cuando falten renders finales para frames seleccionados.
- Tests unitarios para layout y JSON.

Excluir:

- ZIP distribuible.
- Metadata compleja de runtime.
- Rects por frame en JSON.
- Offsets, pivots, trimming o rotacion.
- Atlas packing avanzado.
- Reorden manual de clips fuera del orden actual de la lista del workspace.
- Export incremental inteligente.
- Render de todos los workspaces.

## Contrato De JSON

El JSON debe usar exactamente esta forma base:

```json
{
  "sheet": "sheet_name",
  "frameWidth": 128,
  "frameHeight": 128,
  "columns": 16,
  "clips": {
    "clip_name": {
      "start": 0,
      "end": 10,
      "count": 11,
      "fps": 12
    }
  }
}
```

Reglas:

- El archivo JSON debe llamarse igual que el PNG, cambiando extension.
- `sheet` no incluye extension.
- `frameWidth` viene de `workspace.export_settings.frame_width`.
- `frameHeight` viene de `workspace.export_settings.frame_height`.
- `columns` viene de `workspace.export_settings.columns`.
- `clips` es un objeto cuyas keys son nombres visibles de clips.
- Los nombres de clips no deben duplicarse dentro del workspace; la regla ya fue incorporada en 5f.
- `start` es el indice global del primer frame del clip dentro del spritesheet final.
- `end` es inclusivo.
- `count` es la cantidad de frames seleccionados/exportados del clip.
- `fps` viene de `clip.fps`.
- Los indices empiezan en `0`, no en `1`.
- No incluir frames originales de Blender en el JSON MVP.
- No incluir rutas absolutas en el JSON MVP.

## Contrato De PNG

El PNG final:

- usa `sheet_name` como nombre base;
- vive en `workspace.export_settings.output_folder`;
- usa `frame_width` x `frame_height` por celda;
- usa `columns` para distribuir frames;
- calcula rows automaticamente:

```text
rows = ceil(total_frames / columns)
```

- ancho final:

```text
columns * frame_width + padding/margin segun contrato aprobado
```

- alto final:

```text
rows * frame_height + padding/margin segun contrato aprobado
```

Para esta fase, `padding` y `margin` deben respetarse si ya estan en `SpriteSheetExportSettings`. Si su semantica no esta implementada todavia, la fase debe definirla antes de escribir el composer.

## Semantica De Padding Y Margin

Definicion propuesta para 5g:

- `margin`: espacio transparente exterior alrededor de todo el spritesheet.
- `padding`: espacio transparente entre celdas.
- Celda base: `frame_width` x `frame_height`.
- Posicion X:

```text
x = margin + column_index * (frame_width + padding)
```

- Posicion Y:

```text
y = margin + row_index * (frame_height + padding)
```

- Ancho final:

```text
margin * 2 + columns * frame_width + max(columns - 1, 0) * padding
```

- Alto final:

```text
margin * 2 + rows * frame_height + max(rows - 1, 0) * padding
```

El JSON no incluye padding ni margin en esta fase para mantener compatibilidad con el ejemplo.

## Flujo De Usuario

1. Usuario selecciona workspace activo.
2. Usuario configura `Export Settings`:
   - `frame_width`;
   - `frame_height`;
   - `columns`;
   - `padding`;
   - `margin`;
   - `transparent`;
   - `output_folder`;
   - `sheet_name`.
3. Usuario marca clips con `Include in Export`.
4. Usuario selecciona frames en cada clip.
5. Usuario presiona `Export Spritesheet`.
6. Addon valida contexto.
7. Addon renderiza frames finales faltantes o reutiliza `render_path` vigente.
8. Addon compone `<sheet_name>.png`.
9. Addon escribe `<sheet_name>.json`.
10. Panel muestra resultado breve.

## Reglas De Implementacion

- No escribir archivos desde `draw()`.
- Crear carpetas solo dentro del operador de export.
- Cancelar con warning claro si falta `output_folder`.
- Cancelar con warning claro si falta `sheet_name`.
- Cancelar con warning claro si no hay clips incluidos.
- Cancelar con warning claro si un clip incluido no tiene frames seleccionados.
- Cancelar con warning claro si falta camera efectiva para un clip que debe renderizarse.
- Cancelar con warning claro si faltan collections efectivas.
- No usar `scene.camera` como fallback silencioso.
- No modificar seleccion persistente.
- No modificar preview cache.
- Reutilizar visibilidad reversible de 5c/5f para renders faltantes.
- Restaurar siempre estado temporal de Blender si se renderiza.
- Si falla render de un frame, no escribir PNG/JSON final incompleto.
- Escribir JSON despues de que PNG final se haya creado correctamente.
- Sobrescribir `<sheet_name>.png` y `<sheet_name>.json` solo como resultado explicito del operador `Export Spritesheet`.
- Evitar rutas absolutas dentro del JSON.
- Orden de frames:
  - clips en orden de lista del workspace;
  - frames seleccionados en orden temporal por `frame_number`.
- Nombres de PNGs intermedios de 5f pueden existir, pero el producto principal es el spritesheet final.

## Diseno Tecnico Propuesto

Crear o actualizar:

- `spritesheet_frame_selector/export/layout.py`
  - `sheet_dimensions(total_frames, frame_width, frame_height, columns, padding, margin)`
  - `frame_rect(index, frame_width, frame_height, columns, padding, margin)`
  - `clip_ranges(exported_clips)`
- `spritesheet_frame_selector/export/metadata.py`
  - `build_spritesheet_metadata(sheet_name, frame_width, frame_height, columns, clip_ranges)`
- `spritesheet_frame_selector/export/composer.py`
  - carga PNGs finales;
  - crea imagen transparente;
  - pega cada frame en su rect;
  - guarda PNG final.
- `spritesheet_frame_selector/operators/export.py`
  - `SPRITESHEET_OT_export_spritesheet`
- `spritesheet_frame_selector/ui/panels.py`
  - boton `Export Spritesheet`;
  - estado del ultimo export.
- `spritesheet_frame_selector/registration.py`
  - registrar operador nuevo.

Backend recomendado:

- Usar Pillow si esta disponible en el runtime Blender.
- Si Pillow no esta disponible, usar API nativa de Blender `bpy.data.images` solo si permite componer sin introducir fragilidad excesiva.
- El plan de implementacion debe validar disponibilidad real antes de decidir backend final.

## Cambios De Modelo Persistente

Preferencia: evitar cambios grandes de modelo.

Agregar solo si hace falta:

- `SpriteSheetWorkspace.last_export_note: StringProperty(default="")`
- `SpriteSheetWorkspace.last_export_png: StringProperty(subtype="FILE_PATH", default="")`
- `SpriteSheetWorkspace.last_export_json: StringProperty(subtype="FILE_PATH", default="")`

No agregar metadata compleja por frame.

## Validaciones Automaticas

Ejecutar:

- `python3 -m compileall spritesheet_frame_selector`
- `python3 -m unittest discover -s tests`
- Busqueda legacy:
  - no `spritesheet_state.clips`;
  - no `spritesheet_state.active_clip_index`;
  - no `spritesheet_state.export_settings`;
  - no `WorldSwapContext`.

Tests unitarios minimos:

- `sheet_dimensions` calcula rows/ancho/alto sin padding/margin.
- `sheet_dimensions` calcula rows/ancho/alto con padding/margin.
- `frame_rect` ubica indices en filas/columnas correctas.
- `clip_ranges` produce `start/end/count` inclusivo.
- `build_spritesheet_metadata` produce JSON equivalente al formato de ejemplo.
- JSON no incluye rutas absolutas.
- Clips sin frames seleccionados fallan validacion.
- Nombres duplicados no aparecen en metadata porque ya se normalizan en workspace.

## Validaciones Blender Background

Si Blender background funciona:

1. Importar addon.
2. Ejecutar doble ciclo `register()` / `unregister()`.
3. Crear escena con camera, cube/light y collection.
4. Crear workspace con default camera y default collection.
5. Crear dos clips incluidos con nombres unicos, fps distintos y rangos cortos.
6. Seleccionar subconjuntos de frames.
7. Configurar export settings:
   - `frame_width=32`;
   - `frame_height=32`;
   - `columns=4`;
   - `sheet_name="test_sheet"`;
   - `output_folder` temporal fuera del repo.
8. Ejecutar `bpy.ops.spritesheet.export_spritesheet()`.
9. Confirmar que existen:
   - `test_sheet.png`;
   - `test_sheet.json`.
10. Confirmar que JSON contiene:
   - `sheet: "test_sheet"`;
   - `frameWidth: 32`;
   - `frameHeight: 32`;
   - `columns: 4`;
   - clips con `start/end/count/fps` correctos.
11. Confirmar que PNG tiene dimensiones esperadas.
12. Confirmar que no se crean outputs dentro del repo salvo que el usuario elija explicitamente esa carpeta.
13. Limpiar temporales generados por la prueba.

Si Blender background sigue fallando:

- documentar el fallo;
- mantener compile/unit tests como validacion automatica;
- dejar validacion manual GUI obligatoria.

## Validacion Manual GUI

En Blender GUI:

1. Crear workspace con camera y default collection.
2. Crear tres clips con nombres distintos.
3. Seleccionar distintos subconjuntos de frames.
4. Marcar los clips como `Include in Export`.
5. Elegir `Export Settings > Folder`.
6. Configurar `Sheet`, dimensiones y columnas.
7. Ejecutar `Export Spritesheet`.
8. Confirmar que PNG y JSON aparecen en la carpeta.
9. Confirmar que JSON se llama igual que PNG.
10. Confirmar que `start/end/count/fps` coinciden con el orden visual del spritesheet.
11. Confirmar que nombres duplicados se normalizan antes del export.
12. Confirmar que excluir un clip lo elimina del PNG y JSON.
13. Desactivar/reactivar addon sin errores.

## Riesgos

### Backend De Composicion

Riesgo:

- Pillow puede no estar disponible en el Python interno de Blender.

Mitigacion:

- Validar disponibilidad antes de implementar.
- Mantener composer detras de modulo reemplazable.
- Si se usa Blender API, aislarla en `export/composer.py`.

### Scope Creep

Riesgo:

- Convertir 5g en packer avanzado.

Mitigacion:

- Sin rects por frame.
- Sin trimming.
- Sin pivots.
- Sin packing variable.
- Grid uniforme por `columns`.

### JSON Keys Por Nombre Visible

Riesgo:

- Sobrescritura si hay nombres duplicados.

Mitigacion:

- Regla ya aplicada: nombres de clips son unicos dentro del workspace.
- Validacion de export debe rechazar cualquier duplicado legado si aparece.

### Renders Intermedios

Riesgo:

- Usar renders stale para componer.

Mitigacion:

- Validar `render_dirty` y existencia de `render_path`.
- Renderizar automaticamente faltantes si es necesario.
- Si falla render, no escribir PNG/JSON final.

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
  - validacion manual GUI minima si background no cubre composer real.
- Actualizar `.context/agent_context.md`, `.context/index.md`, `.context/handoff.md` y `.context/worklog.jsonl`.

Criterio final:

- `Export Spritesheet` genera PNG final.
- `Export Spritesheet` genera JSON con formato aprobado.
- PNG y JSON comparten nombre base.
- Export soporta uno o varios clips incluidos.
- Indices JSON son globales, empiezan en `0` y usan `end` inclusivo.
- El addon no reintroduce modelo legacy ni rutas globales fuera de workspace.

## Supuestos

- Fase 5f queda como backend/accion auxiliar de render de frames finales.
- El flujo principal visible para usuario sera `Export Spritesheet`.
- El JSON del usuario es el contrato base de MVP.
- Clips duplicados por nombre ya se normalizan dentro del workspace.
- La fase 5h, si se crea, sera para mejoras posteriores de atlas avanzado y no para el JSON basico del MVP.

## Resultado De Ejecucion

Estado: validado por el usuario para export PNG/JSON, frames individuales y correcciones UI/naming/atajos posteriores.

Cambios implementados:

- Backend de layout puro en `spritesheet_frame_selector/export/layout.py`.
- Backend de metadata JSON en `spritesheet_frame_selector/export/metadata.py`.
- Composer PNG aislado en `spritesheet_frame_selector/export/composer.py` usando API nativa de Blender, sin Pillow.
- Operador `SPRITESHEET_OT_export_spritesheet` en `spritesheet_frame_selector/operators/export.py`.
- UI `Export Spritesheet` en `Export Settings`.
- Estado de ultimo export en `SpriteSheetWorkspace`:
  - `last_export_note`;
  - `last_export_png`;
  - `last_export_json`.
- Registro centralizado actualizado.
- Tests unitarios para layout y metadata en `tests/test_export_layout_metadata.py`.

Validaciones ejecutadas:

- `python3 -m compileall spritesheet_frame_selector`: pasa.
- `python3 -m unittest discover -s tests`: pasa, 53 tests.
- Busqueda legacy `spritesheet_state.clips`, `spritesheet_state.active_clip_index`, `spritesheet_state.export_settings`, `WorldSwapContext`: sin coincidencias.

Validaciones de Blender:

- El usuario valido en Blender que `Export Spritesheet` funciona correctamente.
- El usuario valido en Blender que `Export Individual Frames` funciona correctamente.
- Blender background en este entorno crashea antes de ejecutar Python con exit code 139, por lo que las validaciones Blender fueron manuales.

### Correccion Post Validacion Manual

El usuario valido que `Export Spritesheet` y el export por frame funcionan, pero pidio corregir el flujo de producto:

- Se retiro el boton separado de render/export por frame del panel.
- Se retiro el operador publico `spritesheet.render_final_frames`.
- `Export Settings` ahora contiene la opcion `Export Individual Frames`.
- Si la opcion esta activa, `Export Spritesheet` genera los PNG individuales dentro de `<output_folder>/<sheet_name>_frames/`.
- Los PNG individuales usan numeracion global por orden exportado, no el numero original del frame de Blender.
- El backend de render final queda como soporte interno para `Export Spritesheet`.

Validaciones automaticas de la correccion:

- `python3 -m compileall spritesheet_frame_selector`: pasa.
- `python3 -m unittest discover -s tests`: pasa, 53 tests.
- Busqueda de `render_final_frames`, `Final Render`, `Export PNG Sequence`, `Include in Export (future)` y `operators.render`: sin coincidencias activas.

### Correccion UI/Naming Posterior

Cambios implementados despues de la validacion del export:

- Los archivos de preview, render final y frames individuales exportados usan 3 digitos: `001`, `002`, `003`.
- `Export Individual Frames` conserva limpieza de archivos legacy de 6 digitos en la carpeta destino.
- `Selector` en el panel principal ya no muestra `Edit`/`Play`; esos controles quedan solo en la ventana visual.
- La seccion `Preview Cache` se renombro a `Preview`.
- `Preview Size` vive en `Preview` como menu desplegable con presets `32px`, `64px`, `128px`, `256px`.
- Los botones de `Preview` quedaron en dos acciones: `Generate Preview` y `Clear Cache`.
- `Refresh Preview` se retiro como operador publico registrado.
- `Export Settings` fue reordenado: `Sheet`, `Folder`, `W/H/Columns`, `Sheet Size`, `Export Individual Frames`, `Export Spritesheet`.
- Las listas de workspaces y clips usan campos editables nativos para el nombre, permitiendo renombrado inline desde la fila.
- El helper de export individual se separo en `spritesheet_frame_selector/export/sequence.py` para evitar depender de `bpy` en tests.
- El selector visual soporta atajos:
  - `Space`: iniciar/reanudar playback o pausar si ya esta reproduciendo.
  - `Tab`: alternar modo `Edit`/`Play`.
  - `Shift + Left`: detener playback y volver al primer frame.

Validaciones automaticas de la correccion UI/naming:

- `python3 -m compileall spritesheet_frame_selector`: pasa.
- `python3 -m unittest discover -s tests`: pasa, 54 tests.

Validacion manual posterior:

- El usuario valido en Blender el panel, menu de preview size, renombrado inline en listas, naming `001` y atajos del selector visual.
