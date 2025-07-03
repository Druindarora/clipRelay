import os
import socket
import uuid
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, SubElement
from datetime import datetime
import http.server
import socketserver
import threading

# Config par défaut
PODCAST_FOLDER = None
RSS_FILENAME = "flux.xml"
PORT = 8000

def set_podcast_folder(folder):
    global PODCAST_FOLDER
    PODCAST_FOLDER = folder
    rss_path = os.path.join(PODCAST_FOLDER, RSS_FILENAME)
    if not os.path.exists(rss_path):
        create_empty_rss(rss_path)

def get_podcast_folder():
    return PODCAST_FOLDER

def create_empty_rss(rss_path):
    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = "Podcast ClipRelay"
    SubElement(channel, "link").text = f"http://localhost:{PORT}"
    SubElement(channel, "description").text = "Flux RSS généré par ClipRelay"
    tree = ET.ElementTree(rss)
    tree.write(rss_path, encoding="utf-8", xml_declaration=True)

def update_rss_feed(title, link, mp3_url):
    if not PODCAST_FOLDER:
        return

    rss_path = os.path.join(PODCAST_FOLDER, RSS_FILENAME)
    try:
        tree = ET.parse(rss_path)
        root = tree.getroot()
        channel = root.find("channel")
        if channel is None:
            return

        for item in channel.findall("item"):
            enclosure = item.find("enclosure")
            if enclosure is not None and enclosure.attrib.get("url") == mp3_url:
                return  # Déjà présent

        item = SubElement(channel, "item")
        SubElement(item, "title").text = title
        SubElement(item, "link").text = link
        SubElement(item, "guid").text = str(uuid.uuid4())
        SubElement(item, "pubDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")

        enclosure = SubElement(item, "enclosure")
        enclosure.set("url", mp3_url)
        enclosure.set("type", "audio/mpeg")
        enclosure.set("length", "0")  # temporairement vide

        tree.write(rss_path, encoding="utf-8", xml_declaration=True)
    except Exception:
        pass

def read_rss_feed():
    if not PODCAST_FOLDER:
        return []

    rss_path = os.path.join(PODCAST_FOLDER, RSS_FILENAME)
    if not os.path.exists(rss_path):
        return []

    try:
        tree = ET.parse(rss_path)
        root = tree.getroot()
        items = []
        for item in root.findall("./channel/item"):
            title = item.findtext("title", default="(Sans titre)")
            items.append({"title": title})
        return items
    except Exception:
        return []

def launch_server():
    if is_port_in_use(PORT):
        return True

    try:
        class PodcastHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=PODCAST_FOLDER, **kwargs)

        def run_server():
            with socketserver.TCPServer(("", PORT), PodcastHandler) as httpd:
                httpd.serve_forever()

        threading.Thread(target=run_server, daemon=True).start()
        return True
    except Exception:
        return False

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0
