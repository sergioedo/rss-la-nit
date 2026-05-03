#!/usr/bin/env python3
"""
Scraper para extraer información de episodios del podcast "De Nit" de RTVE.
"""

import html
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
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if data.get('@type') in ['AudioObject', 'Episode', 'PodcastEpisode', 'RadioEpisode']:
                    return data
            except (json.JSONDecodeError, AttributeError):
                continue
        return None
    
    def _extract_audio_url(self, soup: BeautifulSoup, episode_id: str) -> Optional[str]:
        json_data = self._extract_json_data(soup)
        if json_data and 'contentUrl' in json_data:
            content_url = json_data['contentUrl']
            if content_url and not content_url.endswith('/'):
                return content_url
        
        try:
            api_url = f"https://api2.rtve.es/api/audios/{episode_id}.json"
            response = self.session.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'page' in data and 'items' in data['page'] and len(data['page']['items']) > 0:
                    item = data['page']['items'][0]
                    if 'qualities' in item and len(item['qualities']) > 0:
                        return item['qualities'][0].get('filePath')
        except Exception as e:
            print(f"Error al obtener audio desde API para episodio {episode_id}: {e}")
        
        return None
    
    def _fetch_api_data(self, episode_id: str) -> Optional[Dict]:
        try:
            api_url = f"https://api2.rtve.es/api/audios/{episode_id}.json"
            response = self.session.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'page' in data and 'items' in data['page'] and len(data['page']['items']) > 0:
                    return data['page']['items'][0]
        except Exception as e:
            print(f"Error al obtener datos desde API para episodio {episode_id}: {e}")
        return None

    def get_episode_details(self, episode_url: str) -> Optional[Dict]:
        try:
            time.sleep(self.delay)
            
            response = self.session.get(episode_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            episode_id = episode_url.rstrip('/').split('/')[-1]
            
            json_data = self._extract_json_data(soup)
            api_data = self._fetch_api_data(episode_id)
            
            title = None
            if json_data and 'name' in json_data:
                title = html.unescape(json_data['name'])
            elif api_data and 'title' in api_data:
                title = html.unescape(api_data['title'])
            else:
                title_tag = soup.find('h1', class_='title') or soup.find('h1')
                title = title_tag.text.strip() if title_tag else None
            
            description = None
            if json_data and 'audio' in json_data and isinstance(json_data['audio'], list) and len(json_data['audio']) > 0 and 'description' in json_data['audio'][0]:
                description = html.unescape(json_data['audio'][0]['description'])
            elif api_data and 'description' in api_data:
                description = html.unescape(re.sub(r'<[^>]+>', '', api_data['description']))
            elif json_data and 'description' in json_data:
                description = html.unescape(json_data['description'])
            else:
                desc_tag = soup.find('meta', {'name': 'description'})
                if desc_tag:
                    description = desc_tag.get('content', '').strip()
            
            pub_date = None
            if json_data and 'audio' in json_data and isinstance(json_data['audio'], list) and len(json_data['audio']) > 0:
                pub_date = json_data['audio'][0].get('uploadDate')
            elif json_data and 'publication' in json_data and isinstance(json_data['publication'], list) and len(json_data['publication']) > 0:
                pub_date = json_data['publication'][0].get('startDate')
            elif api_data and 'publicationDate' in api_data:
                pub_date = api_data['publicationDate']
            else:
                date_tag = soup.find('time')
                if date_tag:
                    pub_date = date_tag.get('datetime', '')
            
            duration = None
            if json_data and 'audio' in json_data and isinstance(json_data['audio'], list) and len(json_data['audio']) > 0:
                duration = json_data['audio'][0].get('duration')
            elif api_data and 'duration' in api_data:
                duration_ms = api_data['duration']
                if duration_ms:
                    seconds = int(duration_ms) // 1000
                    hours = seconds // 3600
                    minutes = (seconds % 3600) // 60
                    secs = seconds % 60
                    duration = f"PT{hours}H{minutes}M{secs}S"
            
            image_url = None
            if json_data and 'image' in json_data:
                image_url = json_data['image']
            elif api_data and 'imageSEO' in api_data:
                image_url = api_data['imageSEO']
            elif json_data and 'audio' in json_data and isinstance(json_data['audio'], list) and len(json_data['audio']) > 0:
                image_url = json_data['audio'][0].get('thumbnailUrl')
            else:
                img_tag = soup.find('meta', {'property': 'og:image'})
                if img_tag:
                    image_url = img_tag.get('content', '')
            
            audio_url = None
            if api_data and 'qualities' in api_data and len(api_data['qualities']) > 0:
                audio_url = api_data['qualities'][0].get('filePath')
            if not audio_url:
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
