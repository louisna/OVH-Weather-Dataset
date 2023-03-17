import os
import sys
import dataclasses
from typing import List
from copy import deepcopy, copy

import yaml
from bs4 import BeautifulSoup
from shapely.geometry import Polygon, LineString, Point

from multiprocessing import Pool
import tqdm

import cchardet
import gc

@dataclasses.dataclass
class Node:
    x: float = 0.0  # Left corner coordinate
    y: float = 0.0
    w: float = 0.0
    h: float = 0.0
    name: str = ''
    links: List = dataclasses.field(default_factory=lambda: [])

    def poly(self, is_label=False):
        # Extend a bit the routers to compensate for the rounding errors
        if is_label:
            border = 0
        else:
            border = 1
        x = self.x - border
        y = self.y - border
        w = self.w + (border * 2)
        h = self.h + (border * 2)
        return Polygon([(x, y), (x + w, y), (x + w, y + h), (x, y + h)])

    def __hash__(self) -> int:
        return hash(self.x) + hash(self.y) + hash(self.w) + hash(self.h)


@dataclasses.dataclass
class Link:
    x1: float = -1.0
    y1: float = -1.0
    ld1: int = None
    lb1: str = ''
    n1: Node = None
    x2: float = -1.0
    y2: float = -1.0
    ld2: int = None
    lb2: str = ''
    n2: Node = None
    a1x1: float = 0.0
    a1y1: float = 0.0
    a1x2: float = 0.0
    a1y2: float = 0.0
    a2x1: float = 0.0
    a2y1: float = 0.0
    a2x2: float = 0.0
    a2y2: float = 0.0

    def ax_b(self):
        a = (self.y2 - self.y1) / (self.x2 - self.x1)
        return a, (self.y1 - (a * self.x1))

    def get_y(self, x):
        a, b = self.ax_b()
        return (a * x) + b

    def line(self):
        # Extend a bit the line to create an intersection with the box
        # TODO: make the extension proportional to the length of the line
        extender = 20000  # Extend by few pixels
        x1 = min(self.x1, self.x2) - extender
        x2 = max(self.x1, self.x2) + extender
        y1 = min(self.y1, self.y2) - extender
        y2 = max(self.y1, self.y2) + extender
        # Create a line from the extended points
        if self.x1 != self.x2:
            return LineString([(x1, self.get_y(x1)), (x2, self.get_y(x2))])
        return LineString([(self.x1, y1), (self.x2, y2)])

    def p1(self):
        return Point(self.x1, self.y1)

    def p2(self):
        return Point(self.x2, self.y2)

    def reverse(self):
        l = copy(self)
        l.lb1, l.lb2 = l.lb2, l.lb1
        l.ld1, l.ld2 = l.ld2, l.ld1
        l.n1, l.n2 = l.n2, l.n1
        l.x1, l.x2 = l.x2, l.x1
        l.y1, l.y2 = l.y2, l.y1
        return l

    def __hash__(self):
        return hash((self.x1, self.x2, self.y1, self.y2))


def parse(filepath):
    the_only_filename = int(filepath.split("/")[-1].split("_")[1][:-4])
    if the_only_filename in ALL_YAML_ALREADY: 
        print("Already parsed")
        return
    filepath = os.path.join(directory, filepath)
    with open(filepath) as fd:
        svg = "".join(fd.readlines())
        weathermap = BeautifulSoup(svg, 'lxml')

        links = set()
        nodes = []
        labels = []

        l = None
        label = None
        for e in weathermap.find('svg').children:
            if e.name == 'text':
                if 'labellink' in e.get('class', []):
                    if l.ld1 is None:
                        l.ld1 = int(e.text[:-1])
                        assert l.ld1 >= 0 and l.ld1 <= 100
                    elif l.ld2 is None:
                        l.ld2 = int(e.text[:-1])
                        assert l.ld2 >= 0 and l.ld2 <= 100
                        if l not in links:  # Avoid duplicate lines
                            links.add(l)
                        l = None
                elif 'node' in e.get('class', []):
                    label.name = e.text
                    labels.append(label)
                    label = None
            elif e.name == 'rect':
                if 'labellink' in e.get('class', []):
                    pass
                    #if l is None:
                    #    l = Link(x1=float(e['x']) + (float(e['width']) / 2), y1=float(e['y']) + (float(e['height']) / 2))
                    #else:
                    #    l.x2 = float(e['x']) + (float(e['width']) / 2)
                    #    l.y2 = float(e['y']) + (float(e['height']) / 2)
                elif 'object' in e.get('class', []) or 'object_null' in e.get('class', []):
                    nodes.append(Node(name=e['alt'], x=float(e['x']), y=float(e['y']), w=float(e['width']), h=float(e['height'])))
                elif 'node' in e.get('class', []):
                    label = Node(x=float(e['x']), y=float(e['y']), w=float(e['width']), h=float(e['height']))
            elif e.name == "polygon":  # Arrow representing the link
                points = e["points"].split()  # Array of "(x1, y1)"
                a1 = [float(i) for i in points[0].split(",")]
                a2 = [float(i) for i in points[-1].split(",")]
                if l is None:
                    l = Link(a1x1=a1[0], a1y1=a1[1], a1x2=a2[0], a1y2=a2[1])
                else:
                    l.a2x1 = a1[0]
                    l.a2y1 = a1[1]
                    l.a2x2 = a2[0]
                    l.a2y2 = a2[1]
                    # Compute the pseudo coordinates
                    l.x1 = (l.a1x1 + l.a1x2) / 2
                    l.y1 = (l.a1y1 + l.a1y2) / 2
                    l.x2 = (l.a2x1 + l.a2x2) / 2
                    l.y2 = (l.a2y1 + l.a2y2) / 2

        nodes_poly = [(n, n.poly()) for n in nodes]
        labels_poly = {l: (l, l.poly(is_label=True)) for l in labels}
        for l in links:
            line = l.line()
            intersecting_nodes = [(n, p) for n, p in nodes_poly]# if p.distance(l.p1()) < 50.0 or p.distance(l.p2()) < 50.0]# if p.intersects(line) or p.distance(line) < 10]
            intersecting_labels = [(n, p) for n, p in labels_poly.values()]# if p.distance(l.p1()) < 50.0 or p.distance(l.p2()) < 50.0]# if p.intersects(line) or p.distance(line) < 10]
            
            p1 = l.p1()
            intersecting_nodes = sorted(intersecting_nodes, key=lambda x: x[1].distance(p1))
            l.n1 = intersecting_nodes.pop(0)[0]
            intersecting_labels = sorted(intersecting_labels, key=lambda x: x[1].distance(p1))
            l.lb1 = intersecting_labels.pop(0)[0]
            labels_poly.pop(l.lb1)
            lb1_b = l.lb1
            l.lb1 = l.lb1.name
            l.n1.links.append(l)

            p2 = l.p2()
            l.n2 = sorted(intersecting_nodes, key=lambda x: x[1].distance(p2))[0][0]
            l.lb2 = sorted(intersecting_labels, key=lambda x: x[1].distance(p2))[0][0]
            labels_poly.pop(l.lb2)
            lb2_b = l.lb2
            l.lb2 = l.lb2.name
            l.n2.links.append(l.reverse())

            dist_lb_l = lb2_b.poly().distance(p2) - lb1_b.poly().distance(p1)
            if abs(dist_lb_l) > 100:
                print("Distance is too big:", dist_lb_l)
                print("Label name", lb2_b)
                print(f"Linked the two following routers: {l.n1.name} -- {l.n2.name}")
                print(f"Location of the first label: x={lb1_b.x} y={lb1_b.y} h={lb1_b.h} w={lb1_b.w}")
                print(f"Location of the secon label: x={lb2_b.x} y={lb2_b.y} h={lb2_b.h} w={lb2_b.w}")
                print(f"Form of the line: ({l.x1}, {l.y1}), ({l.x2}, {l.y2})")
                print(f"Location first node: {l.n1.x}, {l.n1.y}, {l.n1.h}, {l.n1.w}")
                print(f"Location secon node: {l.n2.x}, {l.n2.y}, {l.n2.h}, {l.n2.w}")
            assert abs(dist_lb_l) < 100
            
        for l in links:
            if l.n1.name == l.n2.name:
                print(l, "self looping")

        output_yaml = {}
        for n in nodes:
            if n.name not in output_yaml.keys():
                output_yaml[n.name] = {'links': []}
            for l in n.links:
                output_yaml[n.name]['links'].append({'label': l.lb1, 'load': l.ld1, 'peer': l.n2.name})

        file_post = filepath.split("/")[-1]
        
        # Sanity check: each router should at least have a link. Empirically we see that no router is isolated in the network
        for n in nodes:
            assert(len(n.links) > 0)
        
        with open(f"{yaml_directory}/{file_post[:-4]}.yaml", 'w+') as f:
            yaml.dump(output_yaml, f)
        
        gc.collect()


def safe_parse(filepath):
    try:
        parse(filepath)
    except Exception as e:
        import traceback
        print("Unable to parse", filepath, "with exception", e)
        traceback.print_exc()

if __name__ == "__main__":
    directory = sys.argv[1].rstrip(os.path.sep)
    yaml_directory = f"{directory}_yaml"
    os.makedirs(yaml_directory, exist_ok=True)
    ALL_YAML_ALREADY = {int(i[:-5].split("_")[1]) for i in os.listdir(yaml_directory)}
    all_files = os.listdir(directory)
    files_to_process = []
    for rf, filepath in [(int(filepath.split("/")[-1].split("_")[1][:-4]), filepath) for filepath in all_files]:
        if rf not in ALL_YAML_ALREADY:
            files_to_process.append(filepath)

    with Pool(processes=24) as pool:
        for _ in tqdm.tqdm(pool.imap_unordered(safe_parse, files_to_process), total=len(files_to_process)):
            pass
    #safe_parse(files_to_process[0])