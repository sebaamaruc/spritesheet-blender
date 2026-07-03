# Validation Plan V2

Estado: vigente
Autoridad: derivado de `docs/specs/mvp_v2.md` y `docs/architecture/addon_architecture.md`
Fecha: 2026-07-03

## Proposito

Este plan define las validaciones esperadas para reconstruir el addon V2 por fases. No reemplaza los planes de implementacion; cada fase debe incluir su propia validacion concreta.

## Validaciones Automaticas Posibles

### Sin Blender O Con Mocks Ligeros

- Calculo de frames desde `frame_start`, `frame_end` y `frame_step`.
- Validacion de rangos invalidos.
- Calculo de rows, columnas y dimensiones estimadas.
- Sanitizacion y unicidad de nombres/cache keys.
- Validacion de settings de export sin efectos secundarios.
- Generacion de metadata JSON multi-clip.
- Manejo de clips con nombres duplicados.
- Seleccion: select all, deselect all, invert, select every N.
- Composer math: posiciones, padding, margin y bounds.

### Con Blender En Background Cuando El Entorno Lo Permita

- Import del paquete.
- `register()` y `unregister()`.
- Activar, desactivar y reactivar addon.
- Registro de `PropertyGroup`, `CollectionProperty` y `PointerProperty`.
- Persistencia de propiedades en escena.
- Creacion de clip y frames.
- Guardar/reabrir `.blend` de prueba.
- Export simple con escena minima si Blender puede renderizar en CI/local.

## Validaciones Manuales En Blender

### Activar, Desactivar Y Reactivar

1. Instalar addon por ZIP o carpeta de desarrollo.
2. Activar addon.
3. Confirmar panel en `3D Viewport > Sidebar > SpriteSheet`.
4. Desactivar addon.
5. Reactivar addon.
6. Confirmar que no aparecen errores, handlers duplicados ni propiedades rotas.

### Archivo Nuevo

1. Abrir archivo nuevo.
2. Activar addon.
3. Crear clip sin configurar nada mas.
4. Confirmar warnings claros para camara, frames o previews faltantes.
5. Guardar archivo.
6. Reabrir y confirmar estado persistente.

### Cambio De Escena

1. Crear dos escenas.
2. Crear clips en una escena.
3. Cambiar a la segunda escena.
4. Confirmar que el panel no asume datos de la escena anterior.
5. Volver a la primera escena.
6. Confirmar que los clips siguen disponibles.

### Camara Faltante O Borrada

1. Crear clip con camara activa.
2. Borrar la camara.
3. Intentar preview y export.
4. Confirmar error o warning claro sin traceback.
5. Asignar nueva camara y repetir.

### Coleccion U Objeto Faltante

1. Crear una escena simple.
2. Crear clip y previews.
3. Borrar u ocultar objetos relevantes.
4. Confirmar que preview/export falla de forma controlada o produce warning comprensible.

### Preview Cache

1. Crear clip 1-20 con preview 64.
2. Generar previews.
3. Confirmar contador de previews generados.
4. Reabrir selector visual.
5. Confirmar que no regenera si no se pidio refresh.
6. Usar Refresh Preview.
7. Usar Clear Preview Cache.

### Selector Visual

1. Abrir selector con previews existentes.
2. Seleccionar y deseleccionar frames con click.
3. Ejecutar Select All, Deselect All, Invert y Select Every N.
4. Cerrar con boton.
5. Reabrir y confirmar estado.
6. Cerrar con ESC.
7. Intentar abrir dos veces rapidamente y confirmar que no quedan dos modals activos.

### Playback Preview

1. Seleccionar frames alternados.
2. Presionar Play.
3. Confirmar que reproduce solo seleccionados.
4. Cambiar FPS del clip.
5. Confirmar cambio perceptible.
6. Pausar y detener.
7. Cerrar selector durante playback y confirmar que no queda timer activo.

### Export PNG Individual

1. Seleccionar al menos un frame.
2. Configurar frame width, frame height, columns, padding, margin y transparencia.
3. Exportar spritesheet individual.
4. Confirmar PNG creado.
5. Confirmar alpha.
6. Confirmar dimensiones esperadas.
7. Confirmar que el frame actual de Blender se restaura.

### Atlas Multi-Clip Con JSON

1. Crear clips `idle` y `run`.
2. Generar previews y seleccionar frames en ambos.
3. Exportar atlas multi-clip.
4. Confirmar PNG creado.
5. Confirmar JSON creado.
6. Confirmar que JSON incluye `sheet`, `frameWidth`, `frameHeight`, `columns` y clips con `start`, `end`, `count`, `fps`.
7. Repetir con nombres duplicados y confirmar metadata sin sobrescritura silenciosa.

### Persistencia `.blend`

1. Crear clips, seleccionar frames y configurar export.
2. Guardar `.blend`.
3. Cerrar Blender.
4. Reabrir archivo.
5. Confirmar clips, seleccion, settings y warnings.
6. Confirmar que caches derivados no son requisito para recuperar la seleccion.

## Validaciones De No Regresion Por Fase

- Fase 4 scaffold: import, register/unregister, panel minimo.
- Fase 5a data model: persistencia, indices, undo/redo basico.
- Fase 5b clips: add, remove, duplicate y cambio de clip activo.
- Fase 5c preview cache: generate, refresh, clear y cache stale.
- Fase 5d selector: apertura, cierre, seleccion y cleanup.
- Fase 5e playback: timers, FPS y cierre durante playback.
- Fase 5f render: render solo seleccionados y restauracion de escena.
- Fase 5g composer/export: PNG correcto y errores controlados.
- Fase 5h multi-clip/json: atlas, metadata y nombres duplicados.
- Fase 6 distribucion: ZIP limpio, instalacion y validacion completa.

## Criterio De Validacion Final

Antes de considerar distribuible el addon V2:

- `register()` y `unregister()` deben pasar repetidamente.
- El addon debe activarse/desactivarse/reactivarse sin errores.
- El flujo MVP completo debe pasar en Blender 5.x.
- El ZIP debe contener solo archivos necesarios.
- No debe haber caches, `.DS_Store`, `__pycache__`, outputs ni pruebas temporales en el paquete.
- Las limitaciones conocidas deben quedar documentadas.
