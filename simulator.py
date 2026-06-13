from parser import MapParser


class Drone():
    """Represents a single drone in the simulation.

    Tracks the drone's planned path, current position, movement
    state (in_transit for restricted zones), and delivery status.
    """

    def __init__(self, drone_id: int, path: list[str],
                 current_zone: str) -> None:
        """Initializes a drone at the start zone.

        Args:
            drone_id: Unique 1-based identifier (e.g. 1 for D1).
            path: Planned route as a list of zone names,
                  starting with the current starting zone.
            current_zone: Name of the zone the drone occupies.
        """
        self.id = drone_id
        self.path: list[str] = path
        self.current_zone: str = current_zone
        self.in_transit: bool = False
        self.turns_remaining: int = 0
        self.delivered: bool = False


class Simulation():
    """Manages the turn-based drone simulation.

    Holds all drones, the parsed map data, and the current turn
    number. Provides methods to initialise and advance the
    simulation state.
    """

    def __init__(self, parser: MapParser) -> None:
        """Initialises the simulation from a parsed map.

        Creates all drones at the start zone and sets the
        turn counter to 0.

        Args:
            parser: A fully parsed MapParser instance containing
                    zones, connections, and drone count.
        """
        self.parser = parser
        self.drones: list[Drone] = []
        self.turn: int = 0
        self._init_drones()

    def _init_drones(self) -> None:
        """Creates drone instances at the start hub.

        Iterates over parsed zones to find the start_hub,
        then creates nb_drones amount of drones there.
        """
        start = ""
        for name, zone in self.parser.zones.items():
            if zone.role == "start":
                start = name
                break
        for i in range(self.parser.nb_drones):
            drone = Drone(drone_id=i + 1, path=[start],
                          current_zone=start)
            self.drones.append(drone)
