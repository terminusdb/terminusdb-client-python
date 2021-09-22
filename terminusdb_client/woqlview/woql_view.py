import json
import warnings
from numbers import Number

from ..errors import InterfaceError

try:
    from IPython.display import Javascript, display
except ImportError:
    pass

REQUIRE_CONFIG = """require.config({
    paths: {
        TerminusClient:'https://cdn.jsdelivr.net/npm/@terminusdb/terminusdb-client@4.3.1/dist/terminusdb-client.min',
        TerminusDBGraph:'https://cdn.jsdelivr.net/npm/@terminusdb/terminusdb-react-components@4.3.1/dist/terminusdb-d3-graph.min'
    }
});"""


class WOQLView:
    def __init__(self):
        ### TODO: make WOQLView works again
        raise InterfaceError("WOQLView is temporary not avaliable in this version")

        self.config = ""
        self.obj = None
        try:
            display(Javascript(REQUIRE_CONFIG))
        except NameError:
            pass

    def edges(self, *args: list):
        for item in args:
            if not isinstance(item, list):
                raise TypeError("argument of edges need to be lists")
        arguments = ",".join(map(str, args))
        self.config += f"woqlGraphConfig.edges({arguments});\n"
        return self

    def height(self, height_input: Number):
        self.config += f"woqlGraphConfig.height({height_input});\n"
        return self

    def width(self, width_input: Number):
        self.config += f"woqlGraphConfig.width({width_input});\n"
        return self

    def edge(self, start: str, end: str):
        if not isinstance(start, str) or not isinstance(end, str):
            raise TypeError("arguments of edge() need to be strings")
        arguments = ",".join(map(lambda x: f'"{x}"', [start, end]))
        self.obj = f"woqlGraphConfig.edge({arguments})"
        return self

    def node(self, *args: str):
        # if not isinstance(select_node, str):
        #     raise TypeError("argument of node() need to be string")
        # self.obj = f'woqlGraphConfig.node("{select_node}")'
        # return self

        for item in args:
            if not isinstance(item, str):
                raise TypeError("arguments of node() need to be strings")
        arguments = ",".join(map(lambda x: f'"{x}"', args))
        self.obj = f"woqlGraphConfig.node({arguments})"
        return self

    def text(self, input_text: str):
        if self.obj is None:
            raise SyntaxError("text() should be used following a node() or edge()")
        self.config += self.obj + f'.text("{input_text}");\n'
        return self

    def distance(self, input_distance: Number):
        if self.obj is None:
            raise SyntaxError("distance() should be used following a node() or edge()")
        self.config += self.obj + f".distance({input_distance});\n"
        return self

    def weight(self, input_weight: Number):
        if self.obj is None:
            raise SyntaxError("weight() should be used following a node() or edge()")
        self.config += self.obj + f".weight({input_weight});\n"
        return self

    def color(self, input_color: list):
        if not isinstance(input_color, list):
            raise TypeError("argument of color() need to be list")
        if len(input_color) > 3:
            input_color = input_color[:3]
        if len(input_color) < 3:
            input_color += [0] * (3 - len(input_color))
        if self.obj is None:
            raise SyntaxError("color() should be used following a node() or edge()")
        arguments = ",".join(map(str, input_color))
        self.config += self.obj + f".color([{arguments}]);\n"
        return self

    def icon(self, input_dict: dict):
        if not isinstance(input_dict, dict):
            raise TypeError("argument of icon() need to be dict")
        if self.obj is None:
            raise SyntaxError("icon() should be used following a node() or edge()")
        self.config += self.obj + f".icon({json.dumps(input_dict)});\n"
        return self

    def size(self, input_size: Number):
        if self.obj is None:
            raise SyntaxError("size() should be used following a node() or edge()")
        self.config += self.obj + f".size({input_size});\n"
        return self

    def collision_radius(self, input_radius: Number):
        if self.obj is None:
            raise SyntaxError(
                "collision_radius() should be used following a node() or edge()"
            )
        self.config += self.obj + f".collisionRadius({input_radius});\n"
        return self

    def hidden(self, input_choice: bool):
        if input_choice:
            self.config += self.obj + ".hidden(true);\n"
        else:
            self.config += self.obj + ".hidden(false);\n"
        return self

    def charge(self, input_charge: Number):
        if self.obj is None:
            raise SyntaxError("charge(() should be used following a node() or edge()")
        self.config += self.obj + f".charge({input_charge});\n"
        return self

    def of(self, input_obj: str):
        if self.obj is None:
            raise SyntaxError("in() should be used following a node() or edge()")
        self.obj += f'.in("{input_obj}")'
        return self

    def show(self, result: dict):
        """Show the graph inline in the Jupyter notebook

        Parameters
        ----------
        result: the result that is returning from a query in dict format."""
        try:
            display(
                Javascript(
                    """
            (function(element){
            require(['TerminusClient','TerminusDBGraph'], function(TerminusClient,TerminusDBGraph){

                console.log(TerminusDBGraph);
                const resultData=%s

                const woqlGraphConfig= TerminusClient.View.graph();
                woqlGraphConfig.height(window.innerHeight).width(window.innerWidth);
                %s


                var result = new TerminusClient.WOQLResult(resultData);
                let viewer = woqlGraphConfig.create(null);

                viewer.setResult(result);
                const graphResult= new TerminusDBGraph.GraphResultsViewer(viewer.config, viewer);
                graphResult.load(element.get(0),true);
                })
                })(element)
                """
                    % (result, self.config)
                )
            )
        except NameError:
            msg = "WOQLView().show need to be used in Jupyter notebook.\n"
            warnings.warn(msg)

    def export(self, filename: str, result: dict):
        """Export the graph into an html file

        Parameters
        ----------
        filename: the file name of the export file (without extention).

        result: the result that is returning from a query in dict format."""
        with open(filename + ".html", "w", encoding="utf-8") as file:
            file.write(
                """<html>
              <head>
                <meta name="viewport" content="width=device-width, initial-scale=1">

                <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.0.9/css/all.css" integrity="sha384-5SOiIsAziJl6AWe0HWRKTXlfcSHKmYV4RBF18PPJ173Kzn7jzMyFuTtk8JA7QQG1" crossorigin="anonymous">

                <title>%s</title>
              </head>
              <body>
                 <div style="width: 100vw; height: 100vw;" id="mycontainer" ></div>
              </body>

              <script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.6/require.js" integrity="sha512-vRqhAr2wsn+/cSsyz80psBbCcqzz2GTuhGk3bq3dAyytz4J/8XwFqMjiAGFBj+WM95lHBJ9cDf87T3P8yMrY7A==" crossorigin="anonymous"></script>

              <script>

              %s

                require(['TerminusClient','TerminusDBGraph'], function(TerminusClient,TerminusDBGraph){


                const resultData=%s

                const woqlGraphConfig= new TerminusClient.View.graph();
                woqlGraphConfig.height(500).width(800);
                %s

                var result = new TerminusClient.WOQLResult(resultData);
                let viewer = woqlGraphConfig.create(null);

                viewer.setResult(result);
                const graphResult= new TerminusDBGraph.GraphResultsViewer(viewer.config, viewer);
                graphResult.load("#mycontainer",true);

              })

              </script>


            </html>"""
                % (filename, REQUIRE_CONFIG, result, self.config)
            )

    def print_js_config(self):
        """Print out the JavaScript config

        Parameters
        ----------
        result: the result that is returning from a query in dict format."""
        print(self.config)  # noqa
