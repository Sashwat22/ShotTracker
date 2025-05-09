import xml.etree.ElementTree as ET
import os

class_map = {'ball': 0, 'hoop': 1}

for xml_file in os.listdir('data/raw_frames'):
    if not xml_file.endswith('.xml'): continue
    tree = ET.parse(f'data/raw_frames/{xml_file}')
    root = tree.getroot()
    size = root.find('size')
    w = float(size.find('width').text)
    h = float(size.find('height').text)

    lines = []
    for obj in root.findall('object'):
        cls = obj.find('name').text
        bbox = obj.find('bndbox')
        x1 = float(bbox.find('xmin').text)
        y1 = float(bbox.find('ymin').text)
        x2 = float(bbox.find('xmax').text)
        y2 = float(bbox.find('ymax').text)

        x_center = ((x1+x2)/2) / w
        y_center = ((y1+y2)/2) / h
        bw = (x2-x1) / w
        bh = (y2-y1) / h

        lines.append(f"{class_map[cls]} {x_center:.6f} {y_center:.6f} {bw:.6f} {bh:.6f}")

    txt_path = xml_file.replace('.xml', '.txt')
    with open(f"data/train/labels/{txt_path}", 'w') as f:
        f.write("\n".join(lines))
