# Présentation

aggreg.py est un agrégateur de flux RSS de gestion des services présents sur les machines d'un parc informatique.

Il prend en entrée des adresses pointant vers des fichiers XML contenant des flux d'événements et retourne une page web où toutes les informations importantes des événements y sont répertoriées.

Les événements sont, à terme, classés en trois catégories : **MINOR**, **MAJOR** et **CRITICAL**.

# Installation

## Prérequis

Non installés par défaut avec Python3 !

- **Python3.9 minimum**
- **pip3** > `apt install python3-pip`
- **feedparser** > `pip install feedparser`
- **PyYaml** > `pip install pyyaml`
- **cssutils** > `pip install cssutils`

# Utilisation

## Flux RSS

aggreg.py réceptionne des flux RSS qui doivent **absolument** contenir (parce que c'est ce que le programme traite et formate) :
- Dans l'entête du flux :
    - Un titre général : **title**
    - Un lien direct vers le flux : **link**
- Dans chaque **item** correspondant à un événement :
    - Le titre de l'événement : **title**
    - La catégorie de l'événement (**MINOR**, **MAJOR** ou **CRITICAL**) : **category**
    - Le gui unique de l'événement : **guid**
    - La decription de l'événement : **description**
    - La date de publication de l'événement : **pubDate** (doit absolument être écrite au format [RFC 822](https://datatracker.ietf.org/doc/html/rfc822 "RFC 822"))

Idéalement, le flux RSS devrait ressembler à ceci (avec autant d'items que d'événements sur le serveur):
```
<rss version="2.0">
    <channel>
        <title>Recent Events for http://serveur1.net/</title>
        <link>http://serveur1.net/rss.xml</link>
        <description>List of recent events.</description>
        <language>en</language>
        <pubDate>Wed, 18 May 2022 10:45 </pubDate>
        <lastBuildDate>Wed, 18 May 2022 10:45 </lastBuildDate>
        <item>
            <title>Quisquam est quaerat voluptatem sed sit.</title>
            <category>MAJOR</category>
            <guid>10cd78e7-9983-4395-812c-70f3474cfe9d</guid>
            <link>http://serveur1.net/10cd78e7-9983-4395-812c-70f3474cfe9d.html</link>
            <description>Dolorem est non non porro. Numquam velit amet tempora quaerat voluptatem aliquam.</description>
            <pubDate>Fri, 08 Apr 2022 09:37 </pubDate>
        </item>
    </channel>
</rss>
```

## Configuration

aggreg.py est fourni avec un fichier de configuration par défaut qu'il faut placer dans le répertoire **/etc/aggreg/** afin que le programme puisse fonctionner !

Il est important que le compte exécutant aggreg.py ait les droits de lecture de ce fichier de configuration, ainsi que les droits d'écriture dans le répertoire de sortie renseigné !

**Fichier de configuration :**
```
sources:
- url
- url
- url
- ...
rss-name: nom_de_fichier
destination: chemin
tri-chrono: true
```

- Il peut être entré autant d'URLs que voulu dans la partie **sources**. Cependant, elles doivent être inscrites selon ce format : **`http://serveur1.net`** ou **`http://serveur1.net/repertoire`** sans aucun slash à la fin de l'adresse !
- Il est primordial que les flux RSS sur les différents serveurs aient le même nom à placé dans **rss-name** sous la forme : **`fichierRSS.xml`**.
- La **destination** du fichier HTML et du répertoire CSS doit être renseignée via un chemin absolu.
- Il est possible de trier les événements des flux par ordre chronologique. Les événements les plus récents apparaîtront en premier si **tri-chrono** est placé sur **`true`**

Il est possible d'utiliser un **fichier de configuration alternatif** en lançant le programme comme suit : `python3 aggreg.py chemin_config_alternative`.
Autrement, le programme se lance simplement via : `python3 aggreg.py`

# FAQ

- J'utilise les hôtes virtuels d'Apache et je ne parviens pas a récupérer le flux RSS
    - Les hôtes virtuels utilisés, sont-ils bien activés ? Pour activer un hôte virtuel : `a2ensite /etc/apache2/sites-available/hote_virtuel.conf`
    - Les hôtes virtuels par défaut, sont-ils bien désactivés ? Pour désactiver un hôte virtuel : `a2dissite /etc/apache2/sites-available/000-default.conf`

- Les fichiers de flux sont accessibles, mais aggreg.py ne les récupère pas
    - La machine hébergeant aggreg.py peut-elle bien accéder aux fichiers de flux sur les machines distantes ?
    - Les URLs rentrées dans le fichier de configuration sont-elles bien écrites sans slash à leur fin (**`http://serveur1.net`** ou **`http://serveur1.net/repertoire`**) ?
    - Le nom du fichier de flux RSS, est-il bien le même pour tous les serveurs et renseigné dans le fichier de configuration sous la forme : **`fichierRSS.xml`** ?

- aggreg.py ne renvoie pas de page HTML ou de feuille de style CSS
    - Le compte exécutant aggreg.py a-t-il les droits d'écriture nécessaires pour le répertoire de destination renseigné dans le fichier de configuration ?
