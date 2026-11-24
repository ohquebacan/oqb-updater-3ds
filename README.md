# OQB UPDATER 3DS

**All In One para Nintendo 3DS**, por **oh que bacan**.

Una tienda nativa para descubrir, descargar, instalar, actualizar y abrir homebrew sin salir de la consola. Incluye nuestros ports, aplicaciones de la comunidad y Universal-DB, con temas claros y oscuros y colores inspirados en Bacan Shop.

This project was developed with the help of [OpenAI Codex](https://openai.com/codex/) and [Claude Code](https://claude.com/product/claude-code). Learn more about the development process [here](AI_DEVELOPMENT.md).

No incluye ROMs, datos comerciales de juegos, firmware DSP ni partidas. Los ports que necesitan archivos propios indican exactamente cuál debes colocar en la SD.

## Descargar

- [OQB Updater 3DS — CIA](https://raw.githubusercontent.com/ohquebacan/oqb-updater-3ds-resources/store-packs/oqb-updater-3ds.cia)
- [OQB Updater 3DS — 3DSX](https://raw.githubusercontent.com/ohquebacan/oqb-updater-3ds-resources/store-packs/oqb-updater-3ds.3dsx)
- [SHA256SUMS](builds/3ds/SHA256SUMS)

**Versión estable: 1.4.**

### Instalación

1. **CIA:** copia el archivo a la SD e instálalo con FBI.
2. **3DSX:** copia `oqb-updater-3ds.3dsx` a `sdmc:/3ds/oqb-updater-3ds/` y ábrelo desde Homebrew Launcher.
3. Abre **OQB UPDATER 3DS**, elige el tema y entra en la tienda.
4. Con Wi-Fi activado, los recursos gráficos y vídeos adicionales se descargan en segundo plano.

La descarga inicial de la aplicación ocupa unos 11 MB. Reserva espacio adicional para los recursos y para cada aplicación que instales.

## Actualizaciones automáticas

Cada apertura comprueba si existe una versión más reciente. Cuando haya una actualización, la app mostrará su versión y pedirá confirmación antes de descargarla. El archivo se verifica por tamaño y SHA-256 antes de instalarse.

Esta versión 1.4 debe instalarse una vez manualmente. Las siguientes versiones podrán instalarse desde la propia aplicación. Consulta [actualizaciones y caché](docs/UPDATES-AND-CACHE.md) para conocer el proceso y sus límites.

## Funciones

- Catálogo de nuestros ports y homebrew de la comunidad.
- Banners, capturas, vídeos y páginas de GitHub dentro de la consola.
- Descargas verificadas, instalación, desinstalación y apertura directa.
- Detección de aplicaciones instaladas mediante FBI o Universal-Updater.
- Actualizaciones de la tienda y de las aplicaciones instaladas.
- Integración opcional con Universal-DB.
- Temas claro y oscuro, varios colores y ocho idiomas.
- Interfaz nativa para las pantallas de 400×240 y 320×240.

## Controles

| Entrada | Acción |
| --- | --- |
| D-Pad / pantalla táctil | Navegar |
| A | Abrir / confirmar |
| B | Volver |
| L / R | Cambiar de pestaña |
| X | Abrir la página de GitHub del elemento seleccionado |
| Y / START / SELECT | Atajos mostrados en la pantalla táctil |
| Vídeo: A · ◀ ▶ · Y · B | Pausa · posición · silencio · volver |

## Compilar

Instala devkitARM, libctru, Citro2D/Citro3D y las portlibs documentadas. Después ejecuta:

```sh
zsh 3ds/build.sh
```

Los resultados se generan en `3ds/build/`. Consulta la [guía de compilación](docs/BUILDING.md) y la [arquitectura](docs/ARCHITECTURE.md).

## Créditos

- **EstebanPdN** — diseño, aplicación nativa y catálogo originales de Forge Store, con ayuda de Codex y Claude Code.
- Los autores de cada aplicación del catálogo; sus páginas enlazan con los repositorios originales y sus recursos se registran en [créditos de assets](docs/ASSET-CREDITS.md).
- [Universal-Team](https://github.com/Universal-Team) — Universal-DB.
- [devkitPro](https://github.com/devkitPro) — devkitARM, libctru, Citro2D y Citro3D.
- libwebp, NanoSVG, Theora, libjpeg-turbo, curl, mbedTLS, Jansson, libarchive y las demás bibliotecas incluidas en los [avisos de terceros](docs/legal/THIRD_PARTY_NOTICES.md).
- La comunidad homebrew de Nintendo 3DS — herramientas, documentación y pruebas.

## Licencia y aviso legal

Los [derechos y licencias](LICENSE.md) dependen de cada componente. El software de terceros conserva su licencia original. Los nombres, imágenes y marcas de los juegos pertenecen a sus respectivos propietarios.

Proyecto homebrew no oficial, sin afiliación con Nintendo.
