# Informe de Pruebas — SpriteSheet Frame Selector V2

Fecha: 2026-07-31
Alcance: análisis del addon y verificación funcional por ejecución real
Entorno: macOS (Darwin 25.5.0), Blender 5.1.1, Python 3.13.9 (Blender) / 3.14.4 (sistema)
Estado del código analizado: `main` @ `c2facfe`

> Tarea lateral de validación. No modifica el `Plan Activo` ni el contexto PCS.

---

## 1. Resumen ejecutivo

Se auditó el addon (4.723 líneas, 12 subpaquetes) y se construyó una batería de
pruebas de integración que corre **dentro de Blender real**, porque la suite
existente usaba un `bpy` simulado y no ejercitaba ninguna API real.

| Suite | Tests | Resultado |
|---|---|---|
| Unitaria con stub (`tests/*.py`) | 85 | ✅ todos pasan |
| Integración headless (`tests/blender/it_*.py`) | 141 | ✅ todos pasan |
| Integración con GUI (`tests/blender/gui_checks.py`) | 10 | ✅ todos pasan |
| **Total** | **236** | ✅ |

Se encontraron **2 defectos confirmados**, ambos corregidos y cubiertos con tests
de regresión verificados. Se documentan **2 hallazgos adicionales** que se
reportan sin corregir por riesgo o por estar fuera de alcance, y **2
observaciones de comportamiento** fijadas por tests.

**Corrección importante a una suposición previa del proyecto:** `AGENTS.md`
afirma que «Blender en background crashea en Metal al inicializarse en este
sandbox». Eso **ya no es cierto** en este entorno: Blender corre en background
y renderiza sin problemas. Toda la validación automática de este informe se
apoya en esa capacidad.

---

## 2. Arquitectura analizada

Addon de tipo *extension* (`blender_manifest.toml`, `schema_version 1.0.0`,
`blender_version_min = "5.0.0"`), sin dependencias externas: solo `bpy`, `gpu`,
`blf` y stdlib.

Modelo de datos persistente en `Scene.spritesheet_state` (`schema_version = 2`),
con el **workspace como raíz**:

```
Scene.spritesheet_state
└── workspaces[]                 (id, name, default_camera, default_collections,
    │                             selector_mode, export_settings, last_export_*)
    └── clips[]                  (id, name, frame_start/end/step, fps,
        │                         overrides de camera/collections, preview_mode,
        │                         preview_size, cache_key/folder/dirty)
        └── frames[]             (frame_number, selected, preview_path)
```

Capas: `core/` (helpers puros) → `preview/`, `render/`, `export/`, `playback/`
(backends) → `operators/`, `ui/` (superficie Blender) → `registration.py`
(29 operadores, 2 UILists, 1 panel, 1 menú, 1 handler `load_pre`).

Flujo de uso: crear workspace → asignar cámara y collection por defecto → crear
clips con rango de frames → generar preview cache → seleccionar frames (panel o
selector modal) → reproducir → exportar PNG + JSON.

---

## 3. Qué se probó y con qué resultado

### 3.1 Ciclo de vida y registro
Registro, desregistro y re-registro repetido (3 ciclos) sin fugas de clases;
eliminación efectiva de `Scene.spritesheet_state` y de los 29 operadores;
handler `load_pre` registrado exactamente una vez. ✅

### 3.2 Modelo de datos y persistencia
Valores por defecto; `min=0` en `frame_start`/`frame_end` (frames negativos se
clampean a 0, regla de dominio); pisos de `frame_step`/`fps`; `preview_size`
acotado a 32–256; `poll` de cámara rechazando no-cámaras.

Unicidad de nombres de clips al crear y al renombrar (sufijo incremental
automático); duplicado profundo de workspace y clip con IDs nuevos y cache
derivado invalidado; clamp de índices activos en todas las operaciones CRUD.

**Persistencia real**: guardado a `.blend`, reset a factory y reapertura —
sobreviven workspaces, clips, rangos, fps, `preview_mode`, `selector_mode`,
export settings, punteros a cámara/collection y la selección frame a frame. ✅

Aislamiento entre escenas verificado (`scene.new` NEW y FULL_COPY). ✅

Referencias rotas: al borrar una collection, el puntero queda en `None` pero se
conserva `collection_name`, y la validación reporta `Missing collection: <nombre>`. ✅

### 3.3 Export (área de mayor riesgo)
Verificación **píxel a píxel** de la composición: orden row-major de los frames,
padding y margin dejando canaletas transparentes, fondo opaco cuando
`transparent=False`, última fila parcial, preservación de alpha en round-trip,
y ausencia de fugas de datablocks de imagen.

End-to-end con render real: PNG con dimensiones correctas, JSON con rangos
contiguos y ordenados multi-clip, clips excluidos omitidos, frames deseleccionados
no renderizados, frames individuales numerados por **orden de exportación**
(`001`, `002`…) y no por frame nativo de Blender (regla de dominio), y limpieza
de frames obsoletos al re-exportar con menos frames.

Restauración de estado tras exportar: `frame_current`, resolución, `filepath`,
`film_transparent`, `file_format`, cámara de escena y exclusión de collections
vuelven a su valor original. Sin temporales huérfanos. ✅

Errores previsibles reportados como `CANCELLED` con mensaje, nunca como traceback:
sin workspace, sin clips, sin carpeta de salida, sin nombre de hoja, sin frames
seleccionados, cámara ausente o borrada, collection borrada, rango vacío,
límite de 999 frames individuales, y hoja que excede 16384 px.

**Seguridad de rutas**: un `sheet_name` con `../` queda confinado a la carpeta de
salida (se aplica `os.path.basename`). ✅

### 3.4 Preview cache
Generación real en modo `RENDERED` en background; los modos `SOLID`/`MATERIAL`
fallan de forma controlada sin viewport. Purga de caches hermanos obsoletos al
cambiar la cache key; `Clear Cache` borra archivos pero **preserva la selección**;
protección efectiva contra borrar carpetas no gestionadas. Cache key estable e
independiente de los nombres visibles de workspace/clip. Raíz de cache junto al
`.blend` cuando está guardado y en temp cuando no. ✅

### 3.5 Visibilidad de collections
Con collections anidadas: los ancestros necesarios permanecen visibles, las no
incluidas quedan excluidas, la collection de la cámara efectiva se mantiene
visible, y el estado del view layer se restaura — **también cuando el cuerpo
lanza una excepción**. ✅

### 3.6 UI
Se ejecuta el `draw` real del panel y de ambos UILists contra un layout
instrumentado que **valida que cada propiedad, operador, menú y UIList
referenciado exista realmente**. Cubre estado vacío, workspace sin clip,
configuración completa con overrides, y avisos de referencias faltantes.
Se verificó también la etiqueta de resolución de hoja. ✅

En GUI real: el panel se registra en `VIEW_3D > Sidebar > SpriteSheet` con la
región `UI` presente. ✅

### 3.7 Selector visual modal
Despacho de eventos con eventos sintéticos: ESC y click derecho cancelan;
eventos de navegación y con modificadores pasan al viewport; clicks fuera del
panel no se capturan; modo EDIT alterna selección y modo PLAY mueve el cursor
sin alterarla; TAB cambia de modo; SPACE alterna play/pause; Shift+Flecha
izquierda vuelve al primer frame; los botones delegan en los operadores
registrados (regla de dominio: la UI no muta selección directamente); scroll con
rueda desplaza la grilla solo dentro del panel; la sesión se invalida al cambiar
de clip.

En GUI real: el modal abre, instala el draw handler, **el draw se ejecuta contra
un contexto GPU vivo sin excepciones** y produce celdas de hit-test (3 frames +
10 botones), y se libera limpiamente. ✅

### 3.8 Playback
Timer real de Blender registrado y desregistrado; pausa/reanudación conservando
posición; loop correcto sobre los frames listos; el refresco de la sesión ante
cambios de selección; detención al deseleccionar todo; y limpieza del timer
tanto al desregistrar el addon como al cargar otro `.blend` (handler `load_pre`). ✅

### 3.9 Undo
Verificado que el estado del addon (workspaces, clips y selección) **está
cubierto por el sistema de undo** de Blender: retrocede paso a paso
selección → clip → workspace. ✅ (ver limitación en §6).

---

## 4. Defectos confirmados y corregidos

### D1 — La detección de transparencia en previews estaba muerta (silenciosa)

- **Archivo**: `spritesheet_frame_selector/preview/generator.py`
- **Severidad**: media (funcionalidad inexistente, sin síntoma visible)

`_preview_file_has_transparency()` hacía `pixels[3::channels]` sobre
`image.pixels`, que es un `bpy_prop_array`. Ese tipo **no admite slicing con
paso**:

```
TypeError: slice indices must be integers or None or have an __index__ method
```

La excepción quedaba capturada por un `except Exception` amplio, de modo que la
función devolvía `None` **para toda imagen real**. Consecuencia: el aviso «no
transparent pixels detected» de los previews `SOLID`/`MATERIAL` (implementado en
Fase 6b) nunca se emitía.

**Por qué no lo detectó la suite existente**: el stub de `tests/test_preview_cache.py`
usaba una `list` de Python como `pixels`, y las listas **sí** admiten slicing con
paso. El test pasaba contra un tipo que no se comporta como el real.

**Corrección**: copiar los píxeles con `foreach_get` a un `array("f")` antes de
segmentar — el mismo idiom que ya usaba `export/composer.py`.

**Verificación**: al revertir la corrección fallan 3 tests (2 unitarios + 1 de
integración); con la corrección, los 3 pasan.

### D2 — `MATERIAL` preview filtraba un error crudo de RNA al usuario

- **Archivo**: `spritesheet_frame_selector/preview/generator.py`
- **Severidad**: media (afecta a un motor de render habitual en pixel-art)

`View3DShading.type` está **filtrado por el motor de render**. Con
`BLENDER_WORKBENCH` solo admite `WIREFRAME`, `SOLID` y `RENDERED`, por lo que
elegir el modo de preview `MATERIAL` producía esta nota en el panel:

```
bpy_struct: item.attr = val: enum "MATERIAL" not found in ('WIREFRAME', 'SOLID', 'RENDERED')
```

Confirmado por ejecución que el modo `MATERIAL` **sí funciona** con
`BLENDER_EEVEE`; el problema es exclusivo de Workbench, y el mensaje era
inaccionable.

**Corrección**: traducir el `TypeError` a un `RuntimeError` con mensaje útil:

```
Material preview is not available with the BLENDER_WORKBENCH render engine;
switch the render engine or pick another preview mode
```

**Verificación**: cubierto en las tres suites; se comprobó además que el estado
del shading del viewport se restaura correctamente tras el fallo.

---

## 5. Hallazgos reportados sin corregir

### H1 — `output_folder` no declara soporte de rutas relativas `//`

`SpriteSheetExportSettings.output_folder` es un `StringProperty(subtype="DIR_PATH")`
sin la opción `PATH_SUPPORTS_BLEND_RELATIVE`. Al asignar una ruta relativa al
`.blend` (que es lo que produce el explorador de archivos de Blender con
«Relative Path» activado, opción por defecto), Blender emite:

```
RuntimeWarning: SpriteSheetExportSettings.output_folder: does not support blend relative "//" prefix
```

**Impacto funcional: ninguno confirmado.** Se verificó por ejecución que el
export con `//out/` sobre un `.blend` guardado escribe correctamente en
`<carpeta_del_blend>/out/`. El ruido queda en la consola.

**Corrección propuesta** (no aplicada):

```python
output_folder: bpy.props.StringProperty(
    name="Output Folder",
    subtype="DIR_PATH",
    options={"ANIMATABLE", "PATH_SUPPORTS_BLEND_RELATIVE"},
    default="",
)
```

**Por qué no se aplicó**: la opción existe y se acepta en Blender 5.1.1, pero no
se pudo verificar en la versión mínima declarada (5.0.0), que no está instalada.
Una opción inválida en una `bpy.props` **rompe el registro completo del addon**,
así que el riesgo de aplicarla a ciegas supera al del warning. Requiere validar
antes en Blender 5.0.

### H2 — `spritesheet_frame_selector.zip` es un artefacto obsoleto

El zip en la raíz del repositorio está `.gitignore`-ado (`*.zip`), o sea que es
un artefacto local, no un entregable versionado. Aun así conviene registrarlo de
cara a la Fase 7 (empaquetado y distribución):

- Le **falta `core/debug.py`** (módulo que el código actual importa en tres sitios).
- **7 archivos** tienen contenido distinto al fuente actual (`workspace_state.py`,
  `composer.py`, `layout.py`, `operators/preview.py`, `playback/controller.py`,
  `preview/generator.py`, `ui/visual_selector.py`).
- Incluye basura de empaquetado: `__MACOSX/` (264 entradas en total) y
  `__pycache__/` con `.pyc` de cpython-313.

Se comprobó que el zip **sí registra** en Blender: es un snapshot antiguo
internamente coherente, anterior a las correcciones de Fase 6. No representa el
código actual. Debe regenerarse limpio antes de distribuir.

---

## 6. Observaciones de comportamiento (fijadas por tests, sin cambio)

### O1 — `clip.frames` se resincroniza de forma diferida

Cambiar `frame_start`, `frame_end` o `frame_step` marca `cache_dirty = True`
pero **no** reconstruye `clip.frames`. La resincronización ocurre recién al
generar previews o al exportar (`_prepare_export_clips` llama a `sync_clip_frames`).

**El export es correcto** (sincroniza antes de renderizar). Lo que queda desfasado
hasta ese momento son los contadores de la UI: «Stored Frames», «Selected Frames»,
el «N selected» del UIList y la etiqueta «Sheet Size».

Parece intencional: el panel muestra deliberadamente «Expected Frames» y «Stored
Frames» por separado. Se documentó el contrato con un test explícito en lugar de
cambiar la semántica de persistencia, que tiene radio de impacto amplio.

### O2 — El botón «Close» del selector libera la sesión pero el modal sobrevive un evento

`_execute_button_action("close")` llama a `cleanup_visual_selector_resources()`,
que libera la sesión y quita el draw handler (el panel desaparece de inmediato),
pero el operador modal sigue vivo hasta el siguiente evento, que consume
devolviendo `CANCELLED`. Impacto cosmético: un evento perdido tras cerrar.
Fijado por test.

---

## 7. Riesgos y limitaciones que permanecen

1. **Cobertura de versiones**: solo hay Blender 5.1.1 instalado. El
   `blender_version_min = "5.0.0"` del manifiesto **no se pudo verificar**.
   Además, se detectó un directorio de configuración de Blender 4.5 en el sistema:
   si se pretende dar soporte a 4.x, el manifiesto actual lo impide (el
   `schema_version 1.0.0` de extensions requiere 4.2+, así que bajar el mínimo
   sería técnicamente viable pero exige validación).

2. **Granularidad del undo por operador**: se verificó que el estado *es*
   recuperable por undo, pero no que cada operador empuje su propio paso en uso
   interactivo real. Los operadores declaran `bl_options={"REGISTER","UNDO"}`,
   que es el mecanismo correcto; sin embargo los pushes de undo no se disparan
   cuando el operador se invoca desde un callback de `bpy.app.timers`, que es la
   única vía de automatización disponible. **Pendiente: comprobación manual con
   Ctrl+Z** tras añadir un clip.

3. **Entrega real de eventos del modal**: la lógica de despacho está cubierta con
   eventos sintéticos y el `draw` se validó contra GPU real, pero el recorrido
   completo teclado/ratón a través del bucle de eventos de Blender no está
   automatizado. Requiere prueba manual.

4. **Rendimiento y escala**: se validaron los límites duros (999 frames
   individuales, 16384 px de hoja) pero no se hicieron pruebas de carga con
   cientos de frames reales ni medición de memoria. El composer materializa la
   hoja completa en un buffer en memoria; el límite de 16384 px acota el peor
   caso pero no se midió.

5. **Modos de preview en GPU no-Metal**: todas las pruebas de viewport se
   ejecutaron sobre macOS/Metal. No se verificó en otros backends gráficos.

6. **`AGENTS.md` desactualizado**: la regla «Blender en background crashea en
   Metal al inicializarse en este sandbox» ya no aplica y desaconseja una vía de
   validación que sí funciona. No se modificó por estar fuera del alcance
   solicitado; se recomienda actualizarla.

---

## 8. Cambios realizados

| Archivo | Cambio |
|---|---|
| `spritesheet_frame_selector/preview/generator.py` | Correcciones D1 y D2 (+36 / −2 líneas) |
| `tests/test_preview_cache.py` | 4 tests de regresión (stub fiel a `bpy_prop_array` y modos de shading) |
| `tests/blender/` | Nueva suite de integración en Blender real (141 tests + 10 checks GUI) |

Ninguna otra parte de la implementación fue modificada.

## 9. Cómo reproducir

```bash
python3 -m compileall spritesheet_frame_selector
python3 -m unittest discover -s tests
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python tests/blender/run_all.py
/Applications/Blender.app/Contents/MacOS/Blender --factory-startup --python tests/blender/gui_checks.py -- /tmp/gui_out.json
```

Detalle de módulos y notas de ejecución: `tests/blender/README.md`.
