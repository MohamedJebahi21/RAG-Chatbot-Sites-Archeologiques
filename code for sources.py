"""
Script de collecte et préparation de données sur les sites archéologiques tunisiens
Version étendue - Collecte 50+ documents depuis sources fiables
Sortie: fichiers .txt structurés
"""

import json
import time
from datetime import datetime
from urllib.parse import quote
import re
import os

try:
    import requests
except ImportError:
    print("Module 'requests' non trouvé. Installation...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

class HeritageDataCollector:
    def __init__(self):
        self.sites = [
            "Carthage", "Dougga", "El Djem", "Kairouan", "Sbeitla",
            "Carthage Punique", "Matmata", "Thuburbo Majus",
            "Musée National du Bardo", "Kerkouane", "Uthina",
            "Maktar", "Nefta", "Medina of Tunis", "Hadrumetum",
            "Bulla Regia", "Chemtou", "Sufetula", "Monastir"
        ]
        self.documents = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.document_counter = 0
    
    def collect_wikipedia_data(self, site_name, lang='en'):
        """Collecte des données depuis Wikipédia"""
        try:
            lang_prefix = 'en' if lang == 'en' else 'fr'
            url = f"https://{lang_prefix}.wikipedia.org/api/rest_v1/page/summary/{quote(site_name)}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 404:
                url = f"https://{lang_prefix}.wikipedia.org/api/rest_v1/page/summary/{quote(site_name)}_Tunisia"
                response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                content = data.get('extract', '')
                cleaned_content = self.clean_text(content)
                
                if len(cleaned_content) < 100:
                    return None
                
                self.document_counter += 1
                doc = {
                    'doc_id': self.document_counter,
                    'title': data.get('title', site_name),
                    'site': site_name,
                    'source': f'Wikipedia {lang.upper()}',
                    'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                    'content': cleaned_content,
                    'sections': self.extract_sections(cleaned_content),
                    'timestamp': datetime.now().isoformat(),
                    'period': self._extract_period(cleaned_content),
                    'type': 'encyclopedia',
                    'language': lang,
                    'word_count': len(cleaned_content.split())
                }
                return doc
        except Exception as e:
            print(f"  ✗ Erreur Wikipedia {lang.upper()} pour {site_name}: {e}")
        return None
    
    def collect_wikidata_info(self, site_name):
        """Collecte des informations depuis Wikidata"""
        try:
            # Recherche dans Wikidata
            search_url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={quote(site_name)}&language=en&format=json"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('search'):
                    entity = data['search'][0]
                    description = entity.get('description', '')
                    label = entity.get('label', site_name)
                    
                    if description:
                        self.document_counter += 1
                        content = f"{label}: {description}"
                        doc = {
                            'doc_id': self.document_counter,
                            'title': f"Wikidata - {label}",
                            'site': site_name,
                            'source': 'Wikidata',
                            'url': f"https://www.wikidata.org/wiki/{entity.get('id', '')}",
                            'content': content,
                            'sections': [{'title': 'Description', 'content': [description]}],
                            'timestamp': datetime.now().isoformat(),
                            'period': self._extract_period(description),
                            'type': 'structured_data',
                            'language': 'en',
                            'word_count': len(content.split())
                        }
                        return doc
        except Exception as e:
            print(f"  ✗ Erreur Wikidata pour {site_name}: {e}")
        return None
    
    def collect_wikivoyage_data(self, site_name, lang='en'):
        """Collecte des données depuis Wikivoyage"""
        try:
            lang_prefix = 'en' if lang == 'en' else 'fr'
            url = f"https://{lang_prefix}.wikivoyage.org/api/rest_v1/page/summary/{quote(site_name)}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                content = data.get('extract', '')
                cleaned_content = self.clean_text(content)
                
                if len(cleaned_content) > 100:
                    self.document_counter += 1
                    doc = {
                        'doc_id': self.document_counter,
                        'title': f"Wikivoyage - {data.get('title', site_name)}",
                        'site': site_name,
                        'source': f'Wikivoyage {lang.upper()}',
                        'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                        'content': cleaned_content,
                        'sections': self.extract_sections(cleaned_content),
                        'timestamp': datetime.now().isoformat(),
                        'period': self._extract_period(cleaned_content),
                        'type': 'travel_guide',
                        'language': lang,
                        'word_count': len(cleaned_content.split())
                    }
                    return doc
        except Exception as e:
            print(f"  ✗ Erreur Wikivoyage {lang.upper()} pour {site_name}: {e}")
        return None
    
    def generate_synthetic_heritage_doc(self, site_name):
        """Génère un document basé sur les connaissances générales des sites tunisiens"""
        heritage_info = {
            "Carthage": "Ancient Phoenician city-state and later Roman city. Major archaeological site with ruins of temples, baths, and villas. Founded in 814 BCE by Phoenician colonists. Destroyed and rebuilt by Romans. UNESCO World Heritage Site.",
            "Dougga": "Best-preserved Roman town in North Africa. Features Capitol, theater, temples, and houses. Ancient Thugga was a Numidian, Punic and Roman settlement. UNESCO World Heritage Site since 1997.",
            "El Djem": "Contains one of the most impressive Roman amphitheaters in the world. Built in the 3rd century AD. Capacity of 35,000 spectators. UNESCO World Heritage Site.",
            "Kairouan": "Fourth holiest city in Islam. Founded in 670 AD. Great Mosque of Kairouan is architectural masterpiece. UNESCO World Heritage Site.",
            "Sbeitla": "Ancient Roman city of Sufetula. Features three temples, triumphal arch, and Byzantine churches. Important archaeological site from Roman period.",
            "Matmata": "Troglodyte village with underground dwellings. Traditional Berber architecture. Famous for Star Wars filming location.",
            "Thuburbo Majus": "Ancient Roman city with Capitol, forum, and thermal baths. Rich mosaics and architectural remains.",
            "Kerkouane": "Only Punic city never rebuilt by Romans. Unique example of Phoenician-Punic architecture. UNESCO World Heritage Site.",
            "Medina of Tunis": "Historic old city with Islamic architecture, souks, and monuments. Founded in 698 AD. UNESCO World Heritage Site."
        }
        
        info = heritage_info.get(site_name, f"Important archaeological and heritage site in Tunisia with historical significance.")
        
        if info != heritage_info.get(site_name, ""):
            self.document_counter += 1
            doc = {
                'doc_id': self.document_counter,
                'title': f"Heritage Overview - {site_name}",
                'site': site_name,
                'source': 'Heritage Documentation',
                'url': '',
                'content': info,
                'sections': [{'title': 'Overview', 'content': [info]}],
                'timestamp': datetime.now().isoformat(),
                'period': self._extract_period(info),
                'type': 'heritage_documentation',
                'language': 'en',
                'word_count': len(info.split())
            }
            return doc
        return None
    
    def _extract_period(self, text):
        """Extrait la période historique du texte"""
        periods = {
            'Punique': ['punic', 'punique', 'carthaginian', 'carthaginois', 'phénicien', 'phoenician'],
            'Romain': ['roman', 'romain', 'rome'],
            'Byzantin': ['byzantine', 'byzantin'],
            'Islamique': ['islamic', 'islamique', 'arab', 'arabe', 'muslim'],
            'Berbère': ['berber', 'berbère', 'amazigh']
        }
        
        text_lower = text.lower()
        found_periods = []
        
        for period, keywords in periods.items():
            if any(keyword in text_lower for keyword in keywords):
                found_periods.append(period)
        
        return ', '.join(found_periods) if found_periods else 'Non spécifié'
    
    def clean_text(self, text):
        """Nettoie et structure le texte"""
        if not text:
            return ""
        
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\[\d+\]', '', text)
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = text.strip()
        
        return text
    
    def extract_sections(self, text):
        """Extrait les sections du texte"""
        sections = []
        section_patterns = [
            r'(?:Histoire|History)[:.\s]',
            r'(?:Architecture|Architecture)[:.\s]',
            r'(?:Description|Description)[:.\s]',
            r'(?:Patrimoine|Heritage)[:.\s]',
            r'(?:Conservation|Conservation)[:.\s]',
            r'(?:Géographie|Geography)[:.\s]'
        ]
        
        paragraphs = text.split('.')
        current_section = {'title': 'Introduction', 'content': []}
        
        for para in paragraphs:
            para = para.strip()
            if not para or len(para) < 10:
                continue
            
            is_section = False
            for pattern in section_patterns:
                if re.match(pattern, para, re.IGNORECASE):
                    if current_section['content']:
                        sections.append(current_section)
                    current_section = {'title': para[:50], 'content': []}
                    is_section = True
                    break
            
            if not is_section:
                current_section['content'].append(para)
        
        if current_section['content']:
            sections.append(current_section)
        
        if not sections and text:
            sections = [{'title': 'Contenu principal', 'content': [text]}]
        
        return sections
    
    def collect_all_data(self):
        """Collecte les données pour tous les sites depuis multiples sources"""
        print("=" * 70)
        print("COLLECTEUR DE DONNÉES - SITES PATRIMONIAUX TUNISIENS")
        print("Objectif: 50+ documents depuis sources fiables")
        print("=" * 70)
        
        for i, site in enumerate(self.sites, 1):
            print(f"\n[{i}/{len(self.sites)}] Collecte pour: {site}")
            print("-" * 70)
            
            # Wikipedia EN
            doc = self.collect_wikipedia_data(site, 'en')
            if doc:
                self.documents.append(doc)
                print(f"  ✓ Wikipedia EN - Doc #{doc['doc_id']} ({doc['word_count']} mots)")
            
            time.sleep(0.5)
            
            # Wikipedia FR
            doc = self.collect_wikipedia_data(site, 'fr')
            if doc:
                self.documents.append(doc)
                print(f"  ✓ Wikipedia FR - Doc #{doc['doc_id']} ({doc['word_count']} mots)")
            
            time.sleep(0.5)
            
            # Wikidata
            doc = self.collect_wikidata_info(site)
            if doc:
                self.documents.append(doc)
                print(f"  ✓ Wikidata - Doc #{doc['doc_id']}")
            
            time.sleep(0.5)
            
            # Wikivoyage EN
            doc = self.collect_wikivoyage_data(site, 'en')
            if doc:
                self.documents.append(doc)
                print(f"  ✓ Wikivoyage EN - Doc #{doc['doc_id']} ({doc['word_count']} mots)")
            
            time.sleep(0.5)
            
            # Wikivoyage FR
            doc = self.collect_wikivoyage_data(site, 'fr')
            if doc:
                self.documents.append(doc)
                print(f"  ✓ Wikivoyage FR - Doc #{doc['doc_id']} ({doc['word_count']} mots)")
            
            # Document synthétique
            doc = self.generate_synthetic_heritage_doc(site)
            if doc:
                self.documents.append(doc)
                print(f"  ✓ Heritage Doc - Doc #{doc['doc_id']}")
        
        print("\n" + "=" * 70)
        print(f"✓ COLLECTE TERMINÉE: {len(self.documents)} documents collectés")
        print("=" * 70)
        return self.documents
    
    def save_to_txt_files(self, output_dir='corpus_txt'):
        """Sauvegarde chaque document dans un fichier .txt séparé"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        print(f"\n📁 Création des fichiers .txt dans '{output_dir}/'...")
        
        for doc in self.documents:
            # Nom de fichier sûr
            safe_title = re.sub(r'[^\w\s-]', '', doc['title'])
            safe_title = re.sub(r'[-\s]+', '_', safe_title)
            filename = f"{output_dir}/doc_{doc['doc_id']:03d}_{safe_title[:50]}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                # En-tête structuré
                f.write("=" * 80 + "\n")
                f.write(f"DOCUMENT #{doc['doc_id']}\n")
                f.write("=" * 80 + "\n\n")
                
                # Métadonnées
                f.write("MÉTADONNÉES:\n")
                f.write("-" * 80 + "\n")
                f.write(f"Titre: {doc['title']}\n")
                f.write(f"Site: {doc['site']}\n")
                f.write(f"Période: {doc.get('period', 'Non spécifié')}\n")
                f.write(f"Source: {doc['source']}\n")
                f.write(f"Type: {doc.get('type', 'N/A')}\n")
                f.write(f"Langue: {doc.get('language', 'N/A')}\n")
                f.write(f"URL: {doc.get('url', 'N/A')}\n")
                f.write(f"Date de collecte: {doc['timestamp']}\n")
                f.write(f"Nombre de mots: {doc.get('word_count', 0)}\n")
                f.write("-" * 80 + "\n\n")
                
                # Contenu
                f.write("CONTENU:\n")
                f.write("=" * 80 + "\n\n")
                f.write(doc['content'])
                f.write("\n\n")
                
                # Sections
                if doc.get('sections'):
                    f.write("\n" + "=" * 80 + "\n")
                    f.write("SECTIONS:\n")
                    f.write("=" * 80 + "\n\n")
                    for section in doc['sections']:
                        f.write(f"\n[{section['title']}]\n")
                        f.write("-" * 80 + "\n")
                        for content in section['content']:
                            f.write(f"{content}\n")
        
        print(f"✓ {len(self.documents)} fichiers .txt créés dans '{output_dir}/'")
    
    def save_master_txt(self, filename='corpus_master.txt'):
        """Sauvegarde tous les documents dans un seul fichier .txt maître"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("CORPUS COMPLET - SITES PATRIMONIAUX TUNISIENS\n")
            f.write("=" * 80 + "\n")
            f.write(f"Total documents: {len(self.documents)}\n")
            f.write(f"Date de création: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n\n")
            
            for doc in self.documents:
                f.write("\n\n" + "=" * 80 + "\n")
                f.write(f"DOCUMENT #{doc['doc_id']}: {doc['title']}\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"Site: {doc['site']}\n")
                f.write(f"Période: {doc.get('period', 'Non spécifié')}\n")
                f.write(f"Source: {doc['source']}\n")
                f.write(f"URL: {doc.get('url', 'N/A')}\n\n")
                f.write("-" * 80 + "\n\n")
                f.write(doc['content'])
                f.write("\n\n")
        
        print(f"✓ Corpus maître sauvegardé dans '{filename}'")
    
    def generate_report(self):
        """Génère un rapport détaillé de la collecte"""
        print("\n" + "=" * 70)
        print("RAPPORT DÉTAILLÉ DE COLLECTE")
        print("=" * 70)
        print(f"\nTotal documents collectés: {len(self.documents)}")
        
        # Par site
        sites_count = {}
        for doc in self.documents:
            site = doc['site']
            sites_count[site] = sites_count.get(site, 0) + 1
        
        print(f"\nDocuments par site:")
        for site, count in sorted(sites_count.items()):
            print(f"  - {site}: {count} document(s)")
        
        # Par source
        sources_count = {}
        for doc in self.documents:
            source = doc['source']
            sources_count[source] = sources_count.get(source, 0) + 1
        
        print(f"\nDocuments par source:")
        for source, count in sorted(sources_count.items()):
            print(f"  - {source}: {count} document(s)")
        
        # Statistiques
        total_words = sum(doc.get('word_count', 0) for doc in self.documents)
        print(f"\nStatistiques:")
        print(f"  - Nombre total de mots: {total_words:,}")
        print(f"  - Moyenne de mots par document: {total_words // len(self.documents) if self.documents else 0}")
        
        print("=" * 70)

# Utilisation
if __name__ == "__main__":
    collector = HeritageDataCollector()
    
    # Collecte
    collector.collect_all_data()
    
    # Sauvegarde en .txt
    collector.save_to_txt_files('corpus_txt')
    collector.save_master_txt('corpus_master.txt')
    
    # Rapport
    collector.generate_report()
    
    print("\n✓ SCRIPT TERMINÉ AVEC SUCCÈS!")
    print(f"✓ Fichiers générés:")
    print(f"  - corpus_txt/ (dossier avec {len(collector.documents)} fichiers .txt)")
    print(f"  - corpus_master.txt (fichier maître)")