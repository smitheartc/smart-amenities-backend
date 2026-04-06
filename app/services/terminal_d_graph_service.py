import networkx as nx
from app.models.models import AmenityType, AmenityStatus
from app.schemas.schemas import RouteOption

class AirportMapService:
    def __init__(self, graph_data):
        # Initialize your graph here
        self.graph = None
        self._build_graph(graph_data)

    def _build_graph(self, data) -> nx.Graph:
        # Logic to convert your DB records or JSON into a networkx graph
        self.graph = nx.node_link_graph(data)
        return self.graph
    
    def update_amenity_data(self, amenities):
        for amenity in amenities:
            if self.graph.has_node(amenity.id):
                self.graph.nodes[amenity.id]['type'] = amenity.type
                self.graph.nodes[amenity.id]['status'] = amenity.status
                self.graph.nodes[amenity.id]['crowd_level'] = amenity.crowd_level
        

    def get_recommendations(self, start_node: str,  target_type: AmenityType):
        
        
        try:
            all_paths = nx.single_source_dijkstra_path(self.graph, source=start_node, weight='weight')
            valid_destinations = []
            for destination in all_paths:
                #if desired amenity type and open
                if (self.graph.nodes[destination].get('type') == target_type) and (self.graph.nodes[destination].get('status') == AmenityStatus.OPEN):
                    valid_destinations.append(destination)
            print(valid_destinations)

            #cost calculation for each valid destination, building the response
            results = []
            for destination in valid_destinations:

                dest_path = all_paths[destination]
                walk_time = nx.path_weight(self.graph, dest_path, "weight")
                wait_time = self.graph.nodes[destination].get('crowd_level').wait_estimate_minutes * 60

                results.append(RouteOption(
                amenity_id=destination,
                path=dest_path,
                walk_seconds=walk_time,
                wait_seconds=wait_time,
                total_seconds=walk_time + wait_time,
                crowd_level=self.graph.nodes[destination].get('crowd_level'),
                status=self.graph.nodes[destination].get('status')
            ))
                
            return results


            
            
            
            # return RouteResponse(path=path)
        except nx.NetworkXNoPath:
            print("Failure!!!")
            # Handle standard errors gracefully
            # return RouteResponse(path=[], error="No path found")