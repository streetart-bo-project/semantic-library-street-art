import folium
from rdflib import Graph, Namespace, RDF, RDFS
import re

# 1. CARICA IL FILE .ttl
ttl_path = "final-csv-ttl\final.ttl"
g = Graph()
g.parse(ttl_path, format="turtle")

# 2. DEFINISCI I NAMESPACE USATI NEL TTL
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
SCHEMA = Namespace("https://schema.org/")
DCTERMS = Namespace("http://purl.org/dc/terms/")
RDFS_NS = Namespace("http://www.w3.org/2000/01/rdf-schema#")

# 3. FUNZIONE PER SISTEMARE LE COORDINATE SCRITTE MALE
def fix_coordinate(raw):
    numbers = re.findall(r"\d+", str(raw))
    if len(numbers) >= 2:
        return float(numbers[0] + "." + numbers[1])
    return None

# 4. ESTRAI TUTTI I METADATI PARTENDO DAGLI OGGETTI "item/workX"
data = []

for item_uri in g.subjects(RDF.type, CRM.E22_Man_Made_Object):
    title = None
    author = None
    description = None
    lat = None
    lon = None

    # Titolo
    for title_node in g.objects(item_uri, CRM.P102_has_title):
        for label in g.objects(title_node, RDFS_NS.label):
            title = str(label).strip('"')

    # Autore
    for auth in g.objects(item_uri, DCTERMS.creator):
        author = str(auth).split("/")[-1]

    # Descrizione
    for note in g.objects(item_uri, CRM.P3_has_note):
        description = str(note).strip('"')

    # Coordinate: via location → geo → lat/lon
    for place in g.objects(item_uri, CRM.P53_has_former_or_current_location):
        for geo in g.objects(place, SCHEMA.geo):
            for lat_value in g.objects(geo, SCHEMA.latitude):
                lat = fix_coordinate(lat_value)
            for lon_value in g.objects(geo, SCHEMA.longitude):
                lon = fix_coordinate(lon_value)

    # Se coordinate valide, salva i dati
    if lat and lon:
        data.append({
            "title": title or "Untitled",
            "author": author or "Unknown",
            "description": description or "",
            "lat": lat,
            "lon": lon,
            "uri": str(item_uri)
        })

# 5. CREA LA MAPPA CON FOLIUM
m = folium.Map(location=[44.4949, 11.3426], zoom_start=13)

for item in data:
    popup_html = f"""
    <b>{item['title']}</b><br>
    <i>Author:</i> {item['author']}<br>
    <p>{item['description']}</p>
    <code>{item['uri']}</code>
    """
    folium.Marker(
        location=[item['lat'], item['lon']],
        popup=folium.Popup(popup_html, max_width=400),
        tooltip=item['title']
    ).add_to(m)

# 6. SALVA LA MAPPA HTML
m.save("street_art_bologna_from_ttl.html")
