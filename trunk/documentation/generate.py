#!/usr/bin/python

import os, types, re, inspect

from svgfig.svg import SVG as XML
from svgfig.svg import load

import svgfig, svgfig.interactive
for module in svgfig.__all__: exec("import svgfig.%s" % module)

docs = []
for f in os.listdir("source"):
    if f[0] != "." and f[-4:] == ".xml":
        docs.extend(load("source/%s" % f).children)

def order(a, b, model):
    ai, bi = None, None
    try:
        ai = model.index(a.name)
    except ValueError: pass
    try:
        bi = model.index(b.name)
    except ValueError: pass

    if ai is None and bi is None:
        return cmp((a.module, a.name), (b.module, b.name))
    elif ai is not None and bi is None:
        return -1
    elif ai is None and bi is not None:
        return 1
    else:
        return cmp(ai, bi)

def strorder(a, b, model):
    ai, bi = None, None
    try:
        ai = model.index(a)
    except ValueError: pass
    try:
        bi = model.index(b)
    except ValueError: pass

    if ai is None and bi is None:
        return cmp(a, b)
    elif ai is not None and bi is None:
        return -1
    elif ai is None and bi is not None:
        return 1
    else:
        return cmp(ai, bi)

group_identifiers = {
  "glyphs": lambda m, n: m == "glyphs" and isinstance(eval("svgfig.%s.%s" % (m, n)), svgfig.svg.SVG),
  "unicode-maps": lambda m, n: m == "glyphs" and isinstance(eval("svgfig.%s.%s" % (m, n)), types.DictType),
  "path-constructors": lambda m, n: m == "pathdata" and n in ("poly", "bezier", "velocity", "foreback", "smooth"),
  "xml-markup": lambda m, n: m == "svg" and n in ("Instruction", "Comment", "CDATA"),
  "ticks": lambda m, n: m == "curve" and n in ("ticks", "logticks"),
  "numbers-for-ticks": lambda m, n: m == "curve" and n in ("format_number", "unicode_number"),
  "utility-functions": lambda m, n: (m == "defaults" and n in ("tonumber", "tonumberlist", "tostringlist", "tostringmap", "isnumber")) or \
                                    (m == "pathdata" and n[:5] == "parse") or \
                                    (m == "svg" and n[:10] == "canonical_") or \
                                    (m == "svg" and n[:11] == "cannonical_"), # XXX DEPRECATED (wrong spelling), remove later
  "conversion-to-xml": lambda m, n: m == "svg" and n[-7:] == "_to_xml",
  "load": lambda m, n: m == "svg" and n in ("load", "load_stream", "template"),
  "svg-tools": lambda m, n: m == "svg" and n in ("randomid", "rgb"),
  "axes": lambda m, n: m == "curve" and n in ("XAxis", "YAxis"),
  "transformation-calculations": lambda m, n: m == "trans" and (n[:15] == "transformation_" or n == "epsilon"),
  "version-info": lambda m, n: m == "defaults" and n[:7] in ("version", "Version"),
  }

group_orders = {
  "unicode-maps": lambda a, b: order(a, b, ["latex", "currency"]),
  "path-constructors": lambda a, b: order(a, b, ["poly", "bezier", "velocity", "foreback", "smooth"]),
  "ticks": lambda a, b: order(a, b, ["ticks", "logticks"]),
  "conversion-to-xml": lambda a, b: order(a, b, ["svg_to_xml"]),
  "load": lambda a, b: order(a, b, ["load", "load_stream", "template"]),
  "transformation-calculations": lambda a, b: order(a, b, ["epsilon"]),
  }

suppress_identifiers = [
  lambda m, n: m == "defaults" and re.sub(r"(.*_).*", r"\1", n) in ("signature_", "require_", "defaults_", "tonumber_", "transform_", "bbox_"),
  ]

groups = {}
loners = {}
for key in group_identifiers.keys():
    grouplist = []
    for d in docs:
        if d.tag == "group" and d["name"] == key:
            grouplist.append(d)
            break
    if grouplist == []:
        grouplist.append(None)
    groups[key] = grouplist

class Doc:
    def __init__(self, module, name, interactive):
        self.module = module
        self.name = name
        self.interactive = interactive

        self.doc = None
        for d in docs:
            if d.tag != "group" and d["module"] == module and d["name"] == name:
                self.doc = d
                break

        self.ingroup = False
        for key, func in group_identifiers.items():
            if func(module, name):
                self.ingroup = True
                groups[key].append(self)
                break
        if not self.ingroup:
            loners["%s-%s" % (module, name)] = self

        self.obj = eval("svgfig.%s.%s" % (module, name))

objects = {}
for module in svgfig.__all__:
    if module != "interactive":
        for name in dir(eval("svgfig.%s" % module)):
            if name[0] != "_" and not isinstance(eval("svgfig.%s.%s" % (module, name)), types.ModuleType):
                suppressed = False
                for func in suppress_identifiers:
                    if func(module, name): suppressed = True

                if not suppressed:
                    objects["%s.%s" % (module, name)] = Doc(module, name, (name in svgfig.interactive.__dict__))

#################################################################################

def google_quoteCamels(s):
    return re.sub(r"([A-Za-z][a-z0-9]*[A-Z]+[A-Za-z0-9]*)", r"!\1", s)

def google_write(doc, f):
    if isinstance(doc, basestring):
        f.write(google_quoteCamels(doc))

    elif doc.tag in ("method", "member" ): pass # only for methods that still exist, on-demand in writeitem

    else:
        if doc.tag == "code": f.write("\n{{{\n")

        for child in doc.children:
            google_write(child, f)
            f.write("\n")

        if doc.tag == "code": f.write("}}}\n")

def google_writeitem(i, f, obj, thetype):
    if thetype == "class" and "__init__" in obj.__dict__:
        arguments = inspect.formatargspec(*inspect.getargspec(obj.__init__))
    elif thetype == "function":
        arguments = inspect.formatargspec(*inspect.getargspec(obj))
    else:
        arguments = ""

    if i.doc is not None and "type" in i.doc.attrib: thetype = i.doc["type"]
    if i.doc is not None and "args" in i.doc.attrib: arguments = "(%s)" % i.doc["args"]

    f.write("= %s %s.%s =\n\n{{{\n" % (thetype.capitalize(), i.module, i.name))

    if i.doc is not None and "internal" in i.doc.attrib and eval(i.doc["internal"]):
        f.write("_(Internal: not intended for the average SVGFig user, but you may find it useful...)_")

    if i.interactive:
        f.write(">>> from svgfig.interactive import *\n")
        f.write(">>> %s%s\n" % (i.name, arguments))
    else:
        f.write(">>> import svgfig.%s\n" % i.module)
        f.write(">>> svgfig.%s.%s%s\n" % (i.module, i.name, arguments))
    if thetype == "variable":
        representation = repr(obj)
        if len(representation) > 80: representation = representation[0:77] + "..."
        f.write(representation)
        f.write("\n")
    f.write("}}}\n\n")

    if i.doc is not None:
        f.write("== Arguments ==\n\n")
        argtable = []
        for child in i.doc.children:
            if isinstance(child, XML) and child.tag == "arg":
                name = child["name"]

                default = "_*required*_"
                if "default" in child.attrib:
                    if child["default"] == "optional":
                        default = "_optional_"
                    else:
                        default = google_quoteCamels("_default_=" + child["default"])

                d = ""
                if "d" in child.attrib:
                    d = google_quoteCamels(child["d"])

                argtable.append("|| %s || %s || %s ||" % (name, default, d))

        f.write("\n".join(argtable))

    if i.doc is not None: google_write(i.doc, f)

    if isinstance(i.obj, types.ClassType):
        members = []
        methods = []
        for name in i.obj.__dict__:
            if name[0] != "_":
                if callable(i.obj.__dict__[name]): methods.append(name)
                else: members.append(name)

        members_order = []
        methods_order = []
        moredocs = {}
        if i.doc is not None:
            for child in i.doc.children:
                if isinstance(child, XML):
                    if child.tag == "member":
                        if child["name"] not in members: members.append(child["name"])
                        members_order.append(child["name"])
                        moredocs[child["name"]] = child

                    elif child.tag == "method":
                        methods_order.append(child["name"])
                        moredocs[child["name"]] = child

        members.sort(lambda a, b: strorder(a, b, members_order))
        methods.sort(lambda a, b: strorder(a, b, methods_order))

        for name in members:
            f.write("== Member %s ==\n\n" % name)
            if name in i.obj.__dict__:
                f.write("*Default value:* %s\n\n" % repr(i.obj.__dict__[name]))
            if name in moredocs:
                google_write(moredocs[name], f)

        for name in methods:
            f.write("== Method %s ==\n\n" % name)

def google():
    os.system("mkdir build/google")
    for filename, docobj in groups.items():
        header = docobj[0]
        items = docobj[1:]
        if filename in group_orders:
            items.sort(group_orders[filename])
        else:
            items.sort(lambda a, b: cmp((a.module, a.name), (b.module, b.name)))

        f = file("build/google/V2Ref-group-%s.wiki" % filename, "w")

        summary = filename
        if header is not None and "summary" in header.attrib:
            summary = header["summary"]

        labels = "Reference,Version2"
        if header is not None and "labels" in header.attrib:
            labels = header["labels"]

        f.write("#summary %s\n#labels %s\n\n_(Documentation for %s.)_\n\n" % (summary, labels, svgfig.defaults.version))

        if header is not None:
            google_write(header, f)
        f.write("\n")

        for i in items:
            obj = eval("svgfig.%s.%s" % (i.module, i.name))
            if isinstance(obj, types.ClassType): thetype = "class"
            elif isinstance(obj, types.InstanceType): thetype = "variable"
            elif callable(obj): thetype = "function"
            else: thetype = "variable"
            google_writeitem(i, f, obj, thetype)

    for filename, docobj in loners.items():
        obj = eval("svgfig.%s.%s" % (docobj.module, docobj.name))
        if isinstance(obj, types.ClassType): thetype = "class"
        elif isinstance(obj, types.InstanceType): thetype = "variable"
        elif callable(obj): thetype = "function"
        else: thetype = "variable"

        f = file("build/google/V2Ref-%s-%s.wiki" % (thetype, filename), "w")

        summary = filename
        if docobj.doc is not None and "summary" in docobj.doc.attrib:
            summary = docobj.doc["summary"]

        labels = "Reference,Version2"
        if docobj.doc is not None and "labels" in docobj.doc.attrib:
            labels = docobj.doc["labels"]

        f.write("#summary %s\n#labels %s\n\n_(Documentation for %s.)_\n\n" % (summary, labels, svgfig.defaults.version))

        google_writeitem(docobj, f, obj, thetype)

        f.write("\n")

os.system("rm -rf build")
os.system("mkdir build")
google()
