# RSS Feed - De Nit (RNE 4)

Feed RSS no oficial del programa "De Nit" de RNE 4 (Catalunya Ràdio) generado automáticamente.

## 🎙️ Descripción

Este proyecto genera automáticamente un feed RSS para el programa de radio "De Nit" de RTVE, permitiendo suscribirse y escuchar los episodios en cualquier aplicación de podcasts.

El sistema extrae la información de los episodios directamente de la web de RTVE y genera un feed RSS 2.0 compatible con todos los lectores de podcasts.

## 📡 Suscripción al Feed

Puedes suscribirte al podcast usando la siguiente URL en tu aplicación de podcasts favorita:

```
https://raw.githubusercontent.com/sergioedo/rss-la-nit/main/feed.xml
```

### Aplicaciones recomendadas:
- **iOS**: Apple Podcasts, Overcast, Castro
- **Android**: Pocket Casts, AntennaPod, Google Podcasts
- **Desktop**: iTunes, gPodder
- **Web**: Feedly, Inoreader

## 🚀 Características

- ✅ Scraping automático de episodios desde RTVE
- ✅ Feed RSS 2.0 con metadatos completos
- ✅ Compatible con iTunes y otras plataformas de podcasts
- ✅ Actualización automática diaria mediante GitHub Actions
- ✅ Incluye título, descripción, audio, imagen y duración de cada episodio
- ✅ Hasta 50 episodios más recientes

## 📁 Estructura del Proyecto

```
rss-la-nit/
├── .github/
│   └── workflows/
│       └── update-rss.yml      # GitHub Actions workflow
├── scraper.py                  # Script de scraping
├── generate_rss.py             # Generador de RSS
├── requirements.txt            # Dependencias de Python
├── feed.xml                    # Feed RSS generado (actualizado automáticamente)
├── .gitignore                  # Archivos ignorados por git
└── README.md                   # Esta documentación
```

## 🛠️ Instalación y Uso Manual

### Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/sergioedo/rss-la-nit.git
cd rss-la-nit
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

### Uso

#### 1. Ejecutar el scraper

Extrae información de los episodios:

```bash
python scraper.py --max-episodes 50 --output episodes.json
```

Opciones disponibles:
- `--max-episodes N`: Número máximo de episodios a obtener (default: 50)
- `--output FILE`: Archivo JSON de salida (default: episodes.json)
- `--delay SECONDS`: Delay entre peticiones (default: 1.0)

#### 2. Generar el feed RSS

Genera el archivo RSS a partir de los episodios extraídos:

```bash
python generate_rss.py --input episodes.json --output feed.xml
```

Opciones disponibles:
- `--input FILE`: Archivo JSON con episodios (default: episodes.json)
- `--output FILE`: Archivo RSS de salida (default: feed.xml)

## 🤖 Automatización

El feed se actualiza automáticamente mediante GitHub Actions:

- **Frecuencia**: Diariamente a las 6:00 AM UTC
- **Trigger manual**: Desde la pestaña "Actions" en GitHub
- **Al hacer push**: Se ejecuta automáticamente al actualizar el repositorio

### Workflow

1. El scraper extrae los últimos episodios de RTVE
2. Se genera un nuevo feed RSS con los datos actualizados
3. Si hay cambios, se hace commit automáticamente al repositorio
4. El feed actualizado queda disponible en la URL pública

## 📦 Dependencias

- **requests**: Peticiones HTTP
- **beautifulsoup4**: Parsing de HTML
- **feedgen**: Generación de feeds RSS
- **python-dateutil**: Manejo de fechas
- **lxml**: Parser XML/HTML

## ⚙️ Tecnologías

- **Python 3.x**: Lenguaje de programación
- **GitHub Actions**: Automatización y CI/CD
- **RSS 2.0**: Formato del feed
- **iTunes Podcast Tags**: Compatibilidad con plataformas de podcasts

## 📝 Notas Importantes

- Este es un proyecto **no oficial** y no está afiliado con RTVE
- El scraper respeta el servidor de RTVE con delays entre peticiones
- El contenido y los derechos pertenecen a RTVE
- El feed se proporciona únicamente para uso personal y educativo

## 🔧 Solución de Problemas

### El scraper no encuentra episodios

- Verifica que la URL del programa siga siendo válida
- RTVE puede haber cambiado la estructura de su web
- Revisa los logs de ejecución para más detalles

### El feed no se actualiza

- Verifica que GitHub Actions esté habilitado en el repositorio
- Revisa los logs de la ejecución del workflow
- Asegúrate de que el repositorio tenga permisos de escritura para GitHub Actions

## 📄 Licencia

Este proyecto está disponible bajo la licencia MIT. El contenido de los episodios pertenece a RTVE.

## 🙏 Créditos

- **RTVE**: Por el contenido original del programa "De Nit"
- **RNE 4 / Catalunya Ràdio**: Emisora que produce el programa
- Todos los presentadores y colaboradores del programa

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📧 Contacto

Para preguntas o sugerencias, abre un issue en GitHub.

---

**Disclaimer**: Este proyecto es no oficial y se proporciona "tal cual" sin garantías de ningún tipo. El uso del feed es bajo tu propia responsabilidad.
