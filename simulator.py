from parser import MapParser


class Drone():
    """Represents one drone in the simulation.

    Each drone has:
    - A unique ID (1, 2, 3, ...)
    - A planned path (list of zones to visit, from start to end)
    - A current position (the zone it occupies right now)
    - A delivered flag (True once it reaches the end zone)

    For restricted zones (which take 2 turns to enter), the drone
    also tracks whether it is "in transit" and how many turns
    remain before it arrives.
    """

    def __init__(self, drone_id: int, path: list[str],
                 current_zone: str) -> None:
        """Creates a drone and places it at the starting zone.

        Args:
            drone_id: Unique number (1 for D1, 2 for D2, etc.).
            path: Ordered list of zone names the drone will follow.
                Example: ["start", "fast_path", "goal"].
            current_zone: Name of the zone the drone starts in.
                This is usually the start_hub name.
        """
        self.id = drone_id
        self.path: list[str] = path
        self.current_zone: str = current_zone
        self.in_transit: bool = False
        self.turns_remaining: int = 0
        self.delivered: bool = False


class Simulation():
    """Runs the turn-by-turn drone simulation.

    The simulation receives a fully parsed map (via MapParser),
    creates the drones, finds the shortest path for each one,
    and then advances turn by turn until all drones reach the end.

    The result is a sequence of movement lines like:
        D1-fast_path D2-corridorA
        D1-goal D2-tunnelB
    """

    def __init__(self, parser: MapParser) -> None:
        """Prepares the simulation.

        This does NOT run the simulation yet. It only:
        - Stores the parsed map data
        - Creates the drones with their paths pre-calculated

        To actually run turns, call run() (not implemented yet).

        Args:
            parser: A MapParser that has already parsed and validated
                a map file (checking_data() was called).
        """
        self.parser = parser
        self.drones: list[Drone] = []
        self.turn: int = 0
        self._init_drones()

    def _init_drones(self) -> None:
        """Finds start and end zones, then creates all drones.

        Each drone gets the optimal path calculated by _dijkstra().
        All drones start at the start zone on turn 0.

        The number of drones comes from the map's nb_drones line.
        """
        start = ""
        end = ""
        for name, zone in self.parser.zones.items():
            if zone.role == "start":
                start = name
            if zone.role == "end":
                end = name

        for i in range(self.parser.nb_drones):
            drone = Drone(drone_id=i + 1, path=self._dijkstra(start, end),
                          current_zone=start)
            self.drones.append(drone)

    def zone_roles(self, role: str) -> int:
        """Returns how many turns it takes to enter a zone type.

        This is used by the pathfinding algorithm.

        Args:
            role: One of "normal", "priority", "restricted".

        Returns:
            1 for normal and priority zones.
            2 for restricted zones.
        """
        if role == "restricted":
            return 2
        return 1

    def _build_graph(self) -> dict[str, list[tuple[str, int]]]:
        """Converts the map data into an adjacency list for pathfinding.

        The map data in the parser is split into two dictionaries:
        - self.parser.zones (zone name → Zone object)
        - self.parser.connections (zone pair → Connection object)

        Pathfinding algorithms (like Dijkstra) need a different format:
        they need to ask "from this zone, which neighbors can I visit
        and what does it cost?".

        This method builds exactly that:

            {
                "start": [("fast_path", 1), ("slow_path", 2)],
                "fast_path": [("start", 1), ("goal", 1)],
                ...
            }

        Each value is a list of (neighbor_name, cost_in_turns) tuples.
        Blocked zones are NOT included as keys or as valid neighbors,
        because drones cannot enter them.

        Returns:
            A dictionary where every key is a zone name and every value
            is a list of (neighbor, movement_cost) pairs.
        """
        zones_paths: dict[str, list[tuple[str, int]]] = {}

        for key, _ in self.parser.zones.items():
            possible_paths: list[tuple[str, int]] = []
            for (zone1, zone2), _ in self.parser.connections.items():
                if key == zone1:
                    cost = self.zone_roles(self.parser.zones[zone2].zone)
                    possible_paths.append((zone2, cost))
                elif key == zone2:
                    cost = self.zone_roles(self.parser.zones[zone1].zone)
                    possible_paths.append((zone1, cost))
            zones_paths[key] = possible_paths

        return zones_paths

    def _dijkstra(self, start: str, end: str) -> list[str]:
        """Finds the cheapest path (fewest turns) from start to end.

        This is the core pathfinding algorithm. It guarantees the
        shortest path because all movement costs are positive (1 or 2).

        **How it works (simple explanation):**

        1. Start with a table that says:
           - start zone = distance 0
           - every other zone = distance "infinite" (we use 9999999)

        2. Keep a list of zones we have not yet processed.

        3. Each round, pick the unprocessed zone with the smallest
           distance. This is the "best candidate" so far.

        4. Look at every neighbor of this zone. For each neighbor,
           calculate:  current_distance + cost_to_neighbor.
           If this is smaller than the neighbor's known distance,
           update the neighbor's distance and remember which zone
           we came from.

        5. Mark the current zone as processed (remove from unvisited).

        6. Repeat until we process the end zone.

        7. To get the final path, start at end and follow the
           "which zone did I come from?" breadcrumbs back to start.
           Then reverse the list.

        Example:
            _dijkstra("start", "goal")
            → ["start", "fast_path", "goal"]

        Args:
            start: Name of the starting zone.
            end: Name of the destination zone.

        Returns:
            An ordered list of zone names from start to end.
            Returns an empty list if no path exists.
        """
        graph = self._build_graph()
        distances: dict[str, int] = {}
        previous: dict[str, str | None] = {}
        for zone in graph:
            distances[zone] = 9999999
            previous[zone] = None

        distances[start] = 0

        unvisited = list(graph.keys())

        while unvisited:
            temp_min = 99999
            track_zone = ""
            for zone in unvisited:
                if distances[zone] < temp_min:
                    temp_min = distances[zone]
                    track_zone = zone

            next_zone_options = graph[track_zone]
            for zone, cost in next_zone_options:
                if zone in unvisited:
                    new_distance = distances[track_zone] + cost
                    if new_distance < distances[zone]:
                        distances[zone] = new_distance
                        previous[zone] = track_zone

            unvisited.remove(track_zone)

            if track_zone == end:
                break

        path: list[str] = []
        current: str | None = end
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        return path
