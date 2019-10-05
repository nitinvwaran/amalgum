import mwparserfromhell


def apply_mwtext_transformations(config, mwtext):
    tfxs = config["transformations"]["mwtext"] or []
    wikicode = mwparserfromhell.parse(mwtext)
    for tfx in tfxs:
        assert "name" in tfx, "Transformation must have a name"

        tfx_f = globals()[tfx["name"]] if tfx["name"] in globals() else None
        assert tfx_f is not None, "Transformation not found: " + tfx["name"]
        if "args" in tfx:
            wikicode = tfx_f(wikicode, **tfx["args"])
        else:
            wikicode = tfx_f(wikicode)
    return str(wikicode)


def drop_headings(wikicode, titles=None):
    out_nodes = []
    skip = False
    titles = [x.lower().strip() for x in titles]
    for n in wikicode._nodes:
        if (
            isinstance(n, mwparserfromhell.nodes.heading.Heading)
            and n.title.lower().strip() in titles
        ):
            skip = True
        elif isinstance(n, mwparserfromhell.nodes.heading.Heading):
            skip = False
        if skip:
            continue
        out_nodes.append(n)
    wikicode._nodes = out_nodes
    return wikicode


def drop_templates(wikicode, names=None):
    out_nodes = []
    names = [x.lower().strip() for x in names]
    for n in wikicode._nodes:
        if (
            isinstance(n, mwparserfromhell.nodes.template.Template)
            and n.name.lower().strip() in names
        ):
            continue
        out_nodes.append(n)
    wikicode._nodes = out_nodes
    return wikicode