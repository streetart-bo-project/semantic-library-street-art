import folium
from rdflib import Graph, Namespace, RDF, RDFS
import re
from folium.plugins import Fullscreen

# carico file .ttl
ttl_path = "final-csv-ttl/final(1).ttl"  # Adatta questo percorso se necessario
g = Graph()
g.parse(ttl_path, format="turtle")

#definisco i namespace del ttl
CRM = Namespace("https://www.cidoc-crm.org/")
SCHEMA = Namespace("https://schema.org/")
DCTERMS = Namespace("http://purl.org/dc/terms/")
RDFS_NS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
STRART = Namespace("https://raw.githubusercontent.com/streetart-bo-project/semantic-library-street-art/main/final.ttl#")


#coordinate latitude-longitude
def fix_coordinate(raw):
    try:
        # Rimuove virgolette, tipi RDF, e cast a float
        cleaned = re.sub(r'["<>^a-zA-Z:_]', '', str(raw)).strip()
        return float(cleaned)
    except:
        return None

# estraggo i metadati dagli items- "item/workX"
data = []

for item_uri in g.subjects(RDF.type, CRM["E22_Man-Made_Object"]):
    title = None
    authors = []
    description = None
    lat = None
    lon = None
    place = None
    subject = None
    theme = None
    date = None
    support = None
    condition = None
    work_id = item_uri.split("/")[-1]  # estrae 'work1'
    image =  image = f"website/img/{work_id}.jpg" #f"https://github.com/streetart-bo-project/semantic-library-street-art/raw/main/website/img/{work_id}.jpg"

    


    # Titolo
    for title_node in g.objects(item_uri, CRM.P102_has_title):
        for label in g.objects(title_node, RDFS_NS.label):
            title = str(label).strip('"')

    # Autore
    for auth in g.objects(item_uri, DCTERMS.creator):
        name = str(auth).split("/")[-1]  # estrae "ALice_Pasquini"
        name = name.replace("_", " ").title().strip()
        authors.append(name)

    author_id = authors[0].lower().replace(" ", "_")  # usa il primo autore
    catalog_url = f"website/{author_id}.html" #f"https://github.com/streetart-bo-project/semantic-library-street-art/raw/main/website/{author_id}.html"




    # Descrizione
    for note in g.objects(item_uri, CRM.P3_has_note):
        description = str(note).strip('"')

    # Coordinate: via location → geo → lat/lon
    for place_node in g.objects(item_uri, CRM.P53_has_former_or_current_location):
        for label in g.objects(place_node, RDFS_NS.label):
            place = str(label).strip('"')
        for geo in g.objects(place_node, SCHEMA.geo):
            for lat_value in g.objects(geo, SCHEMA.latitude):
                lat = fix_coordinate(lat_value)
            for lon_value in g.objects(geo, SCHEMA.longitude):
                lon = fix_coordinate(lon_value)

    #subject
    # subject
    for subj in g.objects(item_uri, CRM.P129_is_about):
        label_found = False
    for label in g.objects(subj, RDFS_NS.label):
        subject = str(label)
        label_found = True
    if not label_found:
        subject = str(subj).split("/")[-1].replace("_", " ")


    #theme
    for them in g.objects(item_uri, CRM.P138_represents):
        label_found = False
    for label in g.objects(subj, RDFS_NS.label):
        theme = str(label)
        label_found = True
    if not label_found:
        theme = str(them).split("/")[-1].replace("_", " ")
        
    #date
    for date_value in g.objects(item_uri, SCHEMA.dateCreated):
        date = str(date_value)

    #support
    for supp in g.objects(item_uri, CRM.P46_forms_part_of):
        label_found = False
    for label in g.objects(subj, RDFS_NS.label):
        support = str(label)
        label_found = True
    if not label_found:
        support = str(supp).split("/")[-1].replace("_", " ")

    #condition
    for cond in g.objects(item_uri, CRM.P44_has_condition):
        label_found = False
    for label in g.objects(subj, RDFS_NS.label):
        condition = str(label)
        label_found = True
    if not label_found:
        condition = str(cond).split("/")[-1].replace("_", " ")
    

    # Se coordinate valide, salva i dati
    if lat and lon:
        data.append({
            "title": title or "Untitled",
            "authors": ", ".join(authors) if authors else "Unknown",
            "description": description or "No description",
            "lat": lat,
            "lon": lon,
            "place": place or "",
            "subject": subject or "",
            "theme": theme or "",
            "date": date or "",
            "support": support or "",
            "condition": condition or "",
            "image": image or ""
        })

# creazione mappa con folium
m = folium.Map(location=[44.4949, 11.3426], zoom_start=13.5,  tiles='CartoDB positron') 
Fullscreen().add_to(m)
marker_group = folium.FeatureGroup(name="Artworks")
m.add_child(marker_group)
marker_lookup = {}

for item in data:
    popup_html = f"""
    <div style="font-family: 'Roboto', sans-serif; font-size: 11px; border-radius: 8px;">
    <b>{item['title']}</b><br>
    <img src="{item['image']}" width="200"><br>
    <br>
    <b>Author:</b> {item['authors']}<br>
    <b>Place:</b> {item['place']}<br>
    <b>Subject:</b> {item['subject']}<br>
    <b>Theme:</b> {item['theme']}<br>
    <b>Date:</b> {item['date']}<br>
    <b>Support:</b> {item['support']}<br>
    <b>Condition:</b> {item['condition']}<br>
    <p>{item['description']}</p>
    <b><a href="{catalog_url}" target="_blank">🔗 View details</a></b><br>
    """
    icon = folium.Icon(icon="paint-brush", prefix="fa", color="blue")  # usa FontAwesome
    marker = folium.Marker(
        location=[item['lat'], item['lon']],
        icon=icon,
        popup=folium.Popup(popup_html, max_width=400),
        tooltip=item['title']
    )
    marker.add_to(marker_group)
    marker_lookup[item['title']] = marker



m.save("street_art_bologna_from_ttl.html")
