# Plan Fase 7 - Validacion Final Y Distribucion

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: validado

## Referencia Superior

`docs/plans/reinicio-v2-master-plan.md`

## Plan Rector Relacionado

`docs/archive/reinicio-v2-fase-5-workspace-root-vertical-slices.md`

## Resumen

Preparar el addon V2 para uso distribuible despues de ejecutar la Fase 6 de correcciones de auditoria tecnica: validar el flujo MVP completo en Blender, revisar lifecycle de registro/recarga, limpiar residuos, confirmar contrato de export PNG/JSON, revisar metadata/manifest y generar un ZIP instalable limpio.

Esta fase no debe agregar features nuevas de producto. Su objetivo es estabilizar lo ya implementado y convertirlo en un paquete confiable.

## Estado De Entrada

- Fase 5a workspace data model: validada.
- Fase 5b workspace/clip management: validada.
- Fase 5c preview cache workspace-aware: validada.
- Fase 5d selector visual minimo: validada.
- Fase 5e playback preview: validada.
- Fase 5e1 selector/playback UX: validada con correcciones posteriores.
- Fase 5f render final workspace-aware: funcionalidad validada por usuario; flujo publico separado reemplazado por opcion integrada en 5g.
- Fase 5g export spritesheet y JSON: validada por usuario; correcciones UI/naming/atajos posteriores validadas por usuario.
- Fase 6 correcciones de auditoria tecnica: implementada, validada y archivada.

## Documentacion Fuente Usada

- `docs/specs/product_requirements.md`
- `docs/specs/mvp_v2.md`
- `docs/specs/validation_plan.md`
- `docs/architecture/addon_architecture.md`
- `docs/design/visual_selector_strategy.md`
- `docs/plans/reinicio-v2-master-plan.md`
- `docs/archive/reinicio-v2-fase-5-workspace-root-vertical-slices.md`
- `docs/archive/reinicio-v2-fase-5g-export-spritesheet-json.md`

## Interpretacion Operativa

El MVP V2 ya tiene implementado el flujo principal:

```text
workspace -> clips -> preview -> selector -> playback -> export PNG/JSON
```

La Fase 7 debe verificar que ese flujo sea instalable, repetible y distribuible despues de que la Fase 6 haya corregido o clasificado explicitamente los hallazgos de `docs/technical-audit.md`. Si aparecen bugs durante validacion, deben corregirse dentro de esta fase solo cuando sean defectos de estabilizacion, packaging, docs, lifecycle o validacion. Nuevas features deben quedar fuera.

## Objetivo

Dejar el addon V2 en estado de paquete instalable para prueba real:

- ZIP limpio instalable en Blender 5.x.
- Registro/desregistro/reactivacion sin errores.
- Flujo MVP completo validado manualmente.
- Validaciones automaticas repetibles.
- Sin residuos locales dentro del paquete.
- Documentacion minima de instalacion, uso y limitaciones.
- PCS actualizado para reflejar el estado final de Fase 7 sin cerrar el proyecto salvo instruccion explicita.

## Alcance

### Incluir

- Revision de estructura del paquete `spritesheet_frame_selector/`.
- Revision de `blender_manifest.toml`.
- Revision de version, nombre, tagline, licencia y compatibilidad Blender 5.x.
- Limpieza de imports muertos, operadores no registrados, clases no usadas y archivos residuales detectables.
- Limpieza de `__pycache__/`, `*.pyc`, `.DS_Store`, ZIPs viejos y outputs locales antes de empaquetar.
- Validacion de `.gitignore` para evitar subir artefactos.
- Generacion de ZIP distribuible limpio.
- Prueba de instalacion/activacion/desactivacion/reactivacion en Blender.
- Prueba de archivo nuevo.
- Prueba de cambio de escena.
- Prueba de camera/collection faltante o borrada.
- Prueba de workspace con default camera/collection.
- Prueba de clip con camera/collection override.
- Prueba de preview en modos disponibles.
- Prueba de selector visual y atajos.
- Prueba de playback.
- Prueba de export spritesheet PNG + JSON.
- Prueba de `Export Individual Frames`.
- Revision del contrato JSON generado frente al contrato aceptado por el usuario.
- Reconciliacion documental de Fase 5h:
  - confirmar que 5g cubre el atlas multi-clip + JSON basico del MVP;
  - dejar 5h como diferido/atlas avanzado si ya no es necesario para MVP;
  - actualizar PCS/docs si corresponde.
- Crear o actualizar documentacion minima de uso si no existe:
  - `README.md` o documento equivalente;
  - instrucciones de instalacion;
  - flujo basico de uso;
  - limitaciones conocidas.

### Excluir

- Nuevas features de selector avanzado.
- Drag select, box select, range select.
- Packing irregular.
- Metadata runtime compleja.
- Integraciones Unity/Unreal/Web.
- Marketplace/licensing publico avanzado.
- Migracion automatica desde archivos V1.
- Dependencias externas obligatorias.
- Cambios de arquitectura no necesarios para estabilizar.

## Archivos Afectados Esperados

- `spritesheet_frame_selector/blender_manifest.toml`
- `spritesheet_frame_selector/__init__.py`
- `spritesheet_frame_selector/registration.py`
- `spritesheet_frame_selector/**/*.py`
- `.gitignore`
- `README.md` o `docs/usage/installation.md` si se decide documentacion en `docs/`
- `docs/specs/validation_plan.md`
- `docs/plans/reinicio-v2-fase-7-validacion-distribucion.md`
- `.context/agent_context.md`
- `.context/index.md`
- `.context/handoff.md`
- `.context/worklog.jsonl`

## Reglas De Implementacion

- No agregar features de producto.
- No cambiar contratos ya validados salvo bug confirmado.
- No crear ZIP final si hay errores de tests o residuos en el paquete.
- No incluir `tests/`, `docs/`, `.context/`, `.git`, `__pycache__/`, `.DS_Store`, outputs ni ZIPs previos dentro del ZIP instalable.
- No usar dependencias externas para packaging.
- No usar comandos destructivos sin aprobacion cuando impliquen borrar residuos.
- Si Blender background crashea por entorno, documentar limitacion y usar validacion manual GUI como fuente final.
- Mantener rutas PCS repo-relativas.
- Validar no es cerrar: no marcar el proyecto como cerrado sin instruccion explicita.

## Pasos De Ejecucion

1. Leer PCS y este plan aprobado.
2. Ejecutar `git status --short --ignored`.
3. Confirmar que los cambios pendientes son esperados del reinicio V2.
4. Revisar estructura del addon:
   - archivos de paquete;
   - imports;
   - registro centralizado;
   - operadores registrados;
   - props persistentes;
   - helpers puros.
5. Revisar `blender_manifest.toml`:
   - `id`;
   - `version`;
   - `name`;
   - `tagline`;
   - `maintainer`;
   - `blender_version_min`;
   - `license`;
   - `tags`.
6. Revisar `.gitignore` y reglas para artefactos.
7. Revisar contrato JSON real generado por 5g y decidir si docs deben alinearse con el contrato validado.
8. Confirmar que la Fase 6 de correcciones de auditoria tecnica quedo validada o que sus diferidos estan documentados como no bloqueantes para distribucion.
9. Reconciliar Fase 5h:
   - si el MVP multi-clip JSON ya esta cubierto por 5g, documentar 5h como diferida/reemplazada por 5g;
   - si falta algo critico para MVP, detener Fase 7 y proponer subplan 5h especifico antes de distribuir.
10. Ejecutar validaciones automaticas:
   - `python3 -m compileall spritesheet_frame_selector`
   - `python3 -m unittest discover -s tests`
   - busquedas `rg` para residuos conocidos.
11. Ejecutar validacion de lifecycle con Blender si el entorno lo permite:
    - importar addon;
    - `register()` / `unregister()` repetido;
    - activar/desactivar/reactivar si se puede desde CLI o GUI.
12. Ejecutar matriz manual en Blender GUI.
13. Corregir solo bugs de estabilizacion encontrados.
14. Limpiar residuos generados por validacion con aprobacion si el entorno la requiere.
15. Crear ZIP instalable limpio en una ruta acordada o temporal ignorada.
16. Inspeccionar contenido del ZIP.
17. Probar instalacion del ZIP en Blender.
18. Actualizar documentacion minima de instalacion/uso/limitaciones.
19. Actualizar plan y PCS segun resultado.

## Matriz De Validacion Manual Blender

### Lifecycle

- Abrir Blender con archivo nuevo.
- Instalar/activar addon.
- Desactivar addon.
- Reactivar addon.
- Cerrar/reabrir Blender si aplica.
- Confirmar que no hay traceback en consola.

### Escena Nueva

- Crear workspace.
- Asignar default camera.
- Asignar default collection.
- Crear clip.
- Generar preview.
- Abrir selector visual.
- Seleccionar/deseleccionar frames.
- Probar atajos:
  - `Space`;
  - `Tab`;
  - `Shift + Left`.
- Reproducir playback.
- Exportar spritesheet PNG + JSON.
- Exportar frames individuales opcionales.

### Multi-Clip

- Crear al menos 2 clips incluidos.
- Confirmar orden manual.
- Confirmar nombres unicos.
- Exportar atlas combinado.
- Confirmar JSON:
  - `sheet`;
  - `frameWidth`;
  - `frameHeight`;
  - `columns`;
  - `clips`;
  - rangos globales;
  - `start` empieza en 0;
  - `end` es inclusivo;
  - `count` correcto;
  - `fps` correcto.

### Overrides

- Workspace default camera + collection.
- Clip con camera override.
- Clip con collection override.
- Confirmar que preview/export respetan override.

### Errores Controlados

- Sin camera efectiva.
- Sin collection efectiva.
- Collection borrada.
- Camera borrada.
- Rango invertido.
- Step invalido.
- Sin frames seleccionados.
- Carpeta de export faltante.
- Nombre de sheet vacio.
- Mas de 999 frames individuales con opcion activa debe fallar con mensaje claro.

### Persistencia

- Guardar `.blend` temporal fuera del repo.
- Reabrir.
- Confirmar workspaces, clips, frames, seleccion, export settings y overrides.
- Confirmar que caches derivados no rompen el archivo si faltan en disco.

## Validaciones Automaticas

- `python3 -m compileall spritesheet_frame_selector`
- `python3 -m unittest discover -s tests`
- `rg -n "__pycache__|\\.DS_Store|MagicMock|Imagenes_test" .`
- `rg -n "TODO|FIXME|print\\(" spritesheet_frame_selector tests`
- `rg -n "Scene\\.spritesheet_state\\.clips|spritesheet_state\\.clips|active_clip_index.*Scene" spritesheet_frame_selector tests`
- Inspeccion de ZIP:
  - no contiene `.git`;
  - no contiene `.context`;
  - no contiene `docs`;
  - no contiene `tests`;
  - no contiene `__pycache__`;
  - no contiene `.DS_Store`;
  - no contiene outputs PNG/JSON temporales.

## Riesgos

- Blender background puede crashear en el entorno local antes de ejecutar Python; la validacion GUI puede ser obligatoria.
- La UI modal del selector depende de draw handlers y debe validarse visualmente.
- El empaquetado ZIP puede incluir residuos si se hace con comandos amplios.
- El contrato JSON documentado historicamente puede diferir del contrato validado por usuario; debe resolverse explicitamente antes de distribuir.
- Los paths de cache/export pueden persistir en `.blend`; deben tolerar archivos faltantes.
- Nombres editables inline en UIList dependen del comportamiento nativo de Blender.

## Criterio De Termino

La Fase 7 queda validada cuando:

- el addon se instala por ZIP limpio;
- activar/desactivar/reactivar no produce errores;
- el flujo MVP completo pasa en Blender GUI;
- los tests automaticos pasan;
- el ZIP inspeccionado contiene solo el addon;
- no quedan residuos en el paquete;
- la documentacion minima de instalacion/uso existe;
- las limitaciones conocidas quedan documentadas;
- PCS registra el estado final y el siguiente paso.

## Resultado Esperado Del ZIP

Estructura esperada dentro del ZIP:

```text
spritesheet_frame_selector/
  __init__.py
  blender_manifest.toml
  preferences.py
  properties.py
  registration.py
  core/
  export/
  operators/
  playback/
  preview/
  render/
  ui/
```

## Proximo Paso Despues De Esta Fase

Si Fase 7 valida correctamente:

- preparar un commit/release interno;
- decidir si se crea una Fase 8 de pulido UX o si el MVP queda listo para uso interno;
- no cerrar el proyecto ni archivar planes sin instruccion explicita del usuario.

Si Fase 7 detecta defectos:

- corregir dentro de Fase 7 si son bugs de estabilidad/distribucion;
- crear subplan especifico si aparece una feature o rediseño mayor.

## Resultado De Ejecucion

Fecha de validacion: 2026-09-22.

- Manifiesto y ZIP validados con la CLI de Blender 5.1.1.
- ZIP construido con `blender --command extension build`; contiene solo el
  addon y su licencia.
- Instalacion y activacion verificadas desde el ZIP en un perfil aislado.
- Compilacion Python correcta.
- Suite unitaria: 85 tests aprobados.
- Suite Blender background: 141 tests aprobados.
- Suite Blender GUI: 10 comprobaciones aprobadas.
- Registro, desregistro, persistencia, previews, selector, playback, export PNG
  y JSON, frames individuales, limites y errores controlados quedan cubiertos
  por las suites anteriores.
- La entrega fisica de eventos de teclado y raton al selector se mantiene como
  comprobacion manual recomendada: no se automatizo sobre una ventana existente
  para evitar interferir con trabajo abierto del usuario.
- Se agregaron README, instrucciones de instalacion y uso, limitaciones y
  licencia GPL-3.0-or-later.
- Fase 5h queda reconciliada como atlas avanzado diferido; Fase 5g cubre el
  atlas multi-clip y JSON simple requeridos por el MVP.

La fase queda validada. No se cierra ni archiva hasta recibir una instruccion
explicita de cierre PCS.
