# MVP V2

Estado: vigente
Autoridad: derivado de `docs/specs/product_requirements.md`
Fecha: 2026-07-03

## Proposito

Este documento define el alcance operativo del primer MVP V2. La arquitectura, estrategia visual y validacion viven en documentos separados:

- `docs/architecture/addon_architecture.md`
- `docs/design/visual_selector_strategy.md`
- `docs/specs/validation_plan.md`

## Flujo Principal

1. El usuario crea o selecciona un workspace.
2. Define defaults del workspace: camara, collections visibles y settings de export.
3. Crea o selecciona un clip dentro del workspace.
4. Define `frame_start`, `frame_end`, `frame_step`, FPS, preview size y overrides opcionales de camara/collections.
5. Genera o refresca previews cacheados usando la visibilidad efectiva del workspace + clip.
6. Abre el selector visual.
7. Selecciona o deselecciona frames.
8. Reproduce el resultado con playback preview.
9. Configura inclusion, orden y export del workspace.
10. Exporta el clip individual como spritesheet PNG.
11. Exporta multiples clips incluidos del workspace como atlas cuando lo necesite, con JSON simple.

## Obligatorio Para MVP V2

### Modelo Y Persistencia

- Workspace es la raiz de dominio del MVP V2.
- El estado persistente vive bajo una unica propiedad de escena: `Scene.spritesheet_state`.
- `SpriteSheetSceneState` contiene `workspaces` y `active_workspace_index`.
- `SpriteSheetWorkspace` contiene `id`, `name`, `default_camera`, `default_collections`, `clips`, `active_clip_index` y `export_settings`.
- Multiples workspaces y multiples clips por workspace en el modelo desde el inicio.
- Estado persistente en `.blend`.
- Clip con `id`, nombre, inclusion en export, rango, step, FPS, preview size, frames, seleccion y estado de cache.
- Clip con override opcional de camara y override opcional de collections.
- Workspace con camara default y collections default para preview/render/export.
- Export settings persistentes por workspace con frame width, frame height, columns, padding, margin, transparencia, output folder, sheet name y opcion de PNG sequence apagada por defecto.
- Indices activos con validacion de bounds.
- Nombres de clip manejados de forma estable para evitar colisiones en cache y metadata.
- Caches derivados identificados por ids/cache keys, no por nombres visibles.

### UI Principal

- Panel en `3D Viewport > Sidebar > SpriteSheet`.
- Gestion de workspaces.
- Selector de workspace activo.
- Lista de clips del workspace activo.
- Configuracion del workspace activo: nombre, default camera, default collections y export settings.
- Configuracion del clip activo.
- Inclusion/exclusion del clip activo para export.
- Orden manual de clips dentro del workspace.
- Controles de preview.
- Resumen de seleccion.
- Warnings claros.
- Contadores de total de frames, previews generados, frames seleccionados, rows estimadas y resolucion estimada.

### Preview

- Generacion de previews pequenos y cacheados.
- Preview size custom desde el inicio.
- Presets 32, 64 y 128.
- Preview generado segun camara efectiva y collections efectivas.
- Camara efectiva: override del clip si esta habilitado; si no, default del workspace. En workspace-root no se debe usar `scene.camera` como fallback silencioso para ocultar configuracion incompleta.
- Collections efectivas: override del clip si esta habilitado; si no, default del workspace.
- Boton `Generate Preview`.
- Boton `Refresh Preview`.
- Boton `Clear Preview Cache`.
- Warning simple cuando el cache pueda estar desactualizado.
- Warning claro si faltan camara o collections efectivas.
- No regenerar automaticamente por cada cambio de escena.

### Selector Visual

- Ventana, popup o modal mas amplio que el sidebar.
- Grilla visual tipo contact sheet.
- Cada celda muestra thumbnail, numero de frame y estado seleccionado/no seleccionado.
- Click toggle como interaccion minima obligatoria.
- Acciones globales: Select All, Deselect All, Invert Selection, Select Every N Frames.
- Ruta clara para agregar drag select, box select y shift range despues.

### Playback Preview

- Playback usando solo frames seleccionados.
- Orden temporal.
- FPS configurable por clip.
- Play, pause y stop.
- Loop si no complica la estabilidad.
- Uso exclusivo de previews cacheados, sin render final.
- Feedback inmediato dentro del selector visual o en un popup simple.

### Render Y Export Individual

- Renderizar solo frames seleccionados.
- Renderizar usando la camara efectiva y collections efectivas del workspace + clip.
- Respetar alpha/transparency.
- Restaurar frame actual y settings temporales al terminar.
- Exportar PNG spritesheet individual.
- Calcular rows automaticamente desde columns.
- Soportar padding y margin.
- Export PNG sequence disponible como opcion, apagada por defecto.

### Atlas Multi-Clip Y JSON

- Estructura preparada para export combinado desde el inicio.
- Export atlas multi-clip incluido en MVP V2 si el export individual y el modelo ya son estables.
- JSON simple obligatorio para atlas multi-clip.
- El atlas exporta clips incluidos del workspace activo en orden manual.
- El JSON debe incluir sheet, frameWidth, frameHeight, columns y clips con identificador estable, nombre visible, start, end, count y FPS opcional.
- El JSON no debe usar nombres de clip como keys unicas que puedan sobrescribirse; debe usar una lista ordenada o keys estables.
- El JSON no debe convertirse en metadata compleja de runtime.

### Registro Y Distribucion

- Addon instalable por ZIP.
- Registro y unregister idempotentes y defensivos.
- Sin dependencias externas obligatorias.
- Compatibilidad objetivo con Blender 5.x.

## Diferido

- Drag select estable.
- Box select/marquee.
- Shift click para seleccionar rango.
- Scrubbing avanzado.
- Deteccion asistida de frames similares.
- Presets por engine/runtime.
- Integraciones Unity/Unreal/Web.
- Packing irregular.
- Metadata expandida.
- Render profiles avanzados.
- Migracion automatica desde archivos V1.
- Export normal/depth/emissive.
- Marketplace, licensing y distribucion publica formal.
- UI altamente pulida.

## Fuera De Alcance

- Editor de pixel art.
- Editor manual de sprites.
- App externa.
- Timeline alternativo.
- Sistema de rigging.
- Editor de pivots.
- Trimming automatico.
- Eliminacion automatica de frames duplicados o similares.
- Dependencias externas obligatorias.

## Decisiones V2 Sobre Contradicciones Historicas

- `docs/archive/mvp-original.md` decia "JSON metadata" como no MVP en una seccion, pero tambien lo declaraba obligatorio para multi-clip. En V2 queda resuelto asi: JSON simple no es requisito para export individual simple, pero es obligatorio para atlas multi-clip.
- El MVP historico sugeria export multi-clip como "si es razonable". En V2 el modelo debe soportarlo desde el inicio; la ejecucion puede validarse despues del export individual, pero no debe requerir redisenar persistencia.
- La auditoria workspace-root confirmo que workspace no es una feature lateral: en V2 es raiz persistente y contiene clips, defaults y export settings. La raiz directa `Scene.spritesheet_state.clips` queda reemplazada como contrato operativo.
- V1 mezclaba modo legacy con modo workspace; V2 no mantiene compatibilidad legacy interna porque es un reinicio limpio.
- V1 basaba algunos caches en nombres visibles y escribia JSON por nombre de clip; V2 debe usar IDs/cache keys y metadata sin sobrescritura por nombres duplicados.
- La solucion V1 para Material Preview/WorldSwap queda como riesgo historico. La V2 debe investigar render nativo o viewport/OpenGL en Blender 5.x antes de fijar esa tecnica.
- Las interacciones avanzadas del selector son deseables, no bloqueantes. El MVP aceptable empieza con click toggle y acciones globales si mantiene una ruta tecnica clara a interacciones mejores.
- El addon generado previo queda fuera de la base estructural. Sus bugs informan riesgos, no patrones a copiar.

## Criterio De Termino Del MVP

El MVP termina cuando el flujo principal workspace-root puede completarse en Blender con datos persistentes, preview cacheado segun visibilidad efectiva, playback usable, export individual correcto, atlas multi-clip con JSON simple y activacion/desactivacion/reactivacion confiable.
