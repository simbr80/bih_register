import xml.etree.ElementTree as ET
from datetime import datetime


tree = ET.parse('xml/od15268do44000.xml')
root = tree.getroot()

for child in root:
    print(child.tag, child.attrib)
    print(child.attrib["FBIH_ID"], child.attrib["datum"])
    child.attrib["FBIH_ID"] = str(int(float(child.attrib["FBIH_ID"])))
    if child.attrib["datum"] != "nan":
        date_object = datetime.strptime(child.attrib["datum"], "%d.%m.%Y")
        child.attrib["datum"] = datetime.strftime(date_object, "%Y-%m-%d")
    else:
        child.attrib["datum"] = "1900-01-01"


tree.write('xml/od15268do44000.xml')