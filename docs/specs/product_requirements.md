# Product Requirements V2

Estado: vigente
Autoridad: derivado de `docs/specs/PROJECT_VISION.md` y `docs/archive/mvp-original.md`
Fecha: 2026-07-03

## Proposito

SpriteSheet Frame Selector V2 es un addon Blender-first para seleccionar visualmente frames de animacion 3D y exportarlos como spritesheets con baja friccion.

El producto no intenta reemplazar herramientas de pixel art, editores de spritesheets ni packers externos. Su valor principal es reducir el costo de decidir que frames de una animacion de Blender deben convertirse en spritesheet.

## Usuario Objetivo

Usuarios principales:

- technical artists;
- generalistas 3D;
- indie developers;
- artistas stylized;
- pipelines web y realtime;
- flujos de VFX flipbooks, billboards e impostors.

Usuarios no prioritarios en V2:

- pixel artists puros;
- ilustradores 2D;
- usuarios casuales sin flujo Blender;
- equipos que necesitan un runtime framework completo.

## Problema

En Blender es facil renderizar secuencias, pero es costoso evaluar visualmente que frames son utiles, descartar frames redundantes, validar timing y exportar solo lo necesario como spritesheet.

El addon debe resolver este flujo:

1. crear o configurar clips de animacion;
2. generar previews pequenos y cacheados;
3. seleccionar frames visualmente;
4. reproducir solo los frames seleccionados;
5. exportar PNG individual o atlas multi-clip cuando corresponda.

## Objetivos

- Reducir friccion en seleccion visual de frames.
- Mantener un flujo compacto dentro de Blender.
- Soportar multiples clips desde el modelo inicial.
- Permitir playback preview usando previews cacheados.
- Exportar spritesheets PNG correctos con alpha.
- Persistir estado de trabajo dentro de `.blend`.
- Ser instalable por ZIP sin dependencias externas obligatorias.
- Mantener arquitectura modular para reemplazar selector visual o composer sin rehacer el producto.

## No Objetivos

- No construir un editor de pixel art.
- No construir una app externa.
- No construir un timeline alternativo.
- No construir un sistema de rigging o animacion.
- No construir un runtime framework.
- No agregar integraciones Unity, Unreal o web en el MVP.
- No implementar packing irregular en el MVP.
- No hacer deteccion o eliminacion automatica de frames similares en el MVP.

## Prioridades De Producto

1. Estabilidad.
2. Flujo funcional completo.
3. Persistencia confiable.
4. Playback preview usable.
5. Selector visual usable.
6. Export correcto.
7. Performance.
8. Refinamiento UX.
9. Features secundarias.
10. Pulido visual.

La UI debe ser tecnica, compacta, clara y funcional. El diseno visual no debe competir con la estabilidad ni con la velocidad de iteracion.

## Requisitos De Distribucion

- Target inicial: Blender 5.x.
- Plataformas objetivo: macOS y Windows.
- Instalacion por ZIP como addon normal.
- Sin terminal para el usuario final.
- Sin dependencias externas obligatorias.
- Dependencias opcionales solo si el flujo basico sigue funcionando sin ellas.
- Paquete distribuible limpio, sin caches, pruebas temporales ni artefactos locales.

## Criterios De Exito

El primer MVP V2 se considera exitoso si permite, en una escena simple:

1. crear al menos un clip;
2. definir rango, step, camara y preview size;
3. generar previews cacheados;
4. abrir selector visual;
5. seleccionar y deseleccionar frames;
6. reproducir el clip usando solo frames seleccionados;
7. guardar y reabrir el `.blend` preservando clips y seleccion;
8. exportar PNG spritesheet individual con alpha, columnas, padding y margen;
9. exportar atlas multi-clip con metadata JSON simple;
10. activar, desactivar y reactivar el addon sin errores ni residuos de registro.

## Decisiones V2

- El producto se define por la experiencia de seleccion visual y playback, no por la composicion de PNG en si.
- Multi-clip no es un extra tardio: el modelo y el pipeline deben asumir multiples clips desde el inicio.
- JSON no es obligatorio para export individual simple, pero si es obligatorio para atlas multi-clip.
- El codigo generado previo no es base estructural de V2; solo puede consultarse como referencia historica de riesgos.
