# Agent Context

PCS-Version: 1
PCS-Template-Version: 1.1.0
Ultima actualizacion: 2026-07-14
Actualizado por: pcs

## Resumen Actual

El usuario decidio reiniciar `spritesheet-blender` como addon V2 mantenible, distribuible y extensible. El addon generado actual no debe repararse incrementalmente como base principal. Debe preservarse por Git, normalizarse la documentacion base y reconstruirse desde una arquitectura limpia.

El plan gobernante aprobado es `docs/plans/reinicio-v2-master-plan.md`. Este master plan no es ejecutable de forma monolitica: cada fase o subfase que se beneficie de precision debe tener un plan especifico aprobado antes de ejecutarse.

## Tarea Activa

Revisar y aprobar el plan de la Fase 7 para realizar la validación final en Blender GUI, empaquetado y distribución. La Fase 6 (Correcciones de Auditoría Técnica) ha sido implementada y archivada.

## Proximo Paso Recomendado

Obtener la aprobación del usuario para el plan `docs/plans/reinicio-v2-fase-7-validacion-distribucion.md` para iniciar las pruebas en Blender GUI, limpieza y empaquetado.

## Estado

- Fase 6 (Correcciones de Auditoria Tecnica): implementada y cerrada (archivada).
- Fase 7 (Validacion final y distribucion): plan propuesto y listo para aprobacion.
- Ejecucion de reinicio V2: pendiente de aprobacion de Fase 7.

## Archivos Relevantes Ahora

- `docs/plans/reinicio-v2-master-plan.md`
- `docs/plans/reinicio-v2-fase-7-validacion-distribucion.md`
- `docs/specs/mvp_v2.md`

## Plan Activo

Ninguno

## Decisiones Vigentes Relevantes

- `DEC-0001`: PCS persiste contexto operativo en el repositorio.
- Reinicio V2: preservar estado actual por Git, limpiar el arbol activo despues de preservacion, reconstruir desde documentacion y arquitectura V2.
- Los planes de fase/subfase son los unicos ejecutables; el master plan gobierna orden, restricciones y criterios.
- Fase 2: `docs/specs/mvp.md` quedo historico/no operativo; el contrato vigente de producto y MVP vive en los documentos V2.
- Fase 3: el addon V1, tests legacy, scratch y residuos locales fueron retirados del arbol activo; el estado V1 solo debe consultarse desde Git/archive si hace falta.
- Fase 4: existe scaffold V2 minimo; no contiene features de producto fuera del lifecycle basico.
- Fase 5a: existe modelo persistente V2 con clips, frames, export settings y estado de escena.
- Fase 5b: existe gestion basica de clips con operadores Add/Remove/Duplicate/Select, UIList nativa, panel de edicion del clip activo, helpers puros de estado y tests unitarios.
- Fase 5c: existe preview cache por clip con Generate/Refresh/Clear, cache key estable, paths administrados y persistencia de seleccion validada en Blender background.
- Fase 5e: existe playback preview runtime sobre previews cacheados y seleccion persistente, con Play/Pause/Stop, timer unico y cleanup en unregister.
- Fase 5a/5b/5c originales se conservan como historial validado, pero fueron reemplazadas como base vigente por workspace-root.
- Fase 5a workspace-root: modelo persistente validado con `Scene.spritesheet_state.workspaces`.
- DEC-0006: workspace es raiz de dominio en V2; 5a/5b/5c quedan sujetos a revision antes de continuar con selector visual.
- DEC-0007: docs V2 ya declaran workspace-root como contrato operativo.
- DEC-0008: preview/render/export deben resolver camara y collections efectivas desde workspace + clip.
- DEC-0009: rehacer Fase 5 desde scaffold para workspace-root.
- DEC-0010: antes de render final se debe corregir selector/playback con superficie modal/custom, `selector_mode` persistente y preview modes persistentes.
- Fase 6 D1: eliminar el subsistema de render cache final para MVP.
- Fase 6 D2: prohibir frames negativos en MVP agregando `min=0` a `frame_start`/`frame_end`.
- Fase 6b0: previews `SOLID`/`MATERIAL` deben forzar temporalmente Camera View del `VIEW_3D` usado por `render.opengl(view_context=True)` para respetar la camara efectiva sin perder el shading de viewport.

## Riesgos Abiertos

- Fase 7 puede descubrir bugs de packaging/lifecycle que requieran correcciones menores antes de distribuir.
- Blender background dentro del sandbox crashea antes de ejecutar Python; fuera del sandbox fue rechazado por politica del entorno actual en validaciones previas.
- La limpieza automatica de `__pycache__` generados por validacion fue rechazada por politica del entorno; no se intento una via alternativa.

## Bloqueos

Ninguno detectado.

## Validaciones Pendientes

- Aprobar e iniciar el plan de la Fase 7 (`docs/plans/reinicio-v2-fase-7-validacion-distribucion.md`) para proceder con la validación GUI integral y la distribución final.
