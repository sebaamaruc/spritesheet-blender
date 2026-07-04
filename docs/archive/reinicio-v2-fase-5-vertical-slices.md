# Reinicio V2 Fase 5: Implementacion Por Vertical Slices

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar por subplanes aprobados
Estado De Ejecucion: reemplazado parcialmente por workspace-root

Estado Operativo Actual: reemplazado para 5a/5b/5c por `docs/plans/reinicio-v2-fase-5-workspace-root-vertical-slices.md`

Nota: este plan rector se conserva como historial aprobado. La ruta vigente para reconstruccion inmediata es workspace-root, segun `DEC-0009`.

## Referencia Superior

`docs/plans/reinicio-v2-master-plan.md`

## Objetivo

Ordenar la implementacion del MVP V2 en vertical slices pequenas, validadas una por una, sin saltar directamente a una feature grande ni reconstruir el addon como bloque monolitico.

Este plan es rector. No implementa codigo por si solo. Cada slice debe tener un subplan especifico aprobado antes de ejecutar cambios.

## Precondiciones

- Fase 1 validada: estado V1 preservado por Git.
- Fase 2 validada: documentacion V2 vigente creada.
- Fase 3 validada: arbol activo limpiado.
- Fase 4 validada: scaffold V2 minimo creado y validado con Blender background.
- Checkpoint Git creado: `77bda46 reinicio v2 docs cleanup scaffold`.

## Fuentes Operativas

- `docs/specs/mvp_v2.md`
- `docs/architecture/addon_architecture.md`
- `docs/design/visual_selector_strategy.md`
- `docs/specs/validation_plan.md`
- `spritesheet_frame_selector/`

## Reglas Generales

- No copiar codigo V1 desde Git/archive como base estructural.
- No implementar mas de un slice por plan aprobado.
- Cada slice debe dejar el addon importable y registrable.
- Cada slice debe preservar `register()`/`unregister()` defensivos.
- Cada slice debe ejecutar validaciones automaticas posibles y Blender background si aplica.
- Si un slice deja deuda o una validacion falla, no avanzar al siguiente slice.
- Las pruebas nuevas deben validar V2, no reconstruir supuestos legacy.
- No crear ZIP distribuible hasta Fase 6 salvo prueba manual puntual ignorada por `.gitignore`.

## Orden De Subplanes

### 5a: Data Model Y Persistencia

Plan requerido: `docs/plans/reinicio-v2-fase-5a-data-model-persistencia.md`.

Objetivo:

- Definir `PropertyGroup` V2 real para clips, frames, export settings y estado de escena.
- Registrar `CollectionProperty` y `PointerProperty` sobre `bpy.types.Scene`.
- Mantener persistencia `.blend` sin operadores complejos.

Criterio de salida:

- Se pueden crear datos mediante Python/Blender background.
- Los indices activos tienen bounds seguros.
- `register()`/`unregister()` siguen pasando repetidamente.

### 5b: Gestion De Clips

Plan requerido: `docs/plans/reinicio-v2-fase-5b-gestion-clips.md`.

Objetivo:

- Agregar operadores y UI minima para add/remove/duplicate/select clips.
- Mostrar lista de clips y configuracion basica del clip activo.
- No generar previews todavia.

Criterio de salida:

- El usuario puede administrar clips desde el panel.
- Cambios de escena y ausencia de clip activo no producen errores.

### 5c: Preview Cache

Plan requerido: `docs/plans/reinicio-v2-fase-5c-preview-cache.md`.

Objetivo:

- Implementar calculo de frames esperados, paths/cache keys estables y estado de cache.
- Agregar operadores Generate/Refresh/Clear Preview con backend minimo y seguro.
- Mantener cache por identificador estable, no solo por nombre visible.

Criterio de salida:

- Preview cache se puede crear/refrescar/limpiar sin destruir seleccion persistente.
- Cache stale se comunica como warning simple.

### 5d: Visual Selector Minimo

Plan requerido: `docs/plans/reinicio-v2-fase-5d-visual-selector-minimo.md`.

Objetivo:

- Implementar selector visual minimo con grilla/contact sheet o fallback visual aceptable.
- Soportar click toggle y acciones Select All, Deselect All, Invert, Select Every N.
- No incluir interacciones avanzadas si comprometen estabilidad.

Criterio de salida:

- El selector abre/cierra confiablemente.
- No filtra draw handlers, timers ni imagenes temporales.
- La seleccion persiste en `.blend`.

### 5e: Playback Preview

Plan requerido: `docs/plans/reinicio-v2-fase-5e-playback-preview.md`.

Objetivo:

- Reproducir solo frames seleccionados usando previews cacheados.
- Agregar Play/Pause/Stop y FPS de clip.
- Controlar timers defensivamente.

Criterio de salida:

- Playback no renderiza.
- Cerrar selector durante playback limpia timers.
- Cambiar clip o desactivar addon no deja estado vivo.

### 5f: Render Final

Plan requerido: `docs/plans/reinicio-v2-fase-5f-render-final.md`.

Objetivo:

- Renderizar solo frames seleccionados.
- Respetar alpha/transparency y settings de escena.
- Restaurar frame actual y settings temporales.

Criterio de salida:

- Render final produce imagenes intermedias esperadas.
- Camara faltante o invalida falla con warning/error controlado.

### 5g: Composer Y Export Individual

Plan requerido: `docs/plans/reinicio-v2-fase-5g-composer-export.md`.

Objetivo:

- Implementar backend composer reemplazable.
- Exportar spritesheet PNG individual.
- Soportar columns, rows auto, frame size, padding, margin y PNG sequence opcional apagada.

Criterio de salida:

- Export individual genera PNG correcto.
- Validacion no crea carpetas durante `draw`.
- Dimensiones grandes tienen warning o bloqueo razonable.

### 5h: Multi-Clip Atlas Y JSON

Plan requerido: `docs/plans/reinicio-v2-fase-5h-multiclip-atlas-json.md`.

Objetivo:

- Exportar multiples clips a un atlas.
- Generar JSON simple obligatorio para atlas multi-clip.
- Resolver nombres duplicados sin sobrescritura silenciosa.

Criterio de salida:

- Atlas multi-clip y JSON pasan validacion manual.
- JSON incluye `sheet`, `frameWidth`, `frameHeight`, `columns` y clips con `start`, `end`, `count`, `fps`.

## Validacion Transversal Por Slice

Cada subplan debe exigir:

- `python3 -m compileall spritesheet_frame_selector`.
- Blender background import/register/unregister.
- Pruebas automaticas especificas si el slice agrega logica testeable fuera de Blender.
- Limpieza posterior de `__pycache__/`, `*.pyc`, `.DS_Store` y outputs.
- `git status --short --ignored` revisado antes de cerrar.

## Riesgos

- Mezclar UI con logica de dominio demasiado temprano.
- Introducir estado global o caches stale.
- Crear operadores dependientes de contexto implicito.
- Implementar selector visual avanzado antes de validar modelo/cache.
- Dejar handlers, timers o draw callbacks sin limpieza.
- Saltar el export individual y llegar al atlas sin base estable.

## Criterio De Termino De Fase 5

La Fase 5 queda lista para validacion/distribucion cuando todos los subplanes 5a-5h esten implementados y validados, el flujo MVP V2 completo funcione en Blender, y no existan features fuera de `docs/specs/mvp_v2.md`.

## Proximo Paso

Crear `docs/plans/reinicio-v2-fase-5a-data-model-persistencia.md` como plan especifico propuesto. No implementar data model hasta que ese subplan sea aprobado.
