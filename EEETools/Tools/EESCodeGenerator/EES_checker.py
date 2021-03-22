from EEETools import costants


class Zones:

    def __init__(self, array_handler):

        self.array_handler = array_handler
        self.__initialize_zones()

    def __initialize_zones(self):

        self.zones = dict()

        for zone_type in costants.ZONES:

            zone_list = list()
            first_connection =  self.__find_new_first_connection(zone_list)

            while first_connection is not None:
                zone_list.append(Zone(zone_type, first_connection))
                first_connection = self.__find_new_first_connection(zone_list)

            self.zones.update({zone_type: zone_list})

    def __find_new_first_connection(self, zone_list):

        for connection in self.array_handler.connection_list:

            if connection.is_fluid_stream:

                found = False

                for zone in zone_list:

                    if zone.contains(connection):
                        found = True
                        break

                if not found:
                    return connection

        return None


class Zone:

    def __init__(self, type, first_connection):

        self.connections = list()
        self.type = type
        self.is_defined = False

        self.add_connections(first_connection)

    def add_connections(self, first_connection):

        self.add_connection(first_connection)

    def add_connection(self, connection):

        if connection not in self.connections:

            if not connection.zones[self.type] is None:
                connection.zones[self.type].remove_connection(connection)

            connection.add_zone(self)
            self.connections.append(connection)

            for new_connection in connection.return_other_zone_connections(self):
                self.add_connection(new_connection)

    def remove_connection(self, connection):
        self.connections.remove(connection)
        connection.zones[self.type] = None

    def contains(self, connection):

        return connection in self.connections
