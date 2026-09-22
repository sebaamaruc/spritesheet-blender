# Tests de integración en Blender real

Los tests de `tests/*.py` corren con un `bpy` simulado (stub) y validan lógica pura.
Los de esta carpeta corren **dentro de Blender real** y validan registro, propiedades
persistentes, operadores, render, composición de píxeles, UI y playback.

## Requisitos

Blender 5.x instalado. Ruta usada en los ejemplos: `/Applications/Blender.app/Contents/MacOS/Blender`.

## Suite headless (background)

Cubre todo lo que no necesita ventana. Devuelve código de salida distinto de 0 si algo falla.

```bash
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python tests/blender/run_all.py
```

Para un solo módulo:

```bash
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python tests/blender/run_all.py -- "it_export.py"
```

| Módulo | Cubre |
|---|---|
| `it_data_model.py` | register/unregister, propiedades, límites, CRUD workspaces/clips, selección, persistencia `.blend` |
| `it_export.py` | composición píxel a píxel, export end-to-end, JSON, validaciones y errores previsibles |
| `it_ui_preview_playback.py` | draw del panel y UILists, visibilidad de collections, preview cache, playback con timers reales |
| `it_selector_interaction.py` | geometría y despacho de eventos del selector modal (clicks, teclado, scroll) |
| `it_edge_cases.py` | aislamiento entre escenas, rutas de cache, rutas relativas `//`, nombres, escala |

## Suite con GUI

Valida lo que exige una ventana real: previews de viewport (`SOLID`/`MATERIAL`),
restauración del shading, el draw del selector contra un contexto GPU vivo y undo.

```bash
/Applications/Blender.app/Contents/MacOS/Blender --factory-startup --python tests/blender/gui_checks.py -- /tmp/gui_out.json
```

Abre una ventana de Blender unos segundos, escribe el resultado en el JSON indicado
y cierra el proceso. Cada entrada del JSON trae `name`, `status` y `detail`.

## Notas

- La suite headless **no** interfiere con `python3 -m unittest discover -s tests`:
  el patrón por defecto es `test*.py` y estos archivos usan el prefijo `it_`.
- `gui_checks.py` termina con `os._exit(0)`: llamar a `bpy.ops.wm.quit_blender()`
  desde un callback de `bpy.app.timers` hace crashear a Blender (contexto nulo).
- Undo no se puede ejercitar en background (`ed.undo` exige contexto de ventana);
  esa validación vive solo en la suite GUI.
