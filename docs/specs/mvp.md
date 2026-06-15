Quiero desarrollar un addon para Blender llamado SpriteSheet Frame Selector.

Contexto:
El objetivo no es crear un editor general de spritesheets. El objetivo es resolver un problema específico de producción: seleccionar visualmente qué frames de una animación 3D en Blender se convertirán en spritesheet, renderizar solo esos frames y exportar una spritesheet final de forma rápida, estable y con baja fricción.

Prioridad del proyecto:
1. Estabilidad.
2. Fluidez.
3. Rendimiento.
4. UX funcional clara.
5. UI bonita solo después.

No se debe sobreconstruir. El addon debe empezar como una herramienta de producción pequeña, robusta y usable.

Target:
- Blender 5.x.
- Debe funcionar en macOS y Windows.
- No depender de terminal ni instalación manual de dependencias externas.
- Evitar Pillow como dependencia obligatoria.
- Si se usa algún backend externo/opcional, debe ser opcional y no bloquear el uso básico.
- El addon debe instalarse como un addon normal de Blender: ZIP/install/enable/use.

Concepto central:
El usuario trabaja una animación en Blender. El addon genera previews pequeños de los frames de esa animación. Luego el usuario selecciona visualmente qué frames quiere usar. Después el addon renderiza solo esos frames seleccionados y compone una spritesheet PNG final.

Arquitectura deseada:
Separar claramente:
1. Properties / data model.
2. Preview generation.
3. Selection state.
4. UI sidebar.
5. Visual selection window/modal.
6. Render queue.
7. Spritesheet composer backend.
8. Persistence inside .blend.
9. Export.

El código debe ser modular para poder reemplazar el composer backend después si hace falta optimizar.

Persistencia:
Todo el estado de trabajo debe guardarse dentro del archivo .blend:
- clips creados;
- rangos de frames;
- frames seleccionados;
- settings de preview;
- settings de export;
- cámara elegida;
- output folder;
- nombre del spritesheet;
- estado de cache/previews.

JSON metadata (obligatorio para multi-clip export)

JSON metadata no es prioridad para export individual simple.

Pero SI es obligatorio cuando:
- múltiples clips se exportan al mismo atlas/spritesheet.

El JSON debe indicar:
- nombre de cada clip;
- índice inicial;
- índice final;
- cantidad de frames;
- FPS opcional;
- frame_width;
- frame_height;
- columnas;
- filas si aplica.

Ejemplo esperado:

{
  "sheet": "character_main",
  "frameWidth": 64,
  "frameHeight": 64,
  "clips": {
    "idle": {
      "start": 0,
      "end": 5,
      "count": 6,
      "fps": 8
    },
    "run": {
      "start": 6,
      "end": 13,
      "count": 8,
      "fps": 12
    }
  }
}

No sobrecomplicar metadata en MVP.
Solo exportar información necesaria para identificar qué frames pertenecen a cada animación.


UI principal:
Crear panel en:
3D Viewport > Sidebar/N Panel > SpriteSheet.

El sidebar debe servir para:
- crear/configurar clips;
- definir rango de frames;
- generar/refresh previews;
- abrir ventana visual de selección;
- configurar export;
- ejecutar export;
- ver estado/warnings.

Además debe existir una ventana/modal/popup más grande para la selección visual de frames. No intentar meter toda la grilla en el sidebar si se vuelve incómodo.

Flujo MVP:
1. Usuario define o crea un clip.
2. Define frame_start, frame_end, frame_step.
3. Define preview cell size: custom desde el inicio, con presets 32, 64, 128.
4. Elige cámara: usar cámara activa por defecto, pero permitir elegir otra cámara.
5. Click en Generate Preview.
6. El addon genera previews pequeños y cacheados.
7. Sidebar muestra aviso si los previews existen.
8. Usuario abre Visual Selector.
9. Visual Selector muestra una grilla tipo spritesheet/contact sheet.
10. Cada celda representa un frame.
11. Cada celda debe mostrar:
   - thumbnail preview;
   - número de frame;
   - estado seleccionado/no seleccionado.
12. Usuario selecciona/deselecciona frames.
13. Estado queda guardado en .blend.
14. Usuario configura export final.
15. Click Export SpriteSheet.
16. Addon renderiza solo frames seleccionados.
17. Addon compone PNG spritesheet final.
18. Guarda archivo en carpeta elegida.

Clips:
- El usuario debe poder trabajar animación por animación.
- Debe existir soporte para múltiples clips en el archivo.
- Cada clip tiene nombre, rango, step, cámara opcional, selección de frames y settings.
- Para MVP, exportar un clip individual es obligatorio.
- Preparar estructura para futuro atlas combinado.
- Si es razonable, implementar “Export All Clips to One SpriteSheet” después del export individual, pero no bloquear el MVP por esto.

Multi-clip support (prioridad alta)

La herramienta debe diseñarse desde el inicio pensando en múltiples clips.

Aunque el MVP puede enfocarse primero en export individual por clip, la arquitectura debe priorizar y facilitar:
- atlas multi-animación;
- export combinado;
- metadata por clip;
- playback por clip;
- administración de múltiples animaciones.

Cada clip debe contener:
- nombre;
- rango de frames;
- selección de frames;
- preview cache;
- FPS;
- cámara opcional;
- settings específicos si hace falta.

El usuario debe poder:
- trabajar clips por separado;
- previsualizar clips individualmente;
- exportar clips individuales;
- combinar varios clips en un único spritesheet final.

Esto no debe sentirse como feature secundaria añadida después.
Debe influir desde el inicio en el data model y export pipeline.

Selección visual:
Implementar en la ventana/modal:

- Click sobre celda: toggle select/unselect.
- Drag mouse normal: pintar selección, seleccionar celdas por donde pasa el mouse.
- Ctrl + drag: pintar deselección.
- Box select / marquee: arrastrar rectángulo para seleccionar múltiples frames.
- Idealmente Shift + click: seleccionar rango entre último frame clickeado y frame actual.
- Botones globales:
  - Select All
  - Deselect All
  - Invert Selection
  - Select Every N Frames

Si alguna interacción avanzada es difícil en Blender API, implementar primero:
1. click toggle;
2. select all/deselect all/invert;
3. select every N;
4. luego drag;
5. luego box select.

No sacrificar estabilidad por interacciones complejas.

Preview:
- Preview debe ser rápido y pequeño.
- Preview size custom desde inicio.
- Presets: 32x32, 64x64, 128x128.
- El preview no necesita calidad final.
- Usar método liviano: viewport render / OpenGL render / EEVEE bajo si aplica.
- No usar render final caro para previews.
- Cachear previews en una carpeta temporal o subcarpeta controlada por el addon.
- No regenerar previews si ya existen, salvo que el usuario use Refresh Preview.
- Si cambia algo importante en escena, no intentar detectar todo automáticamente. Mostrar un warning simple tipo “Preview may be outdated. Refresh manually if animation/camera/materials changed.”
- Debe existir botón Refresh Preview.
- Debe existir botón Clear Preview Cache.

Render final:
- Debe renderizar solo frames seleccionados.
- Debe respetar alpha/transparency.
- Debe usar configuración de escena por defecto.
- Permitir override de resolución final por frame:
  - frame_width;
  - frame_height.
- Formato default: PNG.
- Export PNG sequence debe existir como opción, pero apagada por defecto.
- El usuario debe elegir output folder.
- El usuario debe definir file name/base name.

Export settings:
- frame_width;
- frame_height;
- columns;
- rows auto calculadas;
- padding;
- margin;
- transparent background;
- output folder;
- spritesheet file name;
- optional PNG sequence export off by default.

Spritesheet composition:
La composición de spritesheet fue un bottleneck en una herramienta anterior. Debe diseñarse para ser rápida.

Requisitos:
- No manipular píxel por píxel en Python puro si se puede evitar.
- No usar operaciones lentas de Blender Image datablocks si existen alternativas más rápidas.
- Investigar primero qué opciones ofrece Blender 5.x para composición eficiente sin dependencias externas obligatorias.
- Preferir backend nativo o bufferizado.
- Diseñar una interfaz clara de composer backend para poder reemplazarlo después.
- Si se usa una dependencia opcional para acelerar, debe ser opcional.
- El addon debe funcionar sin instalación manual externa.

El composer debe:
- recibir lista ordenada de imágenes renderizadas;
- recibir frame_width, frame_height, columns, padding, margin;
- calcular rows automáticamente;
- componer un PNG final con alpha;
- guardar en output folder.

Performance:
- Preview selection debe sentirse fluida.
- Generación de previews puede tardar, pero debe mostrar progreso.
- Export final puede tardar según render engine, pero debe mostrar progreso.
- La composición del spritesheet no debería ser el bottleneck principal.
- Evitar bloquear Blender más de lo necesario.
- Restaurar frame actual al terminar.
- Restaurar settings temporales modificadas.
- No ensuciar la escena con objetos o imágenes innecesarias.

Data model sugerido:
Crear PropertyGroups similares a:

SpriteSheetFrameItem:
- frame_number: int
- selected: bool
- preview_path: string
- original_index: int

SpriteSheetClip:
- name: string
- frame_start: int
- frame_end: int
- frame_step: int
- camera: pointer/string
- preview_size: int
- frames: CollectionProperty(SpriteSheetFrameItem)
- selected_frame_index: int
- cache_folder: string
- cache_dirty: bool
- last_preview_note: string

SpriteSheetExportSettings:
- frame_width: int
- frame_height: int
- columns: int
- padding: int
- margin: int
- transparent: bool
- output_folder: string
- sheet_name: string
- export_png_sequence: bool
- png_sequence_folder: string

Scene properties:
- clips: CollectionProperty(SpriteSheetClip)
- active_clip_index: int
- export_settings: PointerProperty(SpriteSheetExportSettings)

Operadores mínimos:
- Add Clip
- Remove Clip
- Duplicate Clip
- Generate Preview
- Refresh Preview
- Clear Preview Cache
- Open Visual Selector
- Select All Frames
- Deselect All Frames
- Invert Selection
- Select Every N Frames
- Export Selected Clip SpriteSheet
- Export PNG Sequence optional
- Export All Clips to One SpriteSheet, solo si no complica MVP

UX del sidebar:
Debe mostrar:
- lista de clips;
- active clip settings;
- preview controls;
- selection summary;
- export settings;
- export button;
- warnings.

Debe mostrar contadores:
- total frames in range;
- preview frames generated;
- selected frames;
- estimated rows;
- estimated sheet resolution;
- warning si sheet supera 4096x4096 o 8192x8192.

Visual Selector:
Debe priorizar estabilidad y funcionalidad.
Si Blender no permite una grilla interactiva perfecta en el primer intento, implementar alternativa robusta:
- una grilla tipo contact sheet con overlay;
- o UIList con thumbnails como fallback;
- pero mantener la arquitectura preparada para mejorar el selector visual.

No aceptar como resultado final un sistema que solo tenga lista textual si no hay ruta clara al selector visual. El diferencial del producto es seleccionar frames visualmente.

Estados visuales:
- Frame seleccionado: overlay claro o borde visible.
- Frame no seleccionado: atenuado.
- Hover si es posible.
- Número de frame visible.
- Clip activo visible.
- Mensaje de cache outdated si corresponde.

Validaciones:
Antes de exportar:
- debe existir clip activo;
- debe haber frames generados;
- debe haber al menos 1 frame seleccionado;
- output folder debe existir o crearse;
- frame_width/frame_height > 0;
- columns > 0;
- padding/margin >= 0;
- cámara válida;
- avisar si no hay cámara y la escena requiere cámara.

No hacer en MVP:
- editor de pivots;
- JSON metadata;
- trimming automático;
- auto remove duplicate/similar frames;
- detección automática de frames idénticos;
- reorden manual;
- integración Unity/Unreal/Web runtime;
- onion skin;
- packing irregular;
- dependencias externas obligatorias;
- UI excesivamente estilizada;
- marketplace/licensing todavía.

Feature futura anotada:
Visualizador de frames idénticos o muy parecidos.
No borrar automáticamente frames duplicados. Solo mostrar/advertir, porque frames repetidos pueden ser decisión de diseño.

Criterio de éxito del primer prototipo:
Debe permitir en una escena simple:
1. crear clip 1-20;
2. generar previews 64x64;
3. abrir selector visual;
4. seleccionar/deseleccionar frames;
5. guardar selección en .blend;
6. cerrar y reabrir el archivo manteniendo selección;
7. exportar solo frames seleccionados;
8. generar un PNG spritesheet correcto con alpha, columnas, padding y margen.

Entregables:
- addon instalable para Blender 5.x;
- estructura de archivos clara;
- instrucciones de instalación;
- instrucciones de uso;
- notas de limitaciones;
- explicación breve del composer backend elegido;
- lista TODO para v2.

Antes de escribir código:
1. Revisar API disponible en Blender 5.x para preview rendering, modal UI y composición de imágenes.
2. Proponer estructura de carpetas del addon.
3. Proponer estrategia concreta para el Visual Selector.
4. Proponer estrategia concreta para composición rápida sin dependencias externas obligatorias.
5. Luego implementar por etapas, no todo de una vez.

Importante:
No improvisar features fuera de scope.
No convertir esto en una app externa.
No convertirlo en un editor completo de spritesheets.
El producto es una herramienta Blender-first para selección visual de frames de animación y exportación rápida a spritesheet.

Playback Preview (feature core)

El addon debe permitir reproducir la animación resultante usando únicamente los frames seleccionados.

Esto es extremadamente importante porque el usuario necesita validar:
- readability;
- timing;
- sensación del movimiento;
- cantidad de frames;
- recortes de animación;
- fluidez del spritesheet final.

El playback preview debe existir desde el MVP.

Requisitos:
- reproducir solo frames seleccionados;
- respetar orden temporal;
- loop opcional;
- FPS configurable;
- play/pause/stop;
- scrub opcional más adelante;
- preview rápido usando previews cacheados;
- no renderizar nuevamente para playback;
- usar thumbnails/previews ya generados;
- playback debe sentirse inmediato y liviano.

Idealmente:
- playback dentro del Visual Selector;
o
- popup/modal de preview simple.

No usar render final para playback.

El usuario debe poder:
1. seleccionar frames;
2. presionar Play;
3. ver exactamente cómo se verá la animación exportada;
4. iterar rápidamente.

Esto es parte central del producto.


El playback preview y el multi-clip atlas son dos de las features más importantes del producto.
No deben tratarse como extras tardíos.
La arquitectura inicial debe diseñarse pensando en ellas.