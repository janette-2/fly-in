from parser import MapParser
from colors import colorize


class Drone():
    """Represents a single drone in the simulation.

    Tracks the drone's ID, path, current position, and delivery
    status. For restricted zones the drone also tracks transit
    state (in_transit and turns_remaining).

    Args:
        drone_id: Unique identifier (1 for D1, 2 for D2, etc.).
        path: Ordered list of zone names the drone follows.
        current_zone: Zone the drone starts in.
    """

    def __init__(self, drone_id: int, path: list[str],
                 current_zone: str) -> None:
        """Initializes the drone at the starting zone.

        Args:
            drone_id: Unique identifier (1 for D1, 2 for D2, etc.).
            path: Ordered list of zone names the drone follows.
            current_zone: Zone the drone starts in.
        """
        self.id = drone_id
        self.path: list[str] = path
        self.path_index: int = 0
        self.current_zone: str = current_zone
        self.in_transit: bool = False
        self.turns_remaining: int = 0
        self.delivered: bool = False
        self.moved_in_shift: bool = False


class Simulation():
    """Runs the turn-by-turn drone simulation.

    Receives a parsed map, creates drones, finds shortest paths,
    and advances until all drones reach the end.

    Args:
        parser: A MapParser that has already parsed and validated
            a map file.
    """

    def __init__(self, parser: MapParser) -> None:
        """Initializes the simulation with parsed map data.

        Creates drones and pre-calculates their paths.
        Call fly_simulation() to run turns.

        Args:
            parser: A MapParser that has already parsed and validated
                a map file.
        """
        self.parser = parser
        self.drones: list[Drone] = []
        self.turn: int = 0
        self._init_drones()

    def _init_drones(self) -> None:
        """Creates all drones with pre-calculated optimal paths.

        Each drone starts at the start zone. The number of drones
        comes from the map's nb_drones line.
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
        self.fly_simulation(start, end)

    def zone_roles(self, role: str) -> int:
        """Returns the turn cost to enter a zone type.

        Args:
            role: "normal", "priority", or "restricted".

        Returns:
            1 for normal/priority, 2 for restricted.
        """
        if role == "restricted":
            return 2
        return 1

    def _build_graph(self) -> dict[str, list[tuple[str, int]]]:
        """Builds an adjacency list for pathfinding from map data.

        Each key is a zone name, each value is a list of
        (neighbor, movement_cost) pairs. Blocked zones are excluded.

        Returns:
            Adjacency list dict.
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
        """Finds the shortest path from start to end using Dijkstra.

        Args:
            start: Name of the starting zone.
            end: Name of the destination zone.

        Returns:
            Ordered list of zone names from start to end.
            Empty list if no path exists.
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
            temp_min = 9999999
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

    def fly_simulation(self, start: str, end: str) -> None:
        """Runs the turn-by-turn simulation until all drones are delivered.

        Each turn processes in-transit arrivals, collects intended
        moves, validates them against capacities, and applies changes.

        Args:
            start: Name of the start zone.
            end: Name of the end (goal) zone.
        """
        # Zones Occupation counters - initialization
        occupation = {}
        for zone in self.parser.zones:
            occupation[zone] = 0
        occupation[start] = self.parser.nb_drones
        shift = 0

        # Loop to capture each shift until delivered
        while not all(drones.delivered for drones in self.drones):
            # Initialization for the first turn, all drones waiting
            shift += 1
            output = []

            to_enter = {zone: 0 for zone in self.parser.zones}
            to_leave = {zone: 0 for zone in self.parser.zones}
            used_connections = {connection: 0 for connection in
                                self.parser.connections}
            attempted_moves = []

            for drone in self.drones:

                if not drone.delivered:

                    # Phase1 - IN TRANSIT

                    if drone.in_transit:
                        drone.turns_remaining -= 1

                        if drone.turns_remaining == 0:
                            arrival_zone = drone.path[drone.path_index + 1]
                            to_enter[arrival_zone] += 1
                            drone.current_zone = arrival_zone
                            drone.path_index += 1
                            # Because is not waiting in a connection,
                            # (which is forbidden) it has arrived
                            drone.in_transit = False

                            if arrival_zone == end:
                                drone.delivered = True

                            output.append(f"D{drone.id}-"
                                          f"{colorize(arrival_zone,
                                                      self.parser.zones[
                                                          arrival_zone].color
                                                      )} "
                                          )
                            drone.moved_in_shift = True

                    # Phase2 - COLLECT NEXT MOVEMENTS

                    if not drone.in_transit and not drone.moved_in_shift:
                        next_zone = drone.path[drone.path_index + 1]
                        if next_zone < drone.current_zone:
                            next_connection_key = (next_zone,
                                                   drone.current_zone)
                        else:
                            next_connection_key = (drone.current_zone,
                                                   next_zone)

                        next_zone_obj = self.parser.zones[next_zone]
                        cost = self.zone_roles(next_zone_obj.zone)

                        attempted_moves.append(
                            (drone, drone.current_zone, next_zone,
                             next_connection_key, cost)
                        )

            # Phase3 - VALIDATE MOVEMENT ATTEMPTS BY
            # ZONE AND LINKS CAPACITIES

            for attemp_tup in attempted_moves:
                drone = attemp_tup[0]
                current_zone = attemp_tup[1]
                next_zone = attemp_tup[2]
                next_connection = attemp_tup[3]
                cost = attemp_tup[4]

                zone_projection = (occupation[next_zone] + to_enter[
                    next_zone]) - to_leave[next_zone]

                if next_zone == end:
                    save_movement = True
                else:
                    save_movement = (
                        zone_projection < self.parser.zones[
                            next_zone].max_drones
                    )

                if cost == 2:
                    # Kept in the middle of its journey
                    # Doesn't fill the zone yet
                    save_movement = True

                save_connection = (
                    used_connections[
                        next_connection]
                    <
                    self.parser.connections[
                        next_connection].max_link_capacity
                )

                if save_connection and save_movement:
                    to_leave[current_zone] += 1
                    used_connections[next_connection] += 1
                    drone.moved_in_shift = True

                    if cost == 2:
                        drone.in_transit = True
                        drone.turns_remaining = 1
                        output.append(f"D{drone.id}-"
                                      f"{colorize(current_zone,
                                                  self.parser.zones[
                                                    current_zone].color
                                                  )}-"
                                      f"{colorize(next_zone,
                                                  self.parser.zones[
                                                      next_zone].color)}")
                    else:
                        to_enter[next_zone] += 1
                        drone.current_zone = next_zone
                        drone.path_index += 1
                        if next_zone == end:
                            drone.delivered = True
                        output.append(f"D{drone.id}-"
                                      f"{colorize(next_zone,
                                                  self.parser.zones[
                                                    next_zone].color
                                                  )}"
                                      )

            # Phase4 - UPDATE PARAMETERS AFTER MOVEMENTS

            for zone in self.parser.zones:
                occupation[zone] += to_enter[zone] - to_leave[zone]

            if output:
                print(" ".join(output))

            # Initialization of the resources for the next shift
            for drone in self.drones:
                drone.moved_in_shift = False
