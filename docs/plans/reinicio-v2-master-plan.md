# Reinicio V2 Master Plan

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: planificar y ejecutar por fases, sin implementar fases sin plan especifico aprobado
Estado De Ejecucion: pendiente

## Proposito

Este master plan gobierna el reinicio de `spritesheet-blender` como addon de Blender mantenible, distribuible y extensible.

El objetivo no es reparar incrementalmente el addon generado actual. El objetivo es preservar el estado actual por Git, reducir el arbol activo a documentacion/base operativa, normalizar la documentacion fuente y reconstruir el addon V2 desde una arquitectura limpia.

## Principios Operativos

- Este documento es un plan gobernante, no un plan ejecutable monolitico.
- Todo trabajo que se beneficie de precision debe tener un plan especifico antes de ejecutarse.
- Las fases y subfases no deben implementarse directamente desde este master plan.
- Cada plan especifico debe declarar objetivo, alcance, archivos afectados, pasos, riesgos, validaciones y criterio de termino.
- Las fases destructivas o sensibles requieren verificacion previa y aprobacion explicita si hay cambios no entendidos en el worktree.
- No borrar historia operativa para reducir ruido; preservar por Git antes de limpiar el arbol activo.
- No usar el codigo generado actual como base de implementacion salvo consulta puntual documentada.
- No implementar codigo del addon hasta que la documentacion V2 y la arquitectura base esten aprobadas.
- Validar no es cerrar: cada fase debe distinguir implementado, validado y listo para cierre.

## Fuentes De Verdad

- Vision de producto vigente: `docs/specs/PROJECT_VISION.md`.
- MVP historico a normalizar: `docs/specs/mvp.md`.
- Auditoria tecnica historica: `docs/archive/audit_report.md`.
- Plan gobernante V2: `docs/plans/reinicio-v2-master-plan.md`.

## Resultado Esperado

Al finalizar el reinicio V2, el proyecto debe tener:

- documentacion base clara y no contradictoria;
- arquitectura modular documentada;
- addon instalable por ZIP en Blender 5.x;
- ausencia de dependencias externas obligatorias;
- flujo MVP completo validado;
- selector visual y playback preview como capacidades centrales;
- soporte multi-clip previsto desde el modelo de datos y el pipeline de exportacion;
- pruebas automaticas y manuales adecuadas para registrar, activar, desactivar, persistir y exportar;
- paquete distribuible limpio sin residuos locales.

## Estructura De Planes Derivados

Los planes derivados deben vivir en `docs/plans/` y ser aprobados antes de ejecutarse cuando cambien estado operativo, borren o archiven archivos, creen scaffold, o implementen codigo.

Planes de fase previstos:

- `docs/plans/reinicio-v2-fase-1-preservacion.md`
- `docs/plans/reinicio-v2-fase-2-documentacion-base.md`
- `docs/plans/reinicio-v2-fase-3-limpieza-arbol-activo.md`
- `docs/plans/reinicio-v2-fase-4-scaffold-addon-v2.md`
- `docs/plans/reinicio-v2-fase-5-vertical-slices.md`
- `docs/plans/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md`
- `docs/plans/reinicio-v2-fase-7-validacion-distribucion.md`

La Fase 5 debe dividirse en subplanes porque cada vertical slice afecta diseño, Blender API, pruebas y riesgos propios:

- `docs/plans/reinicio-v2-fase-5a-data-model-persistencia.md`
- `docs/plans/reinicio-v2-fase-5b-gestion-clips.md`
- `docs/plans/reinicio-v2-fase-5c-preview-cache.md`
- `docs/plans/reinicio-v2-fase-5d-visual-selector-minimo.md`
- `docs/plans/reinicio-v2-fase-5e-playback-preview.md`
- `docs/plans/reinicio-v2-fase-5f-render-final.md`
- `docs/plans/reinicio-v2-fase-5g-composer-export.md`
- `docs/plans/reinicio-v2-fase-5h-multiclip-atlas-json.md`

Si una fase o subfase resulta demasiado amplia durante su preparacion, debe dividirse nuevamente antes de ejecutar.

## Fase 1: Preservacion Del Estado Actual

Objetivo: conservar el addon generado actual y sus residuos historicos sin mantenerlos como base activa.

Plan requerido: `docs/plans/reinicio-v2-fase-1-preservacion.md`.

Debe definir:

- revision de `git status --short --ignored`;
- estrategia exacta de rama/tag de archivo;
- manejo de cambios no commiteados existentes;
- criterio para confirmar que el estado viejo es recuperable;
- prohibicion de limpiar archivos antes de completar la preservacion.

Criterio de termino:

- existe una referencia Git recuperable para el estado previo;
- el handoff indica que el codigo viejo debe consultarse desde Git;
- no se ha limpiado ni reemplazado el arbol activo todavia.

## Fase 2: Documentacion Base V2

Objetivo: convertir la idea base en documentos operativos claros antes de reconstruir codigo.

Plan requerido: `docs/plans/reinicio-v2-fase-2-documentacion-base.md`.

Debe producir o actualizar:

- `docs/specs/product_requirements.md`;
- `docs/specs/mvp_v2.md`;
- `docs/architecture/addon_architecture.md`;
- `docs/design/visual_selector_strategy.md`;
- `docs/specs/validation_plan.md`.

Debe decidir como archivar o degradar `docs/specs/mvp.md` cuando sea reemplazado.

Criterio de termino:

- los documentos V2 son suficientes para implementar sin consultar el codigo viejo;
- las contradicciones entre vision, MVP, arquitectura y validacion estan resueltas;
- el alcance V2 declara explicitamente que no se construira editor de pixel art, suite de animacion ni app externa.

## Fase 3: Limpieza Del Arbol Activo

Objetivo: dejar el repositorio listo para reconstruccion limpia.

Plan requerido: `docs/plans/reinicio-v2-fase-3-limpieza-arbol-activo.md`.

Debe ejecutarse solo despues de completar Fase 1 y validar la preservacion Git.

Debe cubrir:

- retiro del addon generado actual;
- retiro de tests legacy si ya no son fuente operativa;
- retiro de `scratch/`, outputs, ZIP viejo, caches y residuos locales;
- actualizacion de `.gitignore` si hace falta;
- verificacion de que el arbol activo queda con documentacion, PCS y archivos base necesarios.

Criterio de termino:

- no queda codigo generado como base activa;
- el estado viejo es recuperable por Git;
- el repo no contiene residuos locales conocidos.

## Fase 4: Scaffold Limpio Del Addon V2

Objetivo: crear una base minima instalable y validable antes de features.

Plan requerido: `docs/plans/reinicio-v2-fase-4-scaffold-addon-v2.md`.

Debe definir:

- estructura de paquetes;
- manifest Blender;
- registro centralizado e idempotente;
- `register()` y `unregister()` defensivos;
- panel minimo en `3D Viewport > Sidebar > SpriteSheet`;
- pruebas minimas de import/registro cuando el entorno lo permita.

Criterio de termino:

- addon V2 existe como scaffold limpio;
- se puede activar, desactivar y reactivar;
- no hay features de producto todavia fuera de lo necesario para validar el scaffold.

## Fase 5: Implementacion Por Vertical Slices

Objetivo: construir el MVP V2 incrementalmente con planes especificos por slice.

Plan rector requerido: `docs/plans/reinicio-v2-fase-5-vertical-slices.md`.

Subplanes obligatorios:

1. Data model y persistencia.
2. Gestion de clips.
3. Preview cache.
4. Visual selector minimo.
5. Playback preview.
6. Render final.
7. Composer/export.
8. Multi-clip atlas + JSON.

Cada subplan debe incluir:

- cambios concretos de modelo o API;
- operadores y UI afectados;
- riesgos Blender API;
- comportamiento ante datos faltantes;
- pruebas automaticas posibles;
- pruebas manuales en Blender;
- criterio para continuar al siguiente slice.

Criterio de termino:

- cada slice esta implementado y validado antes del siguiente;
- no se agregan features fuera de `docs/specs/mvp_v2.md`;
- playback preview y multi-clip no quedan como extensiones improvisadas.

## Fase 6: Correcciones Auditoria Tecnica

Objetivo: corregir o clasificar formalmente los hallazgos de la auditoria tecnica post-Fase 5 antes de preparar distribucion.

Plan requerido: `docs/plans/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md`.

Debe cubrir:

- selector modal y lifecycle runtime;
- output correctness de previews/render/export;
- decision explicita sobre render cache final;
- rendimiento/memoria de composer/export;
- validacion, registro y deuda tecnica detectada;
- verificacion runtime de puntos no confirmados por la auditoria estatica.

El plan de Fase 6 es rector. No debe ejecutarse como monolito si la correccion se beneficia de subplanes especificos.

Criterio de termino:

- todos los hallazgos C/A/M/B de `docs/technical-audit.md` estan corregidos, diferidos con razon o clasificados como no aplicables con evidencia;
- los hallazgos criticos y altos no quedan diferidos salvo decision explicita del usuario;
- las validaciones automaticas y runtime aplicables pasan o tienen limitacion documentada;
- Fase 7 queda habilitada como validacion/distribucion final.

## Fase 7: Validacion Final Y Distribucion

Objetivo: preparar el addon V2 para uso distribuible.

Plan requerido: `docs/plans/reinicio-v2-fase-7-validacion-distribucion.md`.

Debe cubrir:

- matriz de validacion manual en Blender 5.x;
- activar/desactivar/reactivar;
- archivo nuevo;
- cambio de escena;
- camara faltante o borrada;
- coleccion faltante o borrada;
- persistencia en `.blend`;
- export PNG con alpha;
- export atlas multi-clip con JSON;
- generacion de ZIP limpio;
- instrucciones de instalacion y uso;
- notas de limitaciones.

Criterio de termino:

- el ZIP instalable contiene solo archivos necesarios;
- el flujo MVP completo esta validado;
- PCS refleja el estado final sin marcar cerrado salvo instruccion explicita del usuario.

## Proximo Paso Operativo

Crear el plan especifico `docs/plans/reinicio-v2-fase-1-preservacion.md`.

Ese plan debe ser detallado y decision-complete antes de ejecutar cualquier preservacion, tag, rama, commit o limpieza.
