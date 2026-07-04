# Estrategia Del Selector Visual V2

Estado: vigente
Autoridad: derivado de `docs/specs/product_requirements.md` y `docs/specs/mvp_v2.md`
Fecha: 2026-07-03

## Principio UX

El selector visual es el diferenciador del producto. Debe ayudar al usuario a decidir rapido que frames conservar, validar timing con playback y volver a exportar sin friccion.

La primera version debe ser robusta antes que sofisticada. Una grilla simple, clara y estable es preferible a un modal avanzado que filtre handlers, falle al cerrar o degrade Blender.

## Experiencia Objetivo

1. El usuario elige un workspace y un clip dentro de ese workspace.
2. Genera previews usando la camara efectiva y collections efectivas del workspace + clip.
3. Abre un selector mas amplio que el sidebar.
4. Ve una grilla de thumbnails con numeros de frame.
5. Selecciona o deselecciona frames.
6. Presiona Play y ve solo los frames seleccionados.
7. Ajusta la seleccion.
8. Cierra el selector sin perder estado.
9. Exporta desde el sidebar usando la inclusion y orden del workspace activo.

## Selector Minimo Aceptable

- Grid/contact sheet de previews cacheados.
- Celda con thumbnail.
- Numero de frame visible.
- Estado seleccionado con borde u overlay claro.
- Estado no seleccionado atenuado.
- Click toggle.
- Select All.
- Deselect All.
- Invert Selection.
- Select Every N Frames.
- Contador visible de seleccion.
- Mensaje claro si faltan previews.
- Nombre del workspace activo visible o disponible en el contexto del selector.
- Nombre del clip activo visible.
- Warning claro si el clip activo no tiene camara efectiva o collections efectivas.
- Cierre confiable con ESC, boton de cerrar y RIGHTMOUSE si aplica.

## Playback Preview

Playback es core, no polish.

Requisitos:

- Reproduce frames seleccionados en orden temporal.
- Usa thumbnails/previews ya generados.
- No renderiza durante playback.
- Tiene Play, Pause y Stop.
- Respeta FPS del clip.
- Puede hacer loop.
- Detiene timers al cerrar o cambiar estado.
- No bloquea el cierre del modal.

El playback puede vivir dentro del selector o abrirse en un popup simple. La decision concreta se toma en el plan de implementacion del slice correspondiente, pero la arquitectura debe permitir reemplazar la superficie visual sin cambiar persistencia ni export.

## Interacciones Diferidas

Estas interacciones son deseables pero no deben bloquear la primera version estable:

- drag para pintar seleccion;
- ctrl drag para pintar deseleccion;
- box select/marquee;
- shift click para rango;
- hover avanzado;
- scrubbing;
- zoom y pan sofisticados;
- shortcuts extensos.

Orden recomendado:

1. click toggle;
2. acciones globales;
3. playback;
4. drag select;
5. shift range;
6. box select.

## Fallback Aceptable

Si la API de Blender dificulta una grilla modal robusta en el primer slice, se permite un fallback temporal con UI nativa siempre que:

- muestre thumbnails o una contact sheet visual;
- permita seleccionar frames sin depender de una lista textual pura;
- mantenga persistencia y playback;
- deje una ruta tecnica clara hacia una grilla mejor.

No es aceptable como resultado final del MVP un selector solo textual sin ruta visual.

## Reglas Tecnicas Del Selector

- El selector consume datos de clip y preview; no calcula ni renderiza previews.
- El selector recibe workspace y clip activos de forma explicita. No debe buscar una lista global de clips en `Scene`.
- La seleccion se escribe en el modelo persistente.
- La carga de imagenes debe tolerar archivos faltantes.
- El modal debe prevenir doble invocacion.
- Draw handlers, timers, images y recursos GPU deben limpiarse al cerrar.
- Cambios de estado GPU deben protegerse con `try/finally`.
- El layout visible puede cachearse y recalcularse solo cuando cambien tamaño, scroll, zoom o cantidad de frames.
- El selector no debe crear directorios ni modificar settings de render.
- Cambiar de workspace o clip mientras el selector esta abierto debe cerrar o invalidar el selector de forma controlada, sin escribir seleccion en el clip equivocado.

## Estados Visuales

- Seleccionado: borde u overlay claro.
- No seleccionado: atenuado.
- Hover: opcional.
- Preview faltante: placeholder tecnico simple.
- Cache posiblemente desactualizado: warning visible, sin bloqueo.
- Clip activo: nombre visible.
- Workspace activo: nombre visible o contexto claro.
- Playback activo: indicador simple y frame actual resaltado.

## Criterio De Termino Del Selector MVP

El selector minimo queda terminado cuando permite abrir, ver previews, seleccionar frames con click y acciones globales, reproducir seleccion, cerrar sin fugas conocidas y conservar estado al guardar/reabrir `.blend`.
