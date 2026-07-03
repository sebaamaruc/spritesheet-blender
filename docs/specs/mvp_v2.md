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

1. El usuario crea o selecciona un clip.
2. Define `frame_start`, `frame_end`, `frame_step`, FPS, preview size y camara.
3. Genera o refresca previews cacheados.
4. Abre el selector visual.
5. Selecciona o deselecciona frames.
6. Reproduce el resultado con playback preview.
7. Configura export.
8. Exporta el clip individual como spritesheet PNG.
9. Exporta multiples clips como atlas cuando lo necesite, con JSON simple.

## Obligatorio Para MVP V2

### Modelo Y Persistencia

- Multiples clips en el modelo desde el inicio.
- Estado persistente en `.blend`.
- Clip con nombre, rango, step, FPS, camara opcional, preview size, frames, seleccion y estado de cache.
- Export settings persistentes con frame width, frame height, columns, padding, margin, transparencia, output folder, sheet name y opcion de PNG sequence apagada por defecto.
- Indices activos con validacion de bounds.
- Nombres de clip manejados de forma estable para evitar colisiones en cache y metadata.

### UI Principal

- Panel en `3D Viewport > Sidebar > SpriteSheet`.
- Lista de clips.
- Configuracion del clip activo.
- Controles de preview.
- Resumen de seleccion.
- Configuracion de export.
- Warnings claros.
- Contadores de total de frames, previews generados, frames seleccionados, rows estimadas y resolucion estimada.

### Preview

- Generacion de previews pequenos y cacheados.
- Preview size custom desde el inicio.
- Presets 32, 64 y 128.
- Boton `Generate Preview`.
- Boton `Refresh Preview`.
- Boton `Clear Preview Cache`.
- Warning simple cuando el cache pueda estar desactualizado.
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
- El JSON debe incluir sheet, frameWidth, frameHeight, columns y clips con start, end, count y FPS opcional.
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
- Las interacciones avanzadas del selector son deseables, no bloqueantes. El MVP aceptable empieza con click toggle y acciones globales si mantiene una ruta tecnica clara a interacciones mejores.
- El addon generado previo queda fuera de la base estructural. Sus bugs informan riesgos, no patrones a copiar.

## Criterio De Termino Del MVP

El MVP termina cuando el flujo principal puede completarse en Blender con datos persistentes, preview cacheado, playback usable, export individual correcto, atlas multi-clip con JSON simple y activacion/desactivacion/reactivacion confiable.
