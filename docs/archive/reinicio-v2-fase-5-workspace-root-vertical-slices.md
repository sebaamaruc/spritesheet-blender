# Reinicio V2 Fase 5 Workspace-Root: Implementacion Por Vertical Slices

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar por subplanes aprobados
Estado De Ejecucion: pendiente

## Referencia Superior

`docs/plans/reinicio-v2-master-plan.md`

## Reemplaza

Este plan reemplaza operativamente el orden original de `docs/plans/reinicio-v2-fase-5-vertical-slices.md` para las slices 5a/5b/5c.

Motivo:

- `DEC-0006`: workspace es raiz de dominio en V2.
- `DEC-0007`: los documentos V2 ya declaran workspace-root como contrato operativo.
- `DEC-0009`: se decidio rehacer Fase 5 desde el scaffold limpio de Fase 4 para workspace-root.

Los planes anteriores `docs/archive/reinicio-v2-fase-5a-data-model-persistencia.md`, `docs/archive/reinicio-v2-fase-5b-gestion-clips.md` y `docs/archive/reinicio-v2-fase-5c-preview-cache.md` se preservan como historial validado, pero no son base arquitectonica vigente.

## Objetivo

Reconstruir el MVP V2 desde el scaffold limpio de Fase 4 usando workspace como raiz de dominio, por slices pequenas, validables y mantenibles.

La implementacion debe partir desde el estado conceptual de Fase 4, no desde el modelo 5a/5b/5c antiguo basado en `Scene.spritesheet_state.clips`.

## Fuentes Operativas

- `docs/specs/mvp_v2.md`
- `docs/architecture/addon_architecture.md`
- `docs/specs/validation_plan.md`
- `docs/specs/workspace_root_decisions.md`
- `docs/specs/workspace_root_refactor_evaluation.md`
- `docs/design/visual_selector_strategy.md`
- `docs/plans/reinicio-v2-fase-4-scaffold-addon-v2.md`

## Regla De Base

La reconstruccion workspace-root debe tratar el commit `77bda46 reinicio v2 docs cleanup scaffold` como referencia conceptual de scaffold limpio.

No se debe ejecutar un `git reset` destructivo sin instruccion explicita del usuario. En implementaciones futuras, el plan de cada slice debe decidir si:

- reemplaza archivos actuales para volver efectivamente al scaffold y luego agrega la slice;
- o aplica cambios manuales equivalentes al scaffold limpio usando `apply_patch`.

En ambos casos, no se debe mantener compatibilidad temporal con `Scene.spritesheet_state.clips`.

## Piezas Que Se Pueden Reaprovechar

- Helpers puros:
  - `spritesheet_frame_selector/core/frame_math.py`
  - `spritesheet_frame_selector/core/frame_sync.py`
- Patrones:
  - registro centralizado defensivo;
  - ids estables;
  - cache que no depende de nombres visibles;
  - clear cache que preserva frames y seleccion;
  - tests unitarios para helpers puros cuando sigan representando el contrato.

Reaprovechar no significa copiar la arquitectura antigua. Todo helper debe revisarse contra workspace-root antes de conservarse.

## Orden De Subplanes Workspace-Root

### 5a: Workspace Data Model Y Persistencia

Plan ejecutado, validado y archivado: `docs/archive/reinicio-v2-fase-5a-workspace-data-model-persistencia.md`.

Objetivo:

- Crear el modelo persistente workspace-root.
- Dejar `Scene.spritesheet_state.workspaces -> active_workspace -> clips -> frames`.
- Validar persistencia save/reopen en Blender.

Criterio de salida:

- El addon registra/desregistra limpiamente.
- Se pueden crear workspaces, defaults, clips, frames y export settings por Python.
- Los datos sobreviven save/reopen.
- No hay operadores de producto fuera del alcance.

### 5b: Workspace Y Clip Management

Plan ejecutado, validado y archivado: `docs/archive/reinicio-v2-fase-5b-workspace-clip-management.md`.

Objetivo:

- Gestionar workspaces y clips desde UI nativa.
- Agregar operadores add/remove/duplicate/select/reorder para workspaces y clips.
- Configurar default camera/default collections de workspace y overrides basicos por clip.

Criterio de salida:

- El usuario puede administrar workspaces y clips desde el panel.
- La duplicacion de workspace genera ids nuevos y no conserva cache como valido.
- Cambio de escena no mezcla workspaces.

### 5c: Preview Cache Workspace-Aware

Plan ejecutado, validado y archivado: `docs/archive/reinicio-v2-fase-5c-workspace-preview-cache.md`.

Objetivo:

- Implementar preview cache usando workspace + clip.
- Resolver camera efectiva y collections efectivas.
- Aplicar/restaurar visibilidad por collections.
- Cache por workspace id, clip id y cache key.

Criterio de salida:

- Generate/Refresh/Clear Preview funcionan sobre clip activo del workspace activo.
- Preview respeta camera y collections efectivas.
- Clear cache no destruye seleccion persistente.

### 5c-spike: Investigacion Preview/Render Nativo

Plan futuro opcional: `docs/plans/reinicio-v2-fase-5c-spike-render-preview-nativo.md`.

Objetivo:

- Probar en Blender 5.x si conviene OpenGL viewport, render still nativo Workbench/EEVEE Next o fallback background.
- Evitar reintroducir WorldSwap sin evidencia.

Este spike puede ejecutarse antes de 5c o como precondicion tecnica de 5c.

### 5d: Visual Selector Minimo

Plan ejecutado, validado y archivado: `docs/archive/reinicio-v2-fase-5d-visual-selector-minimo.md`.

Objetivo:

- Consumir previews existentes del clip activo.
- Mostrar grilla/contact sheet visual.
- Permitir seleccion y acciones globales.

Criterio de salida:

- El selector abre desde el panel.
- La seleccion persiste.
- No genera previews, playback, render ni export.

### 5e: Playback Preview

Plan ejecutado, validado y archivado: `docs/archive/reinicio-v2-fase-5e-playback-preview.md`.

Objetivo:

- Reproducir previews cacheados de frames seleccionados del clip activo.
- Respetar FPS del clip.
- Mantener estado runtime fuera del `.blend`.
- Limpiar timers al detener, cerrar o desregistrar.

Criterio de salida:

- Play/Pause/Stop funcionan sobre workspace/clip activo.
- Playback usa solo previews existentes.
- La seleccion persistente no cambia durante playback.
- No se implementa render, composer ni export.

### 5f: Render Final Workspace-Aware

Plan ejecutado y archivado: `docs/archive/reinicio-v2-fase-5f-render-final-workspace-aware.md`.

### 5e1: Correccion UX Selector/Playback

Plan ejecutado, validado y archivado antes de 5f: `docs/archive/reinicio-v2-fase-5e1-selector-playback-ux.md`.

Precedente tecnico validado:

- `docs/archive/reinicio-v2-fase-5e1-spike-selector-modal-preview-modes.md`
- `docs/specs/selector_modal_preview_modes_spike.md`

Objetivo:

- Reemplazar o evolucionar el selector hacia superficie modal/custom.
- Agregar visor grande de playback.
- Persistir `selector_mode` en `.blend`.
- Agregar preview modes y presets de tamano.

Criterio de salida:

- Selector/playback quedan usables para inspeccion visual real antes de render/export.
- No se avanza a render final hasta validar esta correccion.

## Reglas Generales

- No copiar codigo V1 como base estructural.
- No mantener modelo dual legacy/workspace.
- No implementar mas de un slice por plan aprobado.
- Cada slice debe dejar el addon importable y registrable.
- Cada slice debe ejecutar validaciones automaticas posibles y Blender background si aplica.
- Si una validacion falla, no avanzar al siguiente slice.
- No crear ZIP distribuible hasta Fase 6 salvo prueba manual puntual ignorada por `.gitignore`.

## Criterio De Termino De Este Plan Rector

La Fase 5 workspace-root queda lista para continuar hacia selector visual cuando:

- nuevo 5a workspace-root esta validado;
- nuevo 5b workspace/clip management esta validado;
- nuevo 5c preview cache workspace-aware esta validado;
- se resolvio la investigacion preview/render nativo necesaria;
- no queda dependencia activa de `Scene.spritesheet_state.clips`.

## Proximo Paso

Fase 5 workspace-root quedo ejecutada hasta 5g; el siguiente plan operativo propuesto es `docs/plans/reinicio-v2-fase-6-validacion-distribucion.md`.
