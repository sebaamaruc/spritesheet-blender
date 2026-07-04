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
- Resolucion de workspace activo y clip activo con indices fuera de rango.
- Generacion de nombres unicos para workspaces y clips.
- Duplicacion logica de workspace sin copiar cache como valido.
- Resolucion logica de camera efectiva: override de clip o default de workspace.
- Resolucion logica de collections efectivas: override de clip o defaults de workspace.
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
- Persistencia de `Scene.spritesheet_state`.
- Creacion de workspace, default camera, default collections, clip y frames.
- Persistencia save/reopen de workspaces, clips, settings, overrides y seleccion.
- Cambio de escena sin mezclar workspaces entre escenas.
- Validacion de PointerProperty de camara y collections faltantes.
- Aplicar/restaurar visibilidad de collections en preview/render sin dejar estado modificado.
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
3. Crear workspace.
4. Crear clip sin configurar nada mas.
5. Confirmar warnings claros para workspace sin camara default, collections default, frames o previews faltantes.
6. Guardar archivo.
7. Reabrir y confirmar estado persistente.

### Cambio De Escena

1. Crear dos escenas.
2. Crear workspaces y clips en una escena.
3. Cambiar a la segunda escena.
4. Confirmar que el panel no asume datos de la escena anterior.
5. Volver a la primera escena.
6. Confirmar que workspaces, clips y settings siguen disponibles.

### Camara Faltante O Borrada

1. Crear workspace con default camera.
2. Crear clip sin override y generar preview.
3. Borrar la camara.
4. Intentar preview y export.
5. Confirmar error o warning claro sin traceback.
6. Asignar nueva default camera y repetir.
7. Activar override de camera en un clip, borrar esa camara y confirmar warning especifico del clip.

### Collections Faltantes O Borradas

1. Crear workspace con default collections.
2. Crear clip que hereda collections default.
3. Crear otro clip con override de collections.
4. Borrar una collection referenciada.
5. Intentar preview y export.
6. Confirmar warning claro usando nombre ultimo conocido.
7. Confirmar que no hay traceback.

### Visibilidad Por Collections

1. Crear collections anidadas.
2. Configurar workspace default collection como collection hija.
3. Generar preview.
4. Confirmar que ancestros necesarios permanecen visibles durante la operacion.
5. Confirmar que collections no incluidas quedan excluidas durante render/preview.
6. Confirmar que la collection de la camara efectiva queda visible.
7. Confirmar que al terminar se restaura el estado original del view layer.

### Coleccion U Objeto Faltante

1. Crear una escena simple.
2. Crear clip y previews.
3. Borrar u ocultar objetos relevantes.
4. Confirmar que preview/export falla de forma controlada o produce warning comprensible.

### Preview Cache

1. Crear workspace con camera y collections default.
2. Crear clip 1-20 con preview 64.
3. Generar previews.
4. Confirmar contador de previews generados.
5. Confirmar que cache key/ruta no dependen del nombre visible del clip.
6. Cambiar override de camera o collections y confirmar que el cache queda stale o cambia key segun la politica implementada.
7. Reabrir selector visual.
8. Confirmar que no regenera si no se pidio refresh.
9. Usar Refresh Preview.
10. Usar Clear Preview Cache.
11. Confirmar que Clear Preview Cache conserva frames y seleccion.

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

1. Crear workspace con camera, collections default y export settings.
2. Seleccionar al menos un frame en un clip incluido.
3. Configurar frame width, frame height, columns, padding, margin y transparencia.
4. Exportar spritesheet individual.
5. Confirmar PNG creado.
6. Confirmar alpha.
7. Confirmar dimensiones esperadas.
8. Confirmar que el frame actual de Blender se restaura.
9. Confirmar que se uso la camara efectiva y collections efectivas.

### Atlas Multi-Clip Con JSON

1. Crear workspace.
2. Crear clips `idle` y `run`.
3. Generar previews y seleccionar frames en ambos.
4. Marcar ambos como incluidos en export.
5. Cambiar orden manual de clips.
6. Exportar atlas multi-clip.
7. Confirmar PNG creado.
8. Confirmar JSON creado.
9. Confirmar que JSON incluye `sheet`, `frameWidth`, `frameHeight`, `columns` y clips ordenados con identificador estable, nombre visible, `start`, `end`, `count`, `fps`.
10. Repetir con nombres duplicados y confirmar metadata sin sobrescritura silenciosa.
11. Excluir un clip y confirmar que no aparece en atlas ni JSON.

### Persistencia `.blend`

1. Crear workspaces, defaults, clips, overrides, seleccionar frames y configurar export.
2. Guardar `.blend`.
3. Cerrar Blender.
4. Reabrir archivo.
5. Confirmar workspaces, clips, seleccion, settings, overrides y warnings.
6. Confirmar que caches derivados no son requisito para recuperar la seleccion.

## Validaciones De No Regresion Por Fase

- Fase 4 scaffold: import, register/unregister, panel minimo.
- Fase 5a workspace-root data model: persistencia de workspaces, clips, defaults, overrides, export settings, indices y undo/redo basico.
- Fase 5b workspace/clip management: add, remove, duplicate, select, reorder workspaces/clips y cambio de activos.
- Fase 5c preview cache workspace-aware: generate, refresh, clear, cache stale, camera/collections efectivas y preservacion de seleccion.
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
