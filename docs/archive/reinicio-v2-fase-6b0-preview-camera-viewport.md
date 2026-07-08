# Plan Fase 6b0 - Preview Desde Camara Efectiva

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: validado

## Referencia Superior

`docs/plans/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md`

## Objetivo

Corregir el bug runtime detectado por el usuario: `Generate Preview` en `SOLID`/`MATERIAL` generaba thumbnails desde la vista libre del viewport cuando el usuario no habia entrado manualmente a Camera View, por lo que el objeto aparecia muy pequeno aunque la camara efectiva estuviera bien configurada.

Este bug no aparece como hallazgo explicito en `docs/technical-audit.md`. Se registra como correccion runtime nueva asociada a Fase 6b porque afecta la exactitud y confiabilidad de previews, y bloquea la validacion practica del selector visual.

## Hallazgos De Auditoria Cubiertos

| ID | Severidad | Titulo | Estado En Este Subplan |
|---|---|---|---|
| P1-preview-camera-view | alto runtime | `Generate Preview` no fuerza Camera View para OpenGL viewport previews | validado por el usuario en Blender GUI |

## Extracto Operativo Del Hallazgo Runtime

### P1-preview-camera-view - Generate Preview no fuerza Camera View

- Problema: `Generate Preview` con solo seleccionar collection y camara puede generar un preview con el objeto muy pequeno. El comportamiento se corrige temporalmente si el usuario entra manualmente a Camera View antes de generar previews.
- Causa: `spritesheet_frame_selector/preview/generator.py::_write_viewport_thumbnail` usa `bpy.ops.render.opengl(write_still=True, view_context=True)`. Blender define `view_context=True` como uso del viewport 3D actual; si ese viewport esta en perspectiva libre, el render OpenGL no usa el encuadre de la camara efectiva.
- Impacto: thumbnails falsos o inconsistentes; el selector visual muestra datos incorrectos aunque la camara efectiva sea correcta.
- Solucion propuesta: mantener `view_context=True` para conservar el contrato `SOLID`/`MATERIAL` basado en shading de viewport, pero forzar temporalmente `region_3d.view_perspective = "CAMERA"` durante el render OpenGL y restaurar la perspectiva previa con `try/finally`.
- Archivos/funciones afectados: `spritesheet_frame_selector/preview/generator.py::ViewportRenderContext`, `_viewport_context_from_area`, `_write_viewport_thumbnail`; `tests/test_preview_cache.py`.
- Aspectos no verificados en runtime: ninguno para este subplan; validado por el usuario en Blender GUI.

## Interpretacion Del Subplan

- Decision: ajustar la ruta OpenGL de previews, no cambiar a `view_context=False`.
- Argumento: `view_context=False` usaria settings de escena, pero perderia el contrato visual de `SOLID`/`MATERIAL` que depende del shading del viewport. Forzar Camera View conserva ambas cosas: shading de viewport y encuadre de camara efectiva.
- Riesgos: en contextos sin `RegionView3D`, la ruta `SOLID`/`MATERIAL` debe fallar con mensaje claro en vez de producir un preview engañoso.
- Dependencias con otros hallazgos: no cierra A4, M1, M2, B9 ni B11; solo desbloquea la confiabilidad basica del encuadre de previews.

## Alcance De Implementacion

- Incluir:
  - extender `ViewportRenderContext` con `region_3d`;
  - forzar Camera View durante `bpy.ops.render.opengl(..., view_context=True)`;
  - restaurar perspectiva, shading y overlays tras exito o error;
  - test unitario de Camera View temporal y restauracion;
  - test unitario de fallo controlado sin `RegionView3D`.
- Excluir:
  - regeneracion forzada o invalidacion por depsgraph;
  - cambios de cache key;
  - cambios de alpha/transparencia;
  - progress UI;
  - scroll/selector/playback.
- Archivos esperados:
  - `spritesheet_frame_selector/preview/generator.py`;
  - `tests/test_preview_cache.py`.

## Validacion

### Automaticas

- Pasado: `python3 -m compileall spritesheet_frame_selector`.
- Pasado: `python3 -m unittest discover -s tests` con 66 tests.

### Blender GUI

Validar en una escena donde el viewport este inicialmente en perspectiva libre alejada:

1. Seleccionar workspace, collection y camara efectiva.
2. Ejecutar `Generate Preview` en `SOLID` sin entrar manualmente a Camera View.
3. Confirmar que el encuadre coincide con la camara efectiva.
4. Repetir en `MATERIAL`.
5. Confirmar que al terminar el viewport vuelve a la perspectiva previa del usuario.
6. Repetir varias veces y confirmar tamano estable.

Resultado:

- Pasado por validacion del usuario: el preview queda con el tamano/encuadre correcto sin activar Camera View manualmente.

### Criterio De Aceptacion

- Los thumbnails `SOLID` y `MATERIAL` no dependen de que el usuario haya activado Camera View antes.
- El viewport queda restaurado tras generar previews.
- La ruta `RENDERED` no cambia en este subplan.

## Proximo Paso Recomendado

Retomar V2-V5 de `docs/plans/reinicio-v2-fase-6a-validacion-hito1-selector-modal-lifecycle.md`.
