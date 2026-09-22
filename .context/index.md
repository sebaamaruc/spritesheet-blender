# Context Index

Ultima actualizacion: 2026-07-08

## Lectura Minima

Leer siempre:

1. `AGENTS.md`
2. `.context/agent_context.md`
3. `.context/index.md`

## Documentos Operativos

| Documento | Cuando leerlo | Estado | Vigencia | Confianza |
|---|---|---|---|---|
| `AGENTS.md` | Al iniciar cualquier sesion para comprender las reglas operativas de IA | lectura_obligatoria | vigente | alta |
| `.context/agent_context.md` | Al iniciar cualquier sesion para conocer el estado y la tarea activa | activo | vigente | alta |
| `.context/handoff.md` | Al continuar trabajo pendiente o cambiar de agente | activo | vigente | alta |
| `.context/decisions.md` | Antes de cambiar reglas, arquitectura o convenciones | activo | vigente | alta |
| `.context/worklog.jsonl` | Solo para auditoria o reconstruccion historica | append-only | vigente | alta |
| `.context/manifest.json` | Para auditoria de version y estructura PCS | activo | vigente | alta |

## Planes Activos y Rectores

| Documento | Cuando leerlo | Estado | Vigencia | Confianza |
|---|---|---|---|---|
| `docs/plans/reinicio-v2-master-plan.md` | Siempre antes de planificar o ejecutar cualquier trabajo del reinicio V2 | aprobado | vigente | alta |

## Planes de Subfases Validados

| Documento | Cuando leerlo | Estado | Vigencia | Confianza |
|---|---|---|---|---|
| `docs/archive/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md` | Plan rector para corregir o clasificar todos los hallazgos de `docs/technical-audit.md` | cerrado | vigente | alta |
| `docs/archive/reinicio-v2-fase-6a-selector-modal-lifecycle.md` | Hito 1 validado: C1, C2 y B5 modal/lifecycle | validado | vigente | alta |
| `docs/archive/reinicio-v2-fase-6a-validacion-hito1-selector-modal-lifecycle.md` | Validacion de hito 1 modal/lifecycle | validado | vigente | alta |
| `docs/archive/reinicio-v2-fase-6a-hito2-selector-playback-integridad.md` | Hito 2 validado: integridad selector/playback | validado | vigente | alta |
| `docs/archive/reinicio-v2-fase-6a-hito3-selector-scroll.md` | Hito 3 validado: M6 scroll del selector | validado | vigente | alta |
| `docs/archive/reinicio-v2-fase-6b0-preview-camera-viewport.md` | Previews usan camara efectiva desde Viewport | validado | vigente | alta |
| `docs/archive/reinicio-v2-fase-6b-preview-alpha-estado-visual.md` | Hito de previews, alpha y estado visual | validado | vigente | alta |
| `docs/archive/reinicio-v2-fase-6c-render-cache-final.md` | Eliminacion de render cache final e integracion MVP | validado | vigente | alta |
| `docs/archive/reinicio-v2-fase-6d-rendimiento-export.md` | Plan de rendimiento, memoria y seguridad de export | cerrado | vigente | alta |
| `docs/archive/reinicio-v2-fase-6e-consolidacion-higiene.md` | Plan de consolidacion, registro e higiene tecnica | cerrado | vigente | alta |
| `docs/archive/reinicio-v2-fase-6f-verificacion-integral-auditoria.md` | Plan de verificacion integral de auditoria | cerrado | vigente | alta |

## Planes Validados Pendientes De Cierre

| Documento | Cuando leerlo | Estado | Vigencia | Confianza |
|---|---|---|---|---|
| `docs/plans/reinicio-v2-fase-7-validacion-distribucion.md` | Resultado validado de packaging y distribucion; conservar activo hasta cierre explicito | validado | vigente | alta |

## Especificaciones

| Documento | Cuando leerlo | Estado | Vigencia | Confianza |
|---|---|---|---|---|
| `docs/technical-audit.md` | Antes de planificar o ejecutar Fase 6; fuente de hallazgos tecnicos C/A/M/B | auditoria_tecnica | vigente | alta |
| `docs/specs/PROJECT_VISION.md` | Para entender la filosofia de UX, workflow de multi-clips y playbacks | activo | vigente | alta |
| `docs/specs/product_requirements.md` | Para entender producto, usuario objetivo, objetivos, no objetivos y criterios de exito V2 | activo | vigente | alta |
| `docs/specs/mvp_v2.md` | Para planificar e implementar alcance MVP V2 | activo | vigente | alta |
| `docs/specs/validation_plan.md` | Para definir validaciones automaticas y manuales por fase | activo | vigente | alta |
| `docs/specs/workspace_root_decisions.md` | Antes de actualizar docs V2 o replanificar Fase 5 con workspace como raiz | activo | vigente | alta |
| `docs/specs/workspace_root_refactor_evaluation.md` | Antes de replanificar Fase 5 workspace-root; contiene decision refactor vs reinicio | activo | vigente | alta |
| `docs/specs/selector_modal_preview_modes_spike.md` | Antes de crear o implementar 5e1 selector/playback UX | activo | vigente | alta |
| `docs/specs/mvp.md` | Para ubicar la referencia historica al MVP original archivado | historico | stale | alta |

## Arquitectura

| Documento | Cuando leerlo | Estado | Vigencia | Confianza |
|---|---|---|---|---|
| `docs/architecture/addon_architecture.md` | Antes de crear scaffold o implementar slices V2 | activo | vigente | alta |

## Diseno

| Documento | Cuando leerlo | Estado | Vigencia | Confianza |
|---|---|---|---|---|
| `docs/design/visual_selector_strategy.md` | Antes de planificar selector visual o playback preview | activo | vigente | alta |

## Codigo

| Documento | Cuando leerlo | Estado | Vigencia | Confianza |
|---|---|---|---|---|
| `spritesheet_frame_selector/` | Scaffold minimo del addon V2; leer antes de planificar slices de implementacion | scaffold | vigente | media |

## Archivo

Los documentos cerrados, reemplazados u obsoletos viven en `docs/archive/`.

## Planes Activos

| Documento | Cuando leerlo | Estado | Vigencia | Confianza |
|---|---|---|---|---|
| `docs/plans/reinicio-v2-fase-7-validacion-distribucion.md` | Plan activo para continuar la tarea actual | activo | vigente | alta |
| `docs/plans/reinicio-v2-master-plan.md` | Plan activo para continuar la tarea actual | activo | vigente | alta |
