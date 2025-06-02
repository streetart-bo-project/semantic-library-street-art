import rdflib
from rdflib import Namespace, URIRef, Literal, XSD
from rdflib.namespace import RDF, RDFS, DCTERMS
import pandas as pd

# Namespaces
SCHEMA = Namespace("https://schema.org/")
CRM = Namespace("https://www.cidoc-crm.org/")
STRART = Namespace("https://raw.githubusercontent.com/streetart-bo-project/semantic-library-street-art/main/final.ttl#")

# 创建 RDF 图
g = rdflib.Graph()

# Base URI
base_uri = "https://raw.githubusercontent.com/streetart-bo-project/semantic-library-street-art/main/final.ttl#"

# 绑定命名空间
g.bind("schema", SCHEMA)
g.bind("crm", CRM)
g.bind("rdfs", RDFS)
g.bind("dcterms", DCTERMS)
g.bind("strart", STRART)

# 读取 CSV 文件列表
files_csv = [
   "csv.csv"
]

for file in files_csv:

    df = pd.read_csv(file,delimiter=';')
    uris_dict = dict()

    for _, row in df.iterrows():

        subject = row["subject"]
        predicate = row["predicate"]
        object = row["object"]

        
        if subject not in uris_dict:
            subject_uri = URIRef(base_uri + subject.replace(" ", "_"))
            uris_dict[subject] = subject_uri
        else:
            subject_uri = uris_dict[subject]

    
        if predicate == "rdf:type":
           predicate_uri = RDF.type
        elif predicate == "rdfs:subClassOf":
            predicate_uri = RDFS.subClassOf
        elif predicate == "crm:P2_has_type":
            predicate_uri = CRM.P2_has_type
        elif predicate == "crm:P1_is_identified_by":
            predicate_uri = CRM.P1_is_identified_by
        elif predicate == "rdfs:label":
            predicate_uri = RDFS.label
        elif predicate == "crm:P102_has_title":
            predicate_uri = CRM.P102_has_title
        elif predicate == "crm:P53_has_former_or_current_location":
            predicate_uri = CRM.P53_has_former_or_current_location
        elif predicate == "schema:geo":
            predicate_uri = SCHEMA.geo
        elif predicate == "schema:latitude":
            predicate_uri = SCHEMA.latitude
        elif predicate == "schema:longitude":
            predicate_uri = SCHEMA.longitude
        elif predicate == "dcterms:creator":
            predicate_uri = DCTERMS.creator
        elif predicate == "crm:P129_is_about":
            predicate_uri = CRM.P129_is_about
        elif predicate == "crm:P138_represents":
            predicate_uri = CRM.P138_represents
        elif predicate == "schema:dateCreated":
            predicate_uri = SCHEMA.dateCreated
        elif predicate == "crm:P3_has_note":
            predicate_uri = CRM.P3_has_note
        elif predicate == "crm:P46_forms_part_of":
            predicate_uri = CRM.P46_forms_part_of
        elif predicate == "crm:P44_has_condition":
            predicate_uri = CRM.P44_has_condition
        else:
            print(f"⚠️ Unknown predicate: {predicate}")
            continue

        # 对象值处理
        obj = None

        if predicate_uri == RDF.type:
            # 这里可以补充具体类型映射
            if object.startswith("crm:"):
                obj = URIRef("https://www.cidoc-crm.org/" + object.split(":")[1])
            elif object.startswith("schema:"):
                obj = URIRef("https://schema.org/" + object.split(":")[1])
            elif object.startswith("strart:"):
                obj = URIRef(base_uri + object.split(":")[1])
            else:
                obj = URIRef(object)

        elif predicate_uri in [CRM.P1_is_identified_by, CRM.P102_has_title,
                               CRM.P53_has_former_or_current_location,
                               SCHEMA.geo, CRM.P138_represents,
                               CRM.P46_forms_part_of, CRM.P44_has_condition]:
            # 对象当成资源，生成 URI
            if object not in uris_dict:
                # 生成 URI（没有额外路径，统一用 base_uri）
                obj = URIRef(base_uri + object.replace(" ", "_"))
                uris_dict[object] = obj
            else:
                obj = uris_dict[object]

        elif predicate_uri == SCHEMA.dateCreated:
            # 处理时间，gYear 类型
            obj = Literal(object, datatype=XSD.gYear)

        elif predicate_uri in [RDFS.label, CRM.P3_has_note, DCTERMS.creator]:
            obj = Literal(object, datatype=XSD.string)

        elif predicate_uri in [SCHEMA.latitude, SCHEMA.longitude]:
            try:
                value_float = float(object)
                obj = Literal(value_float, datatype=XSD.float)
            except ValueError:
                obj = Literal(object)

        else:
            # 默认全部当字符串处理
            obj = Literal(object, datatype=XSD.string)

        if obj is None:
            continue

        g.add((subject_uri, predicate_uri, obj))

    print(f"✅ Processed file: {file}")

# 导出 Turtle 文件
turtle_str = g.serialize(format="turtle", encoding="utf-8", base=base_uri)
with open("work3.ttl", "wb") as f:
    f.write(turtle_str)
