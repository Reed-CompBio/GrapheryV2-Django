from __future__ import annotations

from django.db import transaction

from . import (
    tutorial_anchor_recipe,
    tutorial_recipe,
    user_recipe,
    code_recipe,
    graph_anchor_recipe,
    graph_recipe,
    execution_result_recipe,
    graph_description_recipe,
)
from ..models import UserRoles

from urllib import request

import json


def make_test_example():
    with transaction.atomic():
        users = [
            user_recipe.make(
                username=f"test_user_{i}",
                displayed_name=f"Test User {i}",
                role=UserRoles.AUTHOR,
            )
            for i in range(3)
        ]
        tutorial_anchor = tutorial_anchor_recipe.make(
            anchor_name="test anchor", url="test-anchor"
        )
        tutorial = tutorial_recipe.make(
            tutorial_anchor=tutorial_anchor,
            title="Test Tutorial",
            abstract="Test Abstract",
            content_markdown=DEFAULT_TUTORIAL_CONTENT,
            authors=users,
        )
        code = code_recipe.make(
            code=DEFAULT_CODE_CONTENT, tutorial_anchor=tutorial_anchor
        )
        graph_anchor = graph_anchor_recipe.make(
            anchor_name="test graph",
            url="test-graph",
            tutorial_anchors=[tutorial_anchor],
        )
        graph = graph_recipe.make(
            graph_anchor=graph_anchor,
            makers=[users[0], users[2]],
            graph_json=json.loads(DEFAULT_GRAPH_JSON),
        )
        graph_description = graph_description_recipe.make(
            graph_anchor=graph_anchor,
            authors=users[:1],
            title="Test Graph Description",
            description_markdown="# Test Contents",
        )
        execution_result = execution_result_recipe.make(
            code=code,
            graph_anchor=graph_anchor,
            result_json=run_controller(DEFAULT_CODE_CONTENT, DEFAULT_GRAPH_JSON)[
                "info"
            ],
            result_json_meta={},
        )

    return


def run_controller(code, graph_json):
    from executor import SERVER_VERSION

    result = json.loads(
        request.urlopen(
            "http://127.0.0.1:7590/run",
            data=json.dumps(
                {
                    "code": code,
                    "graph": graph_json,
                    "version": SERVER_VERSION,
                }
            ).encode(),
        )
        .read()
        .decode()
    )

    return result


DEFAULT_GRAPH_JSON = (
    '{"attributes": {}, "options": {"allowSelfLoops": true, "type": "undirected", "multi": false}, "nodes": ['
    '{"key": "v_69", "attributes": {"id": "v_69", "name": "F", "displayed": {}, "x": 0.14158142709866434, '
    '"y": -0.009582286081413916, "size": 10}}, {"key": "v_75", "attributes": {"id": "v_75", "name": "D", '
    '"displayed": {}, "x": 0.06801486069191857, "y": 0.2289512039610408, "size": 10}}, {"key": "v_72", '
    '"attributes": {"id": "v_72", "name": "H", "displayed": {}, "x": -0.3549170296467903, '
    '"y": -0.40161952167552617, "size": 10}}, {"key": "v_67", "attributes": {"id": "v_67", "name": "K", '
    '"displayed": {}, "x": 0.5449661795238367, "y": 0.13440199861414825, "size": 10}}, {"key": "v_66", '
    '"attributes": {"id": "v_66", "name": "B", "displayed": {}, "x": -0.13657108540833676, '
    '"y": -0.19309786830309722, "size": 10}}, {"key": "v_71", "attributes": {"id": "v_71", "name": "J", '
    '"displayed": {}, "x": -0.9999999999999999, "y": 0.7368332414783836, "size": 10}}, {"key": "v_68", '
    '"attributes": {"id": "v_68", "name": "E", "displayed": {}, "x": 0.3601340866784741, '
    '"y": 0.0011544314754232427, "size": 10}}, {"key": "v_73", "attributes": {"id": "v_73", "name": "L", '
    '"displayed": {}, "x": 0.5700598231037489, "y": -0.147890271860211, "size": 10}}, {"key": "v_65", '
    '"attributes": {"id": "v_65", "name": "C", "displayed": {}, "x": 0.08856498332648087, '
    '"y": 0.09123558368247167, "size": 10}}, {"key": "v_70", "attributes": {"id": "v_70", "name": "A", '
    '"displayed": {}, "x": -0.13045183344818678, "y": -0.003422233981471192, "size": 10}}, {"key": "v_64", '
    '"attributes": {"id": "v_64", "name": "I", "displayed": {}, "x": -0.5198912824628348, '
    '"y": -0.5653770116497179, "size": 10}}, {"key": "v_74", "attributes": {"id": "v_74", "name": "G", '
    '"displayed": {}, "x": 0.36850987054302436, "y": 0.12841273433996955, "size": 10}}], "edges": [{"key": '
    '"v_69->v_68", "source": "v_69", "target": "v_68", "attributes": {"id": "e_73", "name": "E-F", '
    '"source": "v_68", "target": "v_69", "displayed": {}}}, {"key": "v_69->v_66", "source": "v_69", '
    '"target": "v_66", "attributes": {"id": "e_74", "name": "B-F", "source": "v_66", "target": "v_69", '
    '"displayed": {}}}, {"key": "v_69->v_75", "source": "v_69", "target": "v_75", "attributes": {"id": '
    '"e_78", "name": "D-F", "source": "v_75", "target": "v_69", "displayed": {}}}, {"key": "v_69->v_74", '
    '"source": "v_69", "target": "v_74", "attributes": {"id": "e_81", "name": "G-F", "source": "v_74", '
    '"target": "v_69", "displayed": {}}}, {"key": "v_75->v_65", "source": "v_75", "target": "v_65", '
    '"attributes": {"id": "e_77", "name": "C-D", "source": "v_65", "target": "v_75", "displayed": {}}}, '
    '{"key": "v_72->v_64", "source": "v_72", "target": "v_64", "attributes": {"id": "e_71", "name": "H-I", '
    '"source": "v_72", "target": "v_64", "displayed": {}}}, {"key": "v_72->v_66", "source": "v_72", '
    '"target": "v_66", "attributes": {"id": "e_79", "name": "B-H", "source": "v_66", "target": "v_72", '
    '"displayed": {}}}, {"key": "v_67->v_68", "source": "v_67", "target": "v_68", "attributes": {"id": '
    '"e_72", "name": "E-K", "source": "v_68", "target": "v_67", "displayed": {}}}, {"key": "v_67->v_74", '
    '"source": "v_67", "target": "v_74", "attributes": {"id": "e_76", "name": "G-K", "source": "v_74", '
    '"target": "v_67", "displayed": {}}}, {"key": "v_66->v_70", "source": "v_66", "target": "v_70", '
    '"attributes": {"id": "e_75", "name": "A-B", "source": "v_70", "target": "v_66", "displayed": {}}}, '
    '{"key": "v_68->v_73", "source": "v_68", "target": "v_73", "attributes": {"id": "e_83", "name": "E-L", '
    '"source": "v_68", "target": "v_73", "displayed": {}}}, {"key": "v_68->v_65", "source": "v_68", '
    '"target": "v_65", "attributes": {"id": "e_70", "name": "C-E", "source": "v_65", "target": "v_68", '
    '"displayed": {}}}, {"key": "v_68->v_74", "source": "v_68", "target": "v_74", "attributes": {"id": '
    '"e_80", "name": "E-G", "source": "v_68", "target": "v_74", "displayed": {}}}, {"key": "v_65->v_70", '
    '"source": "v_65", "target": "v_70", "attributes": {"id": "e_82", "name": "A-C", "source": "v_70", '
    '"target": "v_65", "displayed": {}}}]} '
)


# DEFAULT_CODE_CONTENT: str = (
#     request.urlopen(
#         "https://raw.githubusercontent.com/Reed-CompBio/GrapheryExecutor/main/executor/tests/example-code.py"
#     )
#     .read()
#     .decode()
# )

DEFAULT_CODE_CONTENT: str = """\
# Python 3.10
from __future__ import annotations

import networkx as nx
from seeker import tracer

graph: nx.Graph


# variables whose names are in the tracer will be displayed
@tracer("greeting", "a_node", "an_edge", "node_iterator")
def main() -> None:
    # since greeting is in `tracer`, it's value will be shown
    greeting: str = "hello world :)"
    greeting = "Welcome to Graphery! :)"

    # graph elements are stored in the `graph_object`
    # nodes can be referenced by `graph_object.nodes`
    node_iterator = list(graph.nodes)
    a_node = node_iterator[0]
    not_traced_node = node_iterator[1]

    # Similarly, edges can be referenced by `graph_object.edges`
    edge_iterator = [*graph.edges]
    an_edge = edge_iterator[0]
    not_traced_edge = edge_iterator[1]



if __name__ == "__main__":
    main()

"""

DEFAULT_TUTORIAL_CONTENT: str = (
    "# h1 Heading 8-)\n"
    + "## h2 Heading\n"
    + "### h3 Heading\n"
    + "#### h4 Heading\n"
    + "##### h5 Heading\n"
    + "<h2> h2 Heading by HTML</h2>\n"
    + "\n"
    + "## Math \n"
    + "inline: $\\sqrt{2}$ 1\n"
    + "$$\n"
    + "\\mathbb{R}^3\n"
    + "$$\n"
    + "## Horizontal Rules\n"
    + "\n"
    + "___\n"
    + "\n"
    + "---\n"
    + "\n"
    + "***\n"
    + "\n"
    + "## Typographic replacements\n"
    + "\n"
    + "Enable typographer option to see result.\n"
    + "\n"
    + "(c) (C) (r) (R) (tm) (TM) (p) (P) +-\n"
    + "\n"
    + "test.. test... test..... test?..... test!....\n"
    + "\n"
    + "!!!!!! ???? ,,  -- ---\n"
    + "\n"
    + "\"Smartypants, double quotes\" and 'single quotes'\n"
    + "\n"
    + "\n"
    + "## Emphasis\n"
    + "\n"
    + "**This is bold text**\n"
    + "\n"
    + "__This is bold text__\n"
    + "\n"
    + "*This is italic text*\n"
    + "\n"
    + "_This is italic text_\n"
    + "\n"
    + "~~Strikethrough~~\n"
    + "\n"
    + "\n"
    + "## Blockquotes\n"
    + "\n"
    + "\n"
    + "> Blockquotes can also be nested...\n"
    + ">> ...by using additional greater-than signs right next to each other...\n"
    + "> > > ...or with spaces between arrows.\n"
    + "\n"
    + "\n"
    + "## Lists\n"
    + "\n"
    + "Unordered\n"
    + "\n"
    + "+ Create a list by starting a line with `+`, `-`, or `*`\n"
    + "+ Sub-lists are made by indenting 2 spaces:\n"
    + "  - Marker character change forces new list start:\n"
    + "    * Ac tristique libero volutpat at\n"
    + "    + Facilisis in pretium nisl aliquet\n"
    + "    - Nulla volutpat aliquam velit\n"
    + "+ Very easy!\n"
    + "\n"
    + "Ordered\n"
    + "\n"
    + "1. Lorem ipsum dolor sit amet\n"
    + "2. Consectetur adipiscing elit\n"
    + "3. Integer molestie lorem at massa\n"
    + "\n"
    + "\n"
    + "1. You can use sequential numbers...\n"
    + "1. ...or keep all the numbers as `1.`\n"
    + "\n"
    + "Start numbering with offset:\n"
    + "\n"
    + "57. foo\n"
    + "1. bar\n"
    + "\n"
    + "\n"
    + "## Code\n"
    + "\n"
    + "Inline `code`\n"
    + "\n"
    + "Indented code\n"
    + "\n"
    + "    // Some comments\n"
    + "    line 1 of code\n"
    + "    line 2 of code\n"
    + "    line 3 of code\n"
    + "\n"
    + "\n"
    + 'Block code "fences"\n'
    + "\n"
    + "```\n"
    + "Sample text here...\n"
    + "```\n"
    + "Syntax highlighting\n"
    + "\n"
    + "```python\n"
    + "a = lambda x: x * x\n"
    + "def test(n):\n"
    + "   return a(n)\n"
    + "\n"
    + "```\n"
    + "\n"
    + "```markdown\n"
    + "# title h1\n"
    + "\n"
    + "- l1\n"
    + "- l2\n"
    + "- l3\n"
    + "- l4\n"
    + "some text with `code` and __bold__ \n"
    + "\n"
    + "```\n"
    + "```typescript"
    + "const a = 1\n"
    + "```\n"
    + "\n"
    + "## Tables\n"
    + "\n"
    + "| Option | Description |\n"
    + "| ------ | ----------- |\n"
    + "| data   | path to data files to supply the data that will be passed into templates. |\n"
    + "| engine | engine to be used for processing templates. Handlebars is the default. |\n"
    + "| ext    | extension to be used for dest files. |\n"
    + "\n"
    + "Right aligned columns\n"
    + "\n"
    + "| Option | Description |\n"
    + "| ------:| -----------:|\n"
    + "| data   | path to data files to supply the data that will be passed into templates. |\n"
    + "| engine | engine to be used for processing templates. Handlebars is the default. |\n"
    + "| ext    | extension to be used for dest files. |\n"
    + "\n"
    + "## Links\n"
    + "\n"
    + "[vue-markdown](https://github.com/miaolz123/vue-markdown)\n"
    + "\n"
    + '[link with title](https://github.com/miaolz123/vue-markdown "VueMarkdown")\n'
    + "\n"
    + "Autoconverted link https://github.com/miaolz123/vue-markdown (enable linkify to see)\n"
    + "\n"
    + "\n"
    + "## Images\n"
    + "\n"
    + "![Minion](https://icatcare.org/app/uploads/2018/06/Layer-1704-1200x630.jpg)\n"
    + "\n"
    + "Like links, Images also have a footnote style syntax\n"
    + "\n"
    + "![Alt text][id]\n"
    + "\n"
    + "With a reference later in the document defining the URL location:\n"
    + "\n"
    + '[id]: https://icatcare.org/app/uploads/2018/06/Layer-1704-1200x630.jpg  "The Dojocat"\n'
    + "\n"
    + "\n"
    + "### Emojies\n"
    + "\n"
    + "> Classic markup: :wink: :cry: :laughing: :yum:\n"
    + ">\n"
    + "> Shortcuts (emoticons): :-) :-( 8-) ;)\n"
    + "\n"
    + "\n"
    + "### Subscript / Superscript\n"
    + "\n"
    + "- 19^th^\n"
    + "- H~2~O\n"
    + "\n"
    + "\n"
    + "### \\<ins>\n"
    + "\n"
    + "++Inserted text++\n"
    + "\n"
    + "\n"
    + "### \\<mark>\n"
    + "\n"
    + "==Marked text==\n"
    + "\n"
    + "\n"
    + "### Footnotes\n"
    + "\n"
    + "Footnote 1 link[^first].\n"
    + "\n"
    + "Footnote 2 link[^second].\n"
    + "\n"
    + "Inline footnote^[Text of inline footnote] definition.\n"
    + "\n"
    + "Duplicated footnote reference[^second].\n"
    + "\n"
    + "[^first]: Footnote **can have markup**\n"
    + "\n"
    + "    and multiple paragraphs.\n"
    + "\n"
    + "[^second]: Footnote text.\n"
    + "\n"
    + "\n"
    + "### Definition lists\n"
    + "\n"
    + "Term 1\n"
    + "\n"
    + ":   Definition 1\n"
    + "with lazy continuation.\n"
    + "\n"
    + "Term 2 with *inline markup*\n"
    + "\n"
    + ":   Definition 2\n"
    + "\n"
    + "        { some code, part of Definition 2 }\n"
    + "\n"
    + "    Third paragraph of definition 2.\n"
    + "\n"
    + "_Compact style:_\n"
    + "\n"
    + "Term 1\n"
    + "  ~ Definition 1\n"
    + "\n"
    + "Term 2\n"
    + "  ~ Definition 2a\n"
    + "  ~ Definition 2b\n"
    + "\n"
    + "\n"
    + "### Abbreviations\n"
    + "\n"
    + "This is HTML abbreviation example.\n"
    + "\n"
    + 'It converts "HTML", but keep intact partial entries like "xxxHTMLyyy" and so on.\n'
    + "\n"
    + "*[HTML]: Hyper Text Markup Language"
)
