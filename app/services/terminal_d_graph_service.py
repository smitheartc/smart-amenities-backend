import networkx as nx
#from app.schemas.map_schemas import RouteResponse

class AirportMapService:
    def __init__(self, graph_data):
        # Initialize your graph here
        self.graph = self._build_graph(graph_data)

    def _build_graph(self, data) -> nx.Graph:
        # Logic to convert your DB records or JSON into a networkx graph
        G = nx.node_link_graph(data)
        print(G)
        return G

    def get_shortest_path(self, start_node: str, end_node: str):# -> RouteResponse:
        # networkx logic happens entirely inside these methods
        try:
            path = nx.dijkstra_path(self.graph, source=start_node, target=end_node, weight='weight')
            print(path)
            # return RouteResponse(path=path)
        except nx.NetworkXNoPath:
            print("Failure!!!")
            # Handle standard errors gracefully
            # return RouteResponse(path=[], error="No path found")