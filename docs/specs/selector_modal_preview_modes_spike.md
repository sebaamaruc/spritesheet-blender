# Spike Tecnico - Selector Modal Y Preview Modes

Estado: validado
Fecha: 2026-07-03
Autoridad: usuario + evidencia local Blender 5.1.1
Plan: `docs/plans/reinicio-v2-fase-5e1-spike-selector-modal-preview-modes.md`

## Preguntas Del Spike

1. Si el selector debe seguir con UI nativa o pasar a una superficie modal/custom.
2. Donde debe vivir `selector_mode`.
3. Como deben funcionar previews grandes y playback visual.
4. Como resolver modos de preview: solid, textura/material y luz renderizada.

## Evidencia Ejecutada

Entorno:

- Blender 5.1.1
- macOS/Darwin
- Addon V2 workspace-root validado hasta Fase 5e

Pruebas ejecutadas:

- Inspeccion de engines disponibles en `RenderSettings.engine`.
- Inspeccion de `View3DShading.type`.
- Inspeccion de `bpy.ops.render.opengl`.
- Inspeccion de `bpy.ops.render.render`.
- Inspeccion de APIs `SpaceView3D.draw_handler_add/remove`.
- Inspeccion de import de `gpu`, `blf` y `gpu_extras.batch`.
- Render still PNG temporal fuera del repo con `bpy.ops.render.render(write_still=True)`.

Resultados:

```text
BLENDER 5.1.1
ENGINES ['BLENDER_EEVEE']
HAS_SPACEVIEW3D_DRAW_HANDLER True True
GPU_IMPORT_OK True True True
OPENGL_PROPS animation, render_keyed_only, sequencer, write_still, view_context
RENDER_PROPS animation, write_still, use_viewport, use_sequencer_scene, layer, scene, frame_start, frame_end
VIEW3D_SHADING_TYPES WIREFRAME, SOLID, MATERIAL, RENDERED
OPENGL_BACKGROUND_FAIL RuntimeError: Cannot use OpenGL render in background mode
RENDER_STILL_RESULT {'FINISHED'} con PNG temporal creado fuera del repo
```

Limitacion confirmada:

- Las funciones GPU de dibujo existen, pero no pueden validarse en background porque no hay contexto grafico. La validacion final de superficie modal/custom requiere Blender GUI.

## Decision Recomendada

### Selector

Pasar a superficie modal/custom en Fase 5e1.

Motivo:

- La UI nativa `invoke_props_dialog` no da suficiente control sobre tamano de thumbnails, visor grande, contornos de estado ni layout eficiente.
- El selector necesita ser una herramienta visual, no una lista de botones con texto.
- La superficie custom permite separar claramente:
  - visor grande del frame actual;
  - grilla de frames;
  - contornos de seleccion/playback;
  - modo `Edit` y modo `Play`;
  - controles compactos.

Forma tecnica recomendada:

- `Operator` modal en area `VIEW_3D`.
- `SpaceView3D.draw_handler_add(..., 'WINDOW', 'POST_PIXEL')`.
- Dibujo con `gpu`, `blf` y `gpu_extras.batch`.
- Texturas desde imagenes cargadas de `frame.preview_path`.
- Estado runtime del modal en modulo dedicado.
- Cleanup obligatorio:
  - remover draw handler;
  - detener playback;
  - liberar imagenes/texturas temporales;
  - limpiar referencias al cerrar, `ESC`, `RIGHTMOUSE`, cambio de workspace/clip y `unregister()`.

Fallback permitido:

- Si la prueba GUI de Fase 5e1 demuestra inestabilidad grave, mantener UI nativa temporal pero redisenada, dejando superficie modal para una fase posterior.

### `selector_mode`

Debe vivir en `.blend`, como indico el usuario.

Ubicacion recomendada:

- `SpriteSheetWorkspace.selector_mode`

Valores:

- `EDIT`
- `PLAY`

Justificacion:

- El selector opera dentro del workspace activo.
- Mantener el modo por workspace evita que un workspace de revision/playback fuerce otro workspace a abrir en el mismo modo.
- No debe vivir por frame.
- No debe vivir solo en runtime porque el usuario espera que Blender recuerde su modo de trabajo.

Comportamiento:

- `EDIT`: click en frame alterna `SpriteSheetFrameItem.selected`.
- `PLAY`: click cambia frame actual o punto de inicio sin alterar seleccion.
- Play/Pause/Stop visibles en ambos modos, pero visualmente prioritarios en `PLAY`.

### Preview Size

El default actual `64x64` es insuficiente para inspeccion real.

Recomendacion:

- Mantener `clip.preview_size`, pero ofrecer presets visibles:
  - `64`: rapido, icono/debug.
  - `128`: minimo util.
  - `256`: recomendado para selector/playback.
  - `512`: inspeccion alta, mas lento/pesado.
- Cambiar `preview_size` marca cache dirty.
- `preview_size` ya participa en cache key; debe seguir haciendolo.
- El selector debe poder dibujar previews grandes hasta el tamano generado; escalar un PNG de 64 a 256 no reemplaza generar preview a 256.

### Preview Mode

Agregar modo de preview persistente.

Modelo recomendado:

- `SpriteSheetWorkspace.default_preview_mode`
- `SpriteSheetClip.use_preview_mode_override`
- `SpriteSheetClip.preview_mode`

Valores recomendados:

- `SOLID`: rapido para timing/pose.
- `MATERIAL`: textura visible sin intentar resultado final de luces.
- `RENDERED`: luz/material/render mas fiel, mas lento.

Resolucion efectiva:

```text
effective_preview_mode = clip.preview_mode si use_preview_mode_override
                         si no workspace.default_preview_mode
```

Cache:

- `effective_preview_mode` debe entrar en `build_preview_cache_key`.
- Cambiar modo de preview marca cache dirty.
- El panel debe mostrar warning claro cuando el cache fue generado con otro modo.

Backend recomendado:

- `SOLID` y `MATERIAL`: usar captura de viewport/OpenGL en contexto GUI cuando exista.
- `RENDERED`: puede usar render still nativo con `BLENDER_EEVEE` cuando no haya contexto OpenGL o cuando se requiera fidelidad.
- Background tests solo pueden validar ruta render still; no validan OpenGL/viewport porque Blender no tiene contexto OpenGL en background.

Implicacion:

- Fase 5e1 debe incluir una prueba manual GUI obligatoria para `SOLID` y `MATERIAL`.
- No reintroducir `WorldSwapContext`.

### Playback Grande

El playback debe mostrar una vista grande del frame actual.

Recomendacion de layout:

```text
┌─────────────────────────────────────────────┐
│ Header compacto: workspace / clip / mode    │
├───────────────────────┬─────────────────────┤
│ Visor grande actual   │ Controles compactos │
│ frame en play/edit    │ Play Pause Stop     │
│                       │ Select tools        │
├───────────────────────┴─────────────────────┤
│ Grilla thumbnails grandes                    │
│ borde seleccionado + borde frame actual      │
└─────────────────────────────────────────────┘
```

Estados visuales:

- Seleccionado: borde persistente, por ejemplo azul/verde.
- Frame actual/playback: borde distinto, por ejemplo amarillo/naranja.
- Seleccionado + actual: doble borde o borde actual dominante con marca secundaria.
- No usar checkbox por celda.
- Texto por celda minimo: numero de frame pequeno.

## Riesgos

### Modal/Draw Handler

Riesgo:

- handler vivo despues de cerrar;
- timer de playback vivo;
- imagenes/texturas retenidas;
- errores de GPU al recargar addon.

Mitigacion:

- controlador unico de selector modal;
- cleanup centralizado llamado por cierre y `unregister()`;
- pruebas manuales de abrir/cerrar repetido, ESC, RIGHTMOUSE, desactivar addon.

### Preview Modes

Riesgo:

- `SOLID` y `MATERIAL` dependen de contexto viewport, no validable por background.

Mitigacion:

- tests automaticos para modelo/cache key;
- Blender background para `RENDERED`;
- validacion manual GUI para `SOLID/MATERIAL`.

### Tamano De Preview

Riesgo:

- previews 512 por muchos frames pueden consumir cache y memoria.

Mitigacion:

- presets claros;
- default recomendado 256 solo si el usuario lo acepta;
- warning de cantidad de frames y tamano estimado en plan 5e1 o fase export.

## Recomendacion Para El Siguiente Plan

Crear `docs/plans/reinicio-v2-fase-5e1-selector-playback-ux.md`.

Alcance recomendado:

- Agregar `selector_mode` persistente en `SpriteSheetWorkspace`.
- Agregar preview modes persistentes:
  - workspace default;
  - override opcional por clip.
- Actualizar cache key para incluir preview mode efectivo.
- Agregar presets de preview size.
- Reemplazar el selector visual nativo por modal/custom.
- Crear visor grande de frame actual.
- Usar contornos visuales para seleccionado y playback.
- Separar modo `EDIT` y modo `PLAY`.
- Reordenar panel principal de forma compacta, sin eliminar configuracion necesaria.

No incluir:

- render final;
- composer;
- export;
- atlas/JSON.

Validacion obligatoria:

- `compileall`.
- `unittest`.
- Blender background para register/unregister, modelo/cache y ruta `RENDERED`.
- Blender GUI manual para:
  - apertura/cierre modal;
  - thumbnails grandes;
  - click en `EDIT`;
  - click en `PLAY`;
  - playback con visor grande;
  - cambio de workspace/clip;
  - desactivar/reactivar addon sin handlers/timers vivos.
