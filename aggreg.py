#!/usr/bin/env python3
"""
Ce programme permet le traitement de flux RSS
et la création d'une page web pour un affichage
condensé et formatté des informations de supervision
d'une infrastructure de services informatiques

Ben Yahya
Nolan
"""


import sys
import os

import urllib.request
import feedparser
import yaml
from xml.etree import ElementTree as ET

from time import localtime, strftime, time
from datetime import datetime

import cssutils
import logging
cssutils.log.setLevel(logging.CRITICAL)



def main():
    
    # Variables globales pour utilisation dans toutes les fonctions
    global sort_time
    global servers
    global rss_file
    global destination_file
    global destination_path
            
    # Fichier de config alternatif
    if len(sys.argv) == 2:
        if os.path.exists(sys.argv[1]):
            with open(sys.argv[1], 'r') as conf:
                config = yaml.load(conf, Loader=yaml.FullLoader)
                if ("url" in config["destination"]) or (not (config["destination"].endswith('.html'))) or (config["rss-name"] == "nom_de_fichier" or config["rss-name"].split('.')[-1] != 'xml') or (config["destination"] == "chemin_complet"):
                    print("\n[Aggreg] > Il semblerait qu'il y ait des erreurs dans le fichier de configuration. Merci de le modifier")
                else:
                    # Placement des valeurs de la config dans les variables
                    sort_time = config["tri-chrono"]
                    servers = config["sources"]
                    rss_file = config["rss-name"]
                    destination_file = config["destination"].split('/')[-1]
                    destination_path = '/'.join(str(elem) for elem in config["destination"].split('/')[:-1]) + "/"
                    flux_rss = []
                    for flux in config["sources"]:
                        flux_rss.append(str(flux) + '/' + config["rss-name"])
                    with open(destination_path + destination_file, 'w') as index: 
                        genere_html(fusion_flux(flux_rss, charge_urls(flux_rss)), index)
        else:
            print("\n[Aggreg] > Il semblerait que le fichier de configuration " + str(sys.argv[1]) + " n'existe pas")
        
    # Erreur de syntaxe
    elif len(sys.argv) > 2:
        print("\n[Aggreg] > Syntaxe : aggreg.py [fichier de configuration alternatif]")

    # Fichier de config dans /etc/aggreg/
    else:
        if os.path.exists('/etc/aggreg/config.yml'):
            with open('/etc/aggreg/config.yml', 'r') as conf:
                config = yaml.load(conf, Loader=yaml.FullLoader)
                if ("url" in config["destination"]) or (not (config["destination"].endswith('.html'))) or (config["rss-name"] == "nom_de_fichier" or config["rss-name"].split('.')[-1] != 'xml') or (config["destination"] == "chemin_complet"):
                    print("\n[Aggreg] > Il semblerait qu'il y ait des erreurs dans le fichier de configuration. Merci de le modifier")
                else:
                    # Placement des valeurs de la config dans les variables
                    sort_time = config["tri-chrono"]
                    servers = config["sources"]
                    rss_file = config["rss-name"]
                    destination_file = config["destination"].split('/')[-1]
                    destination_path = '/'.join(str(elem) for elem in config["destination"].split('/')[:-1]) + "/"
                    flux_rss = []
                    for flux in config["sources"]:
                        flux_rss.append(str(flux) + '/' + config["rss-name"])
                    with open(destination_path + destination_file, 'w') as index: 
                        genere_html(fusion_flux(flux_rss, charge_urls(flux_rss)), index)
        else:
            print("\n[Aggreg] > Il semblerait que le fichier de configuration config.yml n'existe pas dans le répetoire /etc/aggreg/")
    
        
def charge_urls(liste_url):
    """Cette fonction permet, via une liste d'URLs rentrée
    via la ligne de commande (liste_url), de vérifier si les pages contenant
    les flux RSS rattachés à ces URLs sont actives et enfin de formater
    ces flux et de les placer un à un dans une liste finale (rss_list)
    """
    rss_list = []
    for i in range(len(liste_url)):
        # Pour chaque URL, si elle est accessible (code = 200),
        # on parse le contenu du fichier RSS qui y est rattaché
        try:
            if urllib.request.urlopen(str(liste_url[i])).getcode() == 200:
                rss_list.append(feedparser.parse(str(liste_url[i])))
            else:
                rss_list.append(None)
        except Exception:
            rss_list.append(None)
    return rss_list


def fusion_flux(liste_url, liste_flux):
    """Cette fonction utilise la liste des URLs de la fonction main
    et la liste des flux de la fonction charge_urls,
    afin de produire une liste (event_list) contenant
    les informations principales de chaque flux (titre, catégorie, serveur,
    date de publication, lien vers le flux et la description de l'événement)
    """
    assert len(liste_url) == len(liste_flux)
    event_list = {'MINOR': [], 'MAJOR': [], 'CRITICAL': []}
    event_list_out = {'MINOR': [], 'MAJOR': [], 'CRITICAL': []}
    dict_rss = {}
    for i in range(len(liste_url)):
        if liste_flux[i] != None:
            # Mise en forme du dictionnaire final*
            # contenant les valeurs intéressantes
            for j in range(len(liste_flux[i]['entries'])):
                dict_rss['titre'] = liste_flux[i]['entries'][j]['title']
                dict_rss['categorie'] = liste_flux[i]['entries'][j]['tags'][0]['term']
                dict_rss['serveur'] = str(servers[i]).split('/')[-1]
                dict_rss['date_publi'] = liste_flux[i]['entries'][j]['published']
                dict_rss['lien'] = str(liste_flux[i]['entries'][j]['guid'])
                dict_rss['guid'] = str(liste_flux[i]['entries'][j]['guid']).split('/')[-1]
                dict_rss['description'] = liste_flux[i]['entries'][j]['summary']
                if dict_rss['categorie'] == 'MINOR':
                    event_list['MINOR'].append(dict_rss)
                elif dict_rss['categorie'] == 'MAJOR':
                    event_list['MAJOR'].append(dict_rss)
                elif dict_rss['categorie'] == 'CRITICAL':
                    event_list['CRITICAL'].append(dict_rss)
                dict_rss = {}
    # Tri par date (ordre du plus récent au plus ancien)
    if sort_time == True:
        event_list_out['MINOR'] = sorted(event_list['MINOR'], key=lambda x:datetime.strptime(x['date_publi'], '%a, %d %b %Y %H:%M'), reverse=True)
        event_list_out['MAJOR'] = sorted(event_list['MAJOR'], key=lambda x:datetime.strptime(x['date_publi'], '%a, %d %b %Y %H:%M'), reverse=True)
        event_list_out['CRITICAL'] = sorted(event_list['CRITICAL'], key=lambda x:datetime.strptime(x['date_publi'], '%a, %d %b %Y %H:%M'), reverse=True)
    # Aucun tri
    else:
        event_list_out['MINOR'] = event_list['MINOR']
        event_list_out['MAJOR'] = event_list['MAJOR']
        event_list_out['CRITICAL'] = event_list['CRITICAL']
        
    # Avoir des listes de même longueur afin de faciliter la suite
    max_length = max(max(len(event_list_out['MINOR']), len(event_list_out['MAJOR'])), len(event_list_out['CRITICAL']))

    event_list_out['MINOR'].extend([''] * (max_length - len(event_list_out['MINOR'])))
    event_list_out['MAJOR'].extend([''] * (max_length - len(event_list_out['MAJOR'])))
    event_list_out['CRITICAL'].extend([''] * (max_length - len(event_list_out['CRITICAL'])))

    return event_list_out


def genere_html(liste_evenements, chemin_html):
    """Cette fonction permet la création d'une page HTML
    prête à être visionnée sur un navigateur,
    rencensant tous les problèmes de tous les serveurs.
    La fonction génère aussi une feuille de style CSS permettant
    la mise en forme de la page HTML et la fonctionnalité responsive.
    """
    
    css = '''
        .titrepage {
            text-align: center;
        }
            
        * {
            box-sizing: border-box;
        }
        
        .banner_minor {
            width: 100%;
            background-color: green;
            color: white;
            text-align: center;
            font-weight: bold;
            padding: inherit;
            border-radius: 22px;
            margin-bottom: 10px;
            font-size: x-large;
        }
        
        .banner_major {
            width: 100%;
            background-color: orange;
            color: white;
            text-align: center;
            font-weight: bold;
            padding: inherit;
            border-radius: 22px;
            margin-bottom: 10px;
            font-size: x-large;
        }
        
        .banner_critical {
            width: 100%;
            background-color: red;
            color: white;
            text-align: center;
            font-weight: bold;
            padding: inherit;
            border-radius: 22px;
            margin-bottom: 10px;
            font-size: x-large;
        }
        
        .column {
            float: left;
            width: 32.9%;
            padding: 10px;
            border-inline: 2px solid black;
            border: 2px solid black;
            border-radius: 10px;
            margin-right: 3px;
            margin-top: 10px;
        }
        
        @media screen and (max-width: 800px) {
            .column {
                width: 100%;
            }
        }
        
        .table {
            margin-top: 5%;
        }
        
        .table:after {
            content: "";
            display: table;
            clear: both;
        }
        
        .event {
            border-top: 2px solid black;
        }
        
        .cat_minor {
            color: green;
            font-weight: bold;
        }
        
        .cat_major {
            color: orange;
            font-weight: bold;
        }
        
        .cat_critical {
            color: red;
            font-weight: bold;
        }
                  
        '''
        
    if not os.path.exists(destination_path + "css"):
        os.mkdir(destination_path + "css")
    with open(destination_path + "css/feed.css", 'w') as css_f:
        sheet = cssutils.parseString(css)
        cssTextDecoded = sheet.cssText.decode('utf-8')
        css_f.write(cssTextDecoded)
    
    events_minor = []
    events_major = []
    events_critical = []
    
    for categorie in liste_evenements.keys():
        # len(liste_evenements['MINOR']) utilisé purement par défaut
        # (MAJOR ou CRITICAL peuvent être utilisées pour le même résultat.
        # Cf. fusion_flux)
        for i in range(len(liste_evenements['MINOR'])):
            if liste_evenements[categorie][i] != '':
                
                # Un article par événement
                article = ['<article class="event">'
                               '<header>'
                                   '<h2>',liste_evenements[categorie][i]['titre'],'</h2>'
                               '</header>'
                               '<p>from: ',liste_evenements[categorie][i]['serveur'],'</p>'
                               '<p>',liste_evenements[categorie][i]['date_publi'],'</p>'
                               '<p class="cat_',categorie.lower(),'">',liste_evenements[categorie][i]['categorie'],'</p>'
                               '<p>',liste_evenements[categorie][i]['guid'],'</p>'
                               '<p><a href="',liste_evenements[categorie][i]['lien'],'">',liste_evenements[categorie][i]['lien'],'</a></p>'
                               '<p>',liste_evenements[categorie][i]['description'],'</p>'
                          '</article>']
                
                locals()["events_" + str(categorie).lower()].extend(article)
    
    # Tableau complet des événements
    events = ['<div class="table">'
                  '<div class="column">',
                      '<div class="banner_minor"><p>Minor</p></div>',
                      ''.join(str(elem) for elem in events_minor),
                  '</div>'
                  '<div class="column">',
                      '<div class="banner_major"><p>Major</p></div>',
                      ''.join(str(elem) for elem in events_major),
                  '</div>'
                  '<div class="column">',
                      '<div class="banner_critical"><p>Critical</p></div>',
                      ''.join(str(elem) for elem in events_critical),
                  '</div>'
              '</div>']
    
    # Page HTML complète
    page = ['<!DOCTYPE html>'
            '<html>'
                '<head>'
                    '<meta charset="utf-8" />'
                    '<meta name="viewport" content="width=device-width, initial-scale=1" />'
                    '<title>Events log</title>'
                    '<link rel="stylesheet" href="css/feed.css" type="text/css" />'
                '</head>'
                '<article>'
                    '<header class="titrepage">'
                        '<h1>Events log</h1>'
                        '<p>',strftime("%a, %d %b %Y %H:%M:%S %Z", localtime(time())),'</p>'
                    '</header>',
                    ''.join(str(elem) for elem in events),
                '</article>'
            '</html>']
    
    ET.ElementTree(ET.fromstring(''.join(str(elem) for elem in page))).write(chemin_html, encoding='unicode', method='html')




if __name__ == '__main__':
    main()