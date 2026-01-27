#!/usr/bin/env python3
"""
Generador de feed RSS para el podcast "De Nit" de RTVE.
"""

import json
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
from dateutil import parser as date_parser
import re
from typing import List, Dict


class RSSGenerator:
    """Generador de feed RSS 2.0 para podcasts."""
    
    def __init__(self):
        """Inicializa el generador de RSS."""
        self.fg = FeedGenerator()
        self._setup_podcast_metadata()
    
    def _setup_podcast_metadata(self):
        """Configura los metadatos del podcast."""
        self.fg.load_extension('podcast')
        
        # Metadatos básicos del feed
        self.fg.title('De Nit - RNE 4')
        self.fg.description(
            'De Nit és el programa nocturn de RNE 4 (Catalunya Ràdio). '
            'Música, tertúlies i molt més durant la nit.'
        )
        self.fg.author({'name': 'RTVE - Ràdio Nacional d\'Espanya'})
        self.fg.link(href='https://www.rtve.es/play/audios/de-nit/', rel='alternate')
        self.fg.link(href='https://raw.githubusercontent.com/sergioedo/rss-la-nit/main/feed.xml', rel='self')
        self.fg.language('ca')
        self.fg.copyright('© RTVE')
        
        # Metadatos de podcast (iTunes)
        self.fg.podcast.itunes_author('RTVE')
        self.fg.podcast.itunes_category('Music')
        self.fg.podcast.itunes_explicit('no')
        self.fg.podcast.itunes_owner(name='RTVE', email='info@rtve.es')
        self.fg.podcast.itunes_summary(
            'De Nit és el programa nocturn de RNE 4. '
            'Feed RSS no oficial generat automàticament.'
        )
        
        # Imagen del podcast
        podcast_image = 'https://img2.rtve.es/imagenes/de-nit/1625484441092.jpg'
        self.fg.image(url=podcast_image, title='De Nit', link='https://www.rtve.es/play/audios/de-nit/')
        self.fg.podcast.itunes_image(podcast_image)
    
    def _parse_duration(self, duration_str: str) -> str:
        """
        Convierte duración ISO 8601 a formato HH:MM:SS.
        
        Args:
            duration_str: Duración en formato ISO 8601 (PT1H2M3S)
            
        Returns:
            Duración en formato HH:MM:SS
        """
        if not duration_str:
            return '00:00:00'
        
        # Parsear formato ISO 8601 (PT1H2M3S)
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)
        
        if match:
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            seconds = int(match.group(3) or 0)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        return '00:00:00'
    
    def _parse_date(self, date_str: str) -> datetime:
        """
        Parsea una fecha en varios formatos posibles.
        
        Args:
            date_str: Fecha como string
            
        Returns:
            Objeto datetime con timezone (UTC)
        """
        if not date_str:
            return datetime.now(timezone.utc)
        
        try:
            dt = date_parser.parse(date_str)
            # Si el datetime no tiene timezone, asignar UTC
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            return datetime.now(timezone.utc)
    
    def add_episode(self, episode_data: Dict):
        """
        Añade un episodio al feed RSS.
        
        Args:
            episode_data: Diccionario con los datos del episodio
        """
        fe = self.fg.add_entry()
        
        # Datos básicos
        title = episode_data.get('title', 'Sin título')
        fe.title(title)
        
        description = episode_data.get('description', '')
        fe.description(description)
        
        # URL del episodio
        episode_url = episode_data.get('url', '')
        if episode_url:
            fe.link(href=episode_url)
        
        # ID único
        episode_id = episode_data.get('id', '')
        guid = episode_url if episode_url else f"de-nit-{episode_id}"
        fe.guid(guid, permalink=True)
        
        # Fecha de publicación
        pub_date = self._parse_date(episode_data.get('pub_date', ''))
        fe.pubDate(pub_date)
        
        # Audio enclosure
        audio_url = episode_data.get('audio_url')
        if audio_url:
            # Determinar tipo MIME
            mime_type = 'audio/mpeg'
            if audio_url.endswith('.m4a'):
                mime_type = 'audio/mp4'
            elif audio_url.endswith('.ogg'):
                mime_type = 'audio/ogg'
            
            fe.enclosure(url=audio_url, type=mime_type, length='0')
        
        # Duración (iTunes)
        duration = episode_data.get('duration', '')
        if duration:
            duration_formatted = self._parse_duration(duration)
            fe.podcast.itunes_duration(duration_formatted)
        
        # Imagen del episodio
        image_url = episode_data.get('image_url')
        if image_url:
            fe.podcast.itunes_image(image_url)
        
        # Autor
        fe.author({'name': 'RTVE'})
    
    def add_episodes(self, episodes: List[Dict]):
        """
        Añade múltiples episodios al feed.
        
        Args:
            episodes: Lista de diccionarios con datos de episodios
        """
        for episode in episodes:
            self.add_episode(episode)
    
    def generate(self, output_file: str = 'feed.xml'):
        """
        Genera el archivo RSS.
        
        Args:
            output_file: Ruta del archivo de salida
        """
        self.fg.rss_file(output_file, pretty=True)
        print(f"✓ Feed RSS generado: {output_file}")


def main():
    """Función principal para generar el RSS."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generador de RSS para De Nit')
    parser.add_argument('--input', type=str, default='episodes.json',
                      help='Archivo JSON con episodios (default: episodes.json)')
    parser.add_argument('--output', type=str, default='feed.xml',
                      help='Archivo RSS de salida (default: feed.xml)')
    
    args = parser.parse_args()
    
    # Cargar episodios
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            episodes = json.load(f)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {args.input}. Ejecuta primero el scraper para generar los datos de episodios.")
        return
    except json.JSONDecodeError:
        print(f"Error: El archivo {args.input} no contiene JSON válido. Verifica que el archivo fue generado correctamente por el scraper.")
        return
    
    if not episodes:
        print("Advertencia: No hay episodios para agregar al feed")
    
    # Generar RSS
    generator = RSSGenerator()
    generator.add_episodes(episodes)
    generator.generate(args.output)
    
    print(f"✓ {len(episodes)} episodios añadidos al feed")


if __name__ == '__main__':
    main()
