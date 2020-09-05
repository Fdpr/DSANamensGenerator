import random
import gui
import xml.etree.ElementTree as Et

namespath = "Res/names.xml"
"""pathname for the names lists"""
genspath = "Res/gens.xml"
"""pathname for the generators tree"""
names = dict()
"""hold all lists of name parts"""
functions = dict()
"""holds all generators"""
tree = dict()
"""Holds hierarchic tree"""


def loadnames() -> dict:
    """Reads all namelists from the names.xml file and packs them into lists. Attributes are automatically applied to
    the names in a format usable for the builder functions. """
    root = Et.parse(namespath).getroot()
    lists = dict()
    for nlist in root:
        listname = nlist.attrib['name']
        lnames = list()
        for name in nlist:
            att: dict = name.attrib
            for k in nlist.attrib.keys():
                if k != "name":
                    att[k] = nlist.attrib[k]
            entry = [name.text, name.attrib]
            lnames.append(entry)
        lists[listname] = lnames
    return lists


def parsegens() -> dict:
    """
    :return: dictionary that holds all functions
    Loads the generators file and constructs all functions from it.
    """
    root = Et.parse(genspath).getroot()
    d = parsecat(root)
    return d


def parsefilter(e) -> dict:
    """
    :type e: Et.Element Parses a filterlist tag and creates the filterfunction. The filterlist tag is an endpoint and
    does not contain children.
    """
    ident = e.attrib['name']
    source = e.attrib['source']
    filters = list()
    n: Et.Element
    for n in e:
        if n.tag == "filter":
            filters.append(n.text)
    f = filterbuilder(source, filters, ident)
    d = {"name": ident, "function": f, "children": None}
    return d


def parsecat(e: Et.Element) -> dict:
    """
    :type e: Et.Element
    Parses a category tag and creates the category function recursively. The category tag must contain children.
    """
    children = list()
    childrennames = list()
    ident = e.attrib['name']
    for n in e:
        d = None
        if n.tag == 'category':
            d = parsecat(n)
        elif n.tag == 'filterlist':
            d = parsefilter(n)
        elif n.tag == 'generator':
            d = parsegenerator(n)
        if d is not None:
            children.append(d)
            childrennames.append(d['name'])
    f = catbuilder(childrennames, ident)
    r = {"name": ident, "function": f, "children": children}
    return r


def parsegenerator(e) -> dict:
    """
    :type e: Et.Element Parses a generator tag and creates the generator function. The generator tag is an endpoint
    and does not contain children.
    """
    ident = e.attrib['name']
    patterns = list()
    weights = list()
    n: Et.Element
    for n in e:
        if n.tag == "pattern":
            patterns.append(n.text)
            weights.append(n.attrib['weight'])
    if 'desc' in e.attrib.keys():
        f = genbuilder(patterns, weights, ident, e.attrib['desc'])
    else:
        f = genbuilder(patterns, weights, ident)
    d = {"name": ident, "function": f, "children": None}
    return d


def filterbuilder(source, filters, ident) -> ():
    """
    :param source: namestring of source generator
    :type source: string
    :param filters: list of filter strings
    :type filters: list[str]
    :param ident: namestring. Generator can be referenced from outer scope by this identifier.
    :type ident: str
    :return: A function that generates a name of the source generator for which all filters apply.
    Builds a filter function, that is: a function which applies a filter to another generator.
    """
    sourcefun = functions[source]
    fmap = dict()
    for s in filters:
        ssplit = s.split(":")
        ssplit.append("")
        fmap[ssplit[0]] = ssplit[1]

    def built() -> (str, dict):
        candidate: (str, dict)
        candidate = sourcefun()
        for tries in range(100):
            possible = True
            for k in fmap.keys():
                if k in candidate[1].keys():
                    if fmap[k] != candidate[1][k] and fmap[k] != "":
                        print("FALSE")
                        possible = False
                else:
                    possible = False
            if possible:
                return candidate
            else:
                candidate = sourcefun()
        return "", dict()

    functions[ident] = built
    return built


def catbuilder(children, ident) -> ():
    """
    :param children: List of names of direct children.
    :type children: list[str]
    :param ident: namestring. Generator can be referenced from outer scope by this identifier.
    :type ident: str
    :return: A function that generates a name of a random child Builds a category function, that is:
    a function that generates a random name from one of its subcategories/subgenerators.
    """
    funs = list()
    for s in children:
        funs.append(functions[s])

    def built() -> (str, dict):
        return random.choice(funs)()

    functions[ident] = built
    return built


def genbuilder(patterns, weights, ident, desc=None) -> ():
    """
    :param patterns: ordered list of patterns from which names are generated
    :type patterns: list[str]
    :param weights: ordered list of weights of the patterns
    :type weights: list[int]
    :param ident: namestring. Generator can be referenced from outer scope by this identifier.
    :type ident: str
    :param desc: Optional name of descriptor function.
    :type desc: str
    :return: A function that generates names according to the weighted patterns.
    Builds a generator function, that is: a function which generates a random name based on a given number
    of weighted patterns.
    """
    funs = list()
    for p in patterns:
        funs.append(patternbuilder(p))
    weightsint = list()
    for w in weights:
        weightsint.append(int(w))

    def built() -> (str, dict):
        res = list(random.choices(funs, weights=weightsint)[0]())
        if desc is not None:
            extra = functions[desc]()
            res[1].update(extra[1])
            res.append(extra[0])
        return res

    functions[ident] = built
    return built


def patternbuilder(pattern):
    """
    returns a function that generates a random name based on a given pattern.
    :type pattern: str
    """
    pattern = pattern.replace("}", "{")
    parts = pattern.split("{")

    def built() -> (str, dict):
        """returns a random name with attributes"""
        attributes = dict()
        name = parts.copy()
        for i in range(len(name)):
            if i % 2 != 0:
                if parts[i].startswith("$"):
                    entry = functions[parts[i].replace("$", "")]()
                else:
                    entry = random.choice(names[parts[i]])
                name[i] = entry[0]
                for att in entry[1]:
                    if att not in attributes.keys():
                        attributes[att] = entry[1][att]
        return str().join(name), attributes
    return built


if __name__ == '__main__':
    names = loadnames()
    tree = parsegens()
    gui.start(tree, functions)
    """patterns = ["{tulamiden_vor_m} ben {tulamiden_vor_m}", "{tulamiden_vor_m}, Töter von {$Weiden Männlich}"]
    weights = [1, 1]
    ident = "Novadi"
    makenames = genbuilder(patterns, weights, ident)
    patterns = ["{weiden_vor_m} {weiden_nach_pre}{weiden_nach_post}"]
    weights = [1]
    ident = "Weiden Männlich"
    genbuilder(patterns, weights, ident)
    for pr in range(1000):
        name, attrib = makenames()
        print(name, str(attrib).replace("{", "").replace("}", "").replace("'", ""), sep=" \t| ")"""
