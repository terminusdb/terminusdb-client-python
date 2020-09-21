import warnings

try:
    from IPython.display import display, Javascript, HTML
except ImportError:
    msg = (
        "woqlview need to be used in Jupyter notebook\n"
    )
    warnings.warn(msg)

import json

class WOQLView:
    def __init__(self):
        self.config = ""
        self.obj = None
        display(Javascript("""
        require.config({
            paths: {
                d3: 'https://d3js.org/d3.v5.min',
                TerminusClient:'https://cheuk.dev/js_scripts/terminusdb-client.min',
                TerminusDBGraph:'https://francesca-bit.github.io/notebooktest/terminusdb-react-graph.min'
            }
        });
        """
          )
        )
    def edges(self, *args):
        for item in args:
            if not isinstance(item, list):
                raise TypeError("argument of edges need to be lists")
        arguments = ",".join(map(str,args))
        self.config += f"woqlGraphConfig.edges({arguments});\n"
        return self

    def height(self, height_input):
        self.config += f"woqlGraphConfig.height({height_input});\n"
        return self

    def width(self, width_input):
        self.config += f"woqlGraphConfig.height({width_input});\n"
        return self

    def edge(self, start, end):
        if not isinstance(start, str) or not isinstance(end, str):
            raise TypeError("arguments of edge() need to be strings")
        arguments = ",".join(map(lambda x: f'"{x}"',[start,end]))
        self.obj = f"woqlGraphConfig.edge({arguments})"
        return self

    def node(self, *args):
        # if not isinstance(select_node, str):
        #     raise TypeError("argument of node() need to be string")
        # self.obj = f'woqlGraphConfig.node("{select_node}")'
        # return self

        for item in args:
            if not isinstance(item, str):
                raise TypeError("arguments of node() need to be strings")
        arguments = ",".join(map(lambda x: f'"{x}"',args))
        self.obj = f"woqlGraphConfig.node({arguments})"
        return self

    def text(self, input_text):
        if self.obj is None:
            raise SyntaxError("text() should be used following a node() or edge()")
        self.config += self.obj + f'.text("{input_text}");\n'
        return self

    def distance(self, input_distance):
        if self.obj is None:
            raise SyntaxError("distance() should be used following a node() or edge()")
        self.config += self.obj + f'.distance({input_distance});\n'
        return self

    def weight(self, input_weight):
        if self.obj is None:
            raise SyntaxError("weight() should be used following a node() or edge()")
        self.config += self.obj + f'.weight({input_weight});\n'
        return self

    def color(self, input_color):
        if not isinstance(input_color, list):
            raise TypeError("argument of color() need to be list")
        if len(input_color) > 3:
            input_color = input_color[:3]
        if len(input_color) < 3:
            input_color += [0]*(3-len(input_color))
        if self.obj is None:
            raise SyntaxError("color() should be used following a node() or edge()")
        arguments = ",".join(map(str,input_color))
        self.config += self.obj + f'.color([{arguments}]);\n'
        return self

    def icon(self, input_dict):
        if not isinstance(input_dict, dict):
            raise TypeError("argument of icon() need to be dict")
        if self.obj is None:
            raise SyntaxError("icon() should be used following a node() or edge()")
        self.config += self.obj + f'.icon({json.dumps(input_dict)});\n'
        return self

    def size(self, input_size):
        if self.obj is None:
            raise SyntaxError("size() should be used following a node() or edge()")
        self.config += self.obj + f'.size({input_size});\n'
        return self

    def collision_radius(self, input_radius):
        if self.obj is None:
            raise SyntaxError("collision_radius() should be used following a node() or edge()")
        self.config += self.obj + f'.collisionRadius({input_radius});\n'
        return self

    def hidden(self, input):
        if input:
            self.config += self.obj + f'.hidden(true);\n'
        else:
            self.config += self.obj + f'.hidden(false);\n'
        return self

    def charge(self, input):
        self.config += self.obj + f'.charge({input});\n'
        return self

    def show(self, result):
        display(Javascript("""
        (function(element){
        require(['d3','TerminusClient','TerminusDBGraph'], function(d3,TerminusClient,TerminusDBGraph){

            console.log(TerminusDBGraph);
            const resultData=%s

            const woqlGraphConfig= TerminusClient.View.graph();
            woqlGraphConfig.height(500).width(800);
            %s


            var result = new TerminusClient.WOQLResult(resultData);
            let viewer = woqlGraphConfig.create(null);

            viewer.setResult(result);
            const graphResult= new TerminusDBGraph.GraphResultsViewer(viewer.config, viewer);
            graphResult.load(element.get(0),true);
            })
            })(element)
            """%(result, self.config)
                      ))

    def print(self, result):
        print("""
        (function(element){
        require(['d3','TerminusClient','TerminusDBGraph'], function(d3,TerminusClient,TerminusDBGraph){

            console.log(TerminusDBGraph);
            const resultData=%s

            const woqlGraphConfig= TerminusClient.View.graph();
            woqlGraphConfig.height(500).width(800);
            %s


            var result = new TerminusClient.WOQLResult(resultData);
            let viewer = woqlGraphConfig.create(null);

            viewer.setResult(result);
            const graphResult= new TerminusDBGraph.GraphResultsViewer(viewer.config, viewer);
            graphResult.load(element.get(0),true);
            })
            })(element)
            """%(result, self.config)
                      )
