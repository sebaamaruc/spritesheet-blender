# Arquitectura Del Addon V2

Estado: vigente
Autoridad: derivado de `docs/specs/product_requirements.md`, `docs/specs/mvp_v2.md` y `docs/archive/audit_report.md`
Fecha: 2026-07-03

## Principios

- Blender-first: usar APIs nativas cuando sean suficientes.
- Modularidad real: UI, operadores, persistencia, preview, playback, render, composer y export no deben mezclarse.
- Sin dependencias externas obligatorias.
- Estado persistente en `.blend`; caches externos son derivados y descartables.
- Registro y unregister defensivos desde el scaffold.
- Funciones de dominio reciben datos explicitos. No deben leer `bpy.context` global cuando puedan recibir `context`, `scene`, `clip` o settings.
- El codigo generado previo solo sirve como referencia de riesgos.

## Paquetes Sugeridos

La estructura exacta se definira en Fase 4, pero los limites de responsabilidad deben respetar esta forma:

```text
spritesheet_frame_selector/
  __init__.py
  blender_manifest.toml
  registration.py
  properties.py
  preferences.py
  ui/
    panels.py
    lists.py
    visual_selector.py
  operators/
    clips.py
    preview.py
    selection.py
    playback.py
    export.py
  core/
    clip_model.py
    frame_math.py
    validation.py
    paths.py
    cache.py
  preview/
    generator.py
    loader.py
  playback/
    controller.py
  render/
    queue.py
    scene_state.py
  export/
    composer_base.py
    composer_native.py
    metadata.py
    pipeline.py
```

## Limites De Modulo

### Registro

- Contiene lista centralizada de clases.
- Registra clases en orden dependiente: PropertyGroups antes que tipos que los referencian.
- Registra propiedades sobre `bpy.types.Scene` despues de registrar sus `PropertyGroup`.
- Unregister limpia propiedades en orden inverso.
- Unregister tolera ejecuciones parciales y recarga del addon.
- No debe abrir archivos, crear caches ni ejecutar logica de producto.

### Properties / Data Model

- Define `PropertyGroup`, `CollectionProperty`, `PointerProperty` y propiedades simples.
- No ejecuta render, export ni IO pesado.
- Valida rangos basicos con callbacks simples solo si no producen efectos secundarios.
- Expone datos suficientes para persistencia en `.blend`.

### Core

- Contiene logica pura o casi pura: calculos de frames, dimensiones, paths, nombres seguros, validacion y resumenes.
- No depende de UI.
- Debe ser testeable fuera de Blender cuando sea posible.
- Puede recibir objetos Blender explicitos si no hay alternativa, pero no debe depender de estado implicito global.

### UI

- Dibuja paneles, listas y controles.
- No crea directorios, no renderiza, no compone imagenes y no muta estado complejo durante `draw`.
- Llama operadores para acciones.
- Muestra warnings calculados por core/validation.

### Operadores

- Son adaptadores entre Blender UI y servicios de dominio.
- Cada operador valida contexto y datos faltantes antes de ejecutar.
- No debe asumir escena, clip activo, camara o action existentes.
- Debe reportar errores con `self.report()` cuando la accion no puede completarse.
- Operadores largos deben conservar/restaurar frame y settings temporales.

### Preview

- Genera thumbnails pequenos y cacheados.
- No borra seleccion persistente al fallar una generacion.
- Expone refresh y clear cache.
- Mantiene cache por clip con identificadores estables, no solo por nombre visible.
- No intenta detectar automaticamente todos los cambios de escena.

### Visual Selector

- Consume previews existentes y estado de seleccion.
- Mantiene dibujo y eventos aislados de la logica de modelo.
- Debe protegerse contra doble invocacion modal.
- Draw handlers, timers e imagenes temporales deben limpiarse siempre.
- Fallos de carga de thumbnails no deben bloquear el cierre del selector.

### Playback

- Usa previews cacheados, no render final.
- No registra timers duplicados.
- Debe detener timers al cerrar selector, cambiar clip, desactivar addon o fallar una operacion.
- No modifica frames seleccionados.

### Render

- Renderiza solo frames seleccionados.
- Conserva/restaura frame actual, motor, resolucion, transparencia y settings temporales.
- Maneja camara faltante o invalida.
- No deja datablocks temporales, worlds, images o handlers sin limpiar.

### Composer

- Tiene interfaz reemplazable.
- Recibe lista ordenada de imagenes renderizadas y settings explicitos.
- No manipula pixel por pixel en Python puro si hay alternativa razonable.
- Valida dimensiones maximas antes de asignar buffers grandes.
- Puede tener backend nativo inicial y backend optimizado opcional futuro.

### Export

- Orquesta validacion, render, composicion, PNG sequence opcional y metadata.
- No debe contener logica de UI.
- Debe tratar nombres duplicados de clips sin sobrescribir metadata.
- Debe crear directorios solo durante acciones explicitas de export, no durante draw o validacion pasiva.

### Cache Y Paths

- Centraliza resolucion de carpetas.
- Diferencia datos persistentes de caches derivados.
- Maneja archivos `.blend` no guardados usando ubicacion temporal controlada.
- Permite limpieza manual.
- Evita colisiones por nombres duplicados.

## Modelo De Datos Conceptual

```text
Scene
  spritesheet_clips: Collection[SpriteSheetClip]
  spritesheet_active_clip_index: int
  spritesheet_export_settings: SpriteSheetExportSettings

SpriteSheetClip
  id: string
  name: string
  frame_start: int
  frame_end: int
  frame_step: int
  fps: int
  camera: PointerProperty(Object) o referencia validable
  preview_size: int
  frames: Collection[SpriteSheetFrameItem]
  active_frame_index: int
  cache_key/cache_folder: string
  cache_dirty: bool
  last_preview_note: string

SpriteSheetFrameItem
  frame_number: int
  selected: bool
  preview_path: string
  original_index: int

SpriteSheetExportSettings
  frame_width: int
  frame_height: int
  columns: int
  padding: int
  margin: int
  transparent: bool
  output_folder: string
  sheet_name: string
  export_png_sequence: bool
  png_sequence_folder: string
```

## Reglas Blender API

- `register()` no debe depender de escena activa.
- `unregister()` debe limpiar Scene properties con `delattr` defensivo.
- Handlers, timers, draw handlers y previews deben tener cleanup explicito.
- Los operadores deben implementar `poll` robusto o validacion temprana.
- Los `draw` de panels no deben producir efectos secundarios de filesystem.
- Modal operators deben cerrar con ESC/RIGHTMOUSE de forma confiable.
- GPU state debe restaurarse con `try/finally` cuando se cambie.
- Undo/redo no debe corromper indices activos ni referencias a clips.
- Recarga del addon no debe dejar timers o handlers vivos.

## Riesgos Heredados Que La V2 Debe Evitar

- Modal que no cierra por orden incorrecto de eventos.
- Draw handlers o timers filtrados.
- Caches basados solo en `clip.name`.
- Validaciones que crean carpetas durante `draw`.
- Uso fragil de `bpy.context` dentro de utilidades.
- Metadatos JSON que sobrescriben clips con nombres duplicados.
- Worlds o images temporales acumulados en `.blend`.
- APIs de render engine incompatibles con Blender 5.x.
- Prints de debug en codigo de produccion.

## Zonas Que Conviene No Sobreoptimizar Al Inicio

- Packing irregular.
- Backends acelerados opcionales.
- Deteccion automatica de cambios de cache.
- Interacciones avanzadas del selector antes de tener click toggle y playback robustos.
- UI altamente pulida antes de validar el flujo.
