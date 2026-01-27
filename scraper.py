#!/usr/bin/env python3
"""
Scraper para extraer información de episodios del podcast "De Nit" de RTVE.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin


class DeNitScraper:
    """Scraper para el programa De Nit de RTVE."""
    
    BASE_URL = "https://www.rtve.es"
    PROGRAM_URL = "https://www.rtve.es/play/audios/de-nit/"
    
    def __init__(self, delay: float = 1.0):
        """
        Inicializa el scraper.
        
        Args:
            delay: Tiempo de espera entre peticiones (en segundos)
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; RSSFeedBot/1.0; +https://github.com/sergioedo/rss-la-nit)'
        })
    
    def _extract_json_data(self, soup: BeautifulSoup) -> Optional[Dict]:
        """
        Extrae datos JSON embebidos en la página.
        
        Args:
            soup: BeautifulSoup object de la página
            
        Returns:
            Diccionario con los datos JSON o None
        """
        # Buscar script tags con datos JSON
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if data.get('@type') in ['AudioObject', 'Episode', 'PodcastEpisode']:
                    return data
            except (json.JSONDecodeError, AttributeError):
                continue
        return None
    
    def _extract_audio_url(self, soup: BeautifulSoup, episode_id: str) -> Optional[str]:
        """
        Extrae la URL del archivo de audio.
        
        Args:
            soup: BeautifulSoup object de la página
            episode_id: ID del episodio
            
        Returns:
            URL del audio o None
        """
        # Intentar extraer de JSON embebido
        json_data = self._extract_json_data(soup)
        if json_data and 'contentUrl' in json_data:
            return json_data['contentUrl']
        
        # Intentar obtener desde la API de RTVE
        try:
            api_url = f"https://www.rtve.es/api/audios/{episode_id}.json"
            response = self.session.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Buscar URL de audio en diferentes campos posibles
                if 'page' in data and 'items' in data['page']:
                    for item in data['page']['items']:
                        if 'url' in item:
                            return item['url']
                        if 'audioUrl' in item:
                            return item['audioUrl']
        except Exception as e:
            print(f"Error al obtener audio desde API para episodio {episode_id}: {e}")
        
        return None
    
    def get_episode_details(self, episode_url: str) -> Optional[Dict]:
        """
        Obtiene los detalles de un episodio específico.
        
        Args:
            episode_url: URL del episodio
            
        Returns:
            Diccionario con los datos del episodio o None
        """
        try:
            # Esperar para no saturar el servidor
            time.sleep(self.delay)
            
            response = self.session.get(episode_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer ID del episodio de la URL
            episode_id = episode_url.rstrip('/').split('/')[-1]
            
            # Extraer datos JSON embebidos
            json_data = self._extract_json_data(soup)
            
            # Título
            title = None
            if json_data and 'name' in json_data:
                title = json_data['name']
            else:
                title_tag = soup.find('h1', class_='title') or soup.find('h1')
                title = title_tag.text.strip() if title_tag else None
            
            # Descripción
            description = None
            if json_data and 'description' in json_data:
                description = json_data['description']
            else:
                desc_tag = soup.find('meta', {'name': 'description'})
                if desc_tag:
                    description = desc_tag.get('content', '').strip()
            
            # Fecha de publicación
            pub_date = None
            if json_data and 'uploadDate' in json_data:
                pub_date = json_data['uploadDate']
            else:
                date_tag = soup.find('time')
                if date_tag:
                    pub_date = date_tag.get('datetime', '')
            
            # Duración
            duration = None
            if json_data and 'duration' in json_data:
                duration = json_data['duration']
            
            # Imagen/thumbnail
            image_url = None
            if json_data and 'thumbnailUrl' in json_data:
                image_url = json_data['thumbnailUrl']
            else:
                img_tag = soup.find('meta', {'property': 'og:image'})
                if img_tag:
                    image_url = img_tag.get('content', '')
            
            # URL del audio
            audio_url = self._extract_audio_url(soup, episode_id)
            
            if not title:
                print(f"Error: No se pudo extraer el título del episodio desde {episode_url}. El episodio será omitido.")
                return None
            
            episode_data = {
                'id': episode_id,
                'url': episode_url,
                'title': title,
                'description': description or '',
                'pub_date': pub_date,
                'duration': duration,
                'image_url': image_url,
                'audio_url': audio_url
            }
            
            return episode_data
            
        except Exception as e:
            print(f"Error al procesar episodio {episode_url}: {e}. Saltando al siguiente episodio.")
            return None
    
    def get_episodes_list(self, max_episodes: int = 50) -> List[Dict]:
        """
        Obtiene la lista de episodios del programa.
        
        Args:
            max_episodes: Número máximo de episodios a obtener
            
        Returns:
            Lista de diccionarios con datos de episodios
        """
        episodes = []
        
        try:
            # Obtener la página principal del programa
            response = self.session.get(self.PROGRAM_URL, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar enlaces a episodios
            episode_links = []
            
            # Buscar en diferentes patrones posibles
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/play/audios/de-nit/' in href and href != self.PROGRAM_URL:
                    full_url = urljoin(self.BASE_URL, href)
                    if full_url not in episode_links:
                        episode_links.append(full_url)
            
            # Limitar al número máximo de episodios
            episode_links = episode_links[:max_episodes]
            
            print(f"Encontrados {len(episode_links)} episodios")
            
            # Obtener detalles de cada episodio
            for i, episode_url in enumerate(episode_links):
                print(f"Procesando episodio {i+1}/{len(episode_links)}: {episode_url}")
                episode_data = self.get_episode_details(episode_url)
                if episode_data:
                    episodes.append(episode_data)
            
        except Exception as e:
            print(f"Error al obtener lista de episodios: {e}")
        
        return episodes


def main():
    """Función principal para ejecutar el scraper."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scraper para De Nit de RTVE')
    parser.add_argument('--max-episodes', type=int, default=50,
                      help='Número máximo de episodios a obtener (default: 50)')
    parser.add_argument('--output', type=str, default='episodes.json',
                      help='Archivo de salida JSON (default: episodes.json)')
    parser.add_argument('--delay', type=float, default=1.0,
                      help='Delay entre peticiones en segundos (default: 1.0)')
    
    args = parser.parse_args()
    
    scraper = DeNitScraper(delay=args.delay)
    episodes = scraper.get_episodes_list(max_episodes=args.max_episodes)
    
    # Guardar resultados
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(episodes, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ {len(episodes)} episodios guardados en {args.output}")


if __name__ == '__main__':
    main()
