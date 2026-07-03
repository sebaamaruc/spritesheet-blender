# Proposed Project Goals

## Síntesis de Visión Global

*   **Producto Completo / Visión Final:** Addon de Blender 5.x ("SpriteSheet Frame Selector") enfocado en pipelines de producción para videojuegos, web y VFX. Permite seleccionar visualmente frames de animaciones 3D, previsualizarlos en loop usando un reproductor liviano basado en caché de imágenes y exportarlos optimizados a una hoja de sprites (PNG) acompañada de un archivo de metadatos JSON para múltiples clips/animaciones.
*   **MVP o Etapa Actual:** Workspace V1 implementado y estabilizado, habiéndose resuelto los fallos de la auditoría técnica post-Workspace V1 (caching de cámara, TypeErrors en poll de UI e indexación de workspace).
*   **Capacidades Internas Necesarias:** Motor de composición de imágenes NumPy interno para generar las hojas de sprites a partir de buffers y sistema de persistencia en el archivo `.blend`.
*   **Estado Implementado:** Arquitectura de datos multi-clip persistente en el archivo `.blend`, panel lateral de UI para gestionar propiedades del exportador, visor modal básico e interactivo de celdas de frames y cobertura de tests de integración para renderizado y visibilidad.
*   **Pendientes, Deuda o Riesgos:** Estabilización de rendimiento GPU en el selector visual (recreación innecesaria de shaders/batches por frame), fugas de timers en el playback preview al conmutar rápido, e incompatibilidades del renderizador con EEVEE Next en Blender 5.x (samples no optimizados).

## Tabla de Metas

| Meta | Grupo | Estado | Fuente | Evidencia | Planes | Decisiones |
|---|---|---|---|---|---|---|
| **Selección Visual de Frames:** Interactuar mediante una grilla/contact sheet con celdas de frames, permitiendo conmutar su estado de selección y persistirlo en el archivo `.blend`. | Producto Completo | implementado | `docs/specs/mvp.md` | `spritesheet_frame_selector/visual_selector.py` L172-192 | | `DEC-0003` |
| **Playback Preview:** Reproducir en loop la secuencia animada resultante usando únicamente los frames seleccionados a un valor de FPS ajustable de manera fluida y liviana. | Producto Completo | implementado | `docs/specs/mvp.md` y `docs/specs/PROJECT_VISION.md` | `spritesheet_frame_selector/visual_selector.py` L718-743 | | |
| **Workspace Multi-Clip (Workspace V1):** Organizar múltiples clips animados ordenados en una lista para exportarse conjuntamente en un único atlas o spritesheet con parámetros específicos. | MVP Actual | validado | `docs/specs/mvp.md` y `docs/archive/implementation_plan.md` | `tests/test_integration_render.py` y `spritesheet_frame_selector/properties.py` | | `DEC-0002` |
| **Composición de Spritesheets con NumPy:** Generar la hoja de sprites final de forma veloz procesando arrays multidimensionales en memoria, respetando alpha, márgenes, padding y columnas. | Pipeline / Herramientas | validado | `docs/specs/mvp.md` | `spritesheet_frame_selector/composer_numpy.py` y `tests/test_composer.py` | | |
| **Metadatos JSON para Atlas Multi-Clip:** Exportar automáticamente un archivo JSON con la correspondencia de clips, cantidad de frames, índices iniciales/finales y dimensiones de celdas para su integración en runtime. | Producto Completo | validado | `docs/specs/mvp.md` y `docs/specs/PROJECT_VISION.md` | `spritesheet_frame_selector/exporter.py` y `tests/test_exporter.py` | | |
| **Compatibilidad con EEVEE Next (Blender 5.x):** Adaptar el contexto de renderizado a la API de EEVEE Next (`BLENDER_EEVEE_NEXT`) optimizando los samples en Material Preview para evitar demoras innecesarias. | Pipeline / Herramientas | pendiente | `docs/archive/audit_report.md` | `spritesheet_frame_selector/utils.py` L374 | | |
| **Optimización de Dibujo GPU en Selector Visual:** Cachear la carga de shaders (`UNIFORM_COLOR`) e inicialización de batches de renderizado para evitar recargas constantes y degradación de rendimiento. | Pipeline / Herramientas | pendiente | `docs/archive/audit_report.md` | `spritesheet_frame_selector/visual_selector.py` L205-213 | | |

## Notas de Revisión

### Decisiones de Alcance y Exclusiones (Fuera de MVP / Denominador de progreso)
Los siguientes elementos descritos en los documentos de especificación original se han catalogado explícitamente fuera del alcance del MVP y no se contabilizan en el progreso del proyecto:
1.  **Trimming Automático de Bordes Transparentes:** Excluido del MVP para evitar sobrecomplicación matemática.
2.  **Deduplicación Automática de Frames Parecidos:** Solo se prevé mostrar una advertencia o visualización manual al usuario si se implementa a futuro; nunca se eliminarán celdas de forma automatizada.
3.  **Editor de Pivotes / Anclajes de Frames (Pivot Editor):** Funcionalidad pospuesta para versiones avanzadas post-MVP.
4.  **Onion Skinning (Papel de cebolla):** Excluido del visor interactivo para mantener la interfaz ligera y simple.
5.  **Empaquetado Irregular (Irregular/Polygon Packing):** El empaquetado del atlas se limitará a grillas rectangulares (columnas y filas auto-calculadas).
6.  **Integraciones de Runtimes Propios (Unity/Unreal/Web plugins):** La responsabilidad del addon finaliza en la entrega de la hoja PNG y la estructura JSON de metadatos.
