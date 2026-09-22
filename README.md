# SpriteSheet Frame Selector

Addon para Blender 5.x que permite organizar animaciones por clips, elegir sus
frames visualmente y exportarlos como un spritesheet PNG con metadata JSON.

## Caracteristicas

- Multiples workspaces y clips persistentes dentro del archivo `.blend`.
- Camara y colecciones predeterminadas por workspace, con overrides por clip.
- Previews cacheados en modos `Rendered`, `Solid` y `Material`.
- Selector visual modal y reproduccion de los frames seleccionados.
- Exportacion de uno o varios clips en un atlas PNG.
- Metadata JSON con rangos, FPS y posicion de cada clip.
- Exportacion opcional de frames individuales numerados por orden de salida.
- Restauracion del estado de render y soporte de transparencia RGBA.

## Requisitos

- Blender 5.0 o posterior.
- No requiere dependencias externas.

La version distribuida se valida en Blender 5.1.1. La compatibilidad declarada
con Blender 5.0 sigue el contrato del proyecto, pero esa version concreta no
forma parte de la matriz automatizada actual.

## Instalacion

1. Descarga el ZIP de la version deseada desde
   [Releases](https://github.com/sebaamaruc/spritesheet-blender/releases).
2. En Blender abre **Edit > Preferences > Extensions**.
3. Abre el menu de la esquina superior derecha y selecciona
   **Install from Disk**.
4. Elige el ZIP sin descomprimirlo.
5. Activa **SpriteSheet Frame Selector** si Blender no lo activa
   automaticamente.

El panel aparece en **3D Viewport > Sidebar (`N`) > SpriteSheet**.

## Uso basico

1. Crea un workspace.
2. Asigna su camara y las colecciones visibles predeterminadas.
3. Crea un clip y configura su rango, step, FPS y tamano de preview.
4. Usa **Generate Preview** para crear sus miniaturas.
5. Abre **Visual Selector** y elige los frames que quieres exportar.
6. Repite el proceso con otros clips y marca los que deban incluirse.
7. Configura en el workspace el tamano de frame, columnas, padding, margen,
   transparencia, carpeta de salida y nombre de la hoja.
8. Ejecuta **Export SpriteSheet**.

El export genera `<nombre>.png` y `<nombre>.json`. Si activas
**Export Individual Frames**, tambien genera una secuencia `001.png`,
`002.png`, etc., limitada a 999 frames por ejecucion.

## Selector visual

- `Tab`: alterna entre edicion y reproduccion.
- `Space`: reproduce o pausa.
- `Shift + Flecha izquierda`: vuelve al primer frame.
- Rueda del raton: desplaza la grilla cuando el cursor esta sobre el panel.
- `Esc` o clic derecho: cierra el selector.

## Limitaciones conocidas

- La interfaz modal y los previews de viewport dependen del contexto grafico de
  Blender.
- La matriz actual usa macOS con Metal; otros backends graficos no estan
  cubiertos todavia.
- El compositor mantiene el atlas completo en memoria. El addon rechaza hojas
  que superen 16384 px por lado.
- Los contadores de frames almacenados se actualizan al regenerar previews o
  exportar despues de cambiar el rango del clip.
- El soporte para rutas Blender relativas (`//`) funciona en Blender 5.1.1,
  aunque puede producir un warning en consola.

## Construccion del paquete

```bash
/Applications/Blender.app/Contents/MacOS/Blender --command extension validate spritesheet_frame_selector
/Applications/Blender.app/Contents/MacOS/Blender --command extension build \
  --source-dir spritesheet_frame_selector \
  --output-filepath spritesheet_frame_selector-0.1.0.zip
```

## Licencia

Este proyecto se distribuye bajo **GNU GPL v3 o posterior**. Consulta
[`LICENSE`](LICENSE).
