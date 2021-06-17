from . import core as bknd_core
from ..static import cfg as ewcfg
from ..static import poi as poi_static


class EwDistrictBase:
    id_server = -1

    # The district's identifying string
    name = ""

    # The faction currently controlling this district
    controlling_faction = ""

    # The faction currently capturing this district
    capturing_faction = ""

    # The amount of progress made on the capture
    capture_points = 0

    # The property class of the district
    property_class = ""

    # The amount of CP it takes for the district to be captured
    max_capture_points = 0

    # The amount of slime in the district
    slimes = 0

    # Time until the district unlocks for capture again
    time_unlock = 0

    # Amount of influence in a district

    cap_side = ""

    # determines if the zone is functional
    degradation = 0

    # a timestamp for when a shambler can next plant a tombstone
    horde_cooldown = 0

    # the amount of gaiaslime the garden gankers have at their disposal
    gaiaslime = 0

    def __init__(self, id_server = None, district = None):
        if id_server is not None and district is not None:
            self.id_server = id_server
            self.name = district

            # find the district's property class
            for poi in poi_static.poi_list:
                if poi.id_poi == self.name:
                    self.property_class = poi.property_class.lower()

            if len(self.property_class) > 0:
                self.max_capture_points = ewcfg.limit_influence[self.property_class]
            else:
                self.max_capture_points = 0

            data = bknd_core.execute_sql_query(
                "SELECT {controlling_faction}, {capturing_faction}, {capture_points},{slimes}, {time_unlock}, {cap_side}, {degradation}, {horde_cooldown}, {gaiaslime} FROM districts WHERE id_server = %s AND {district} = %s".format(

                    controlling_faction=ewcfg.col_controlling_faction,
                    capturing_faction=ewcfg.col_capturing_faction,
                    capture_points=ewcfg.col_capture_points,
                    district=ewcfg.col_district,
                    slimes=ewcfg.col_district_slimes,
                    time_unlock=ewcfg.col_time_unlock,
                    cap_side=ewcfg.col_cap_side,
                    degradation=ewcfg.col_degradation,
                    horde_cooldown=ewcfg.col_horde_cooldown,
                    gaiaslime=ewcfg.col_gaiaslime,
                ), (
                    id_server,
                    district
                ))

            if len(data) > 0:  # if data is not empty, i.e. it found an entry
                # data is always a two-dimensional array and if we only fetch one row, we have to type data[0][x]
                self.controlling_faction = data[0][0]
                self.capturing_faction = data[0][1]
                self.capture_points = data[0][2]
                self.slimes = data[0][3]
                self.time_unlock = data[0][4]
                self.cap_side = data[0][5]
                self.degradation = data[0][6]
                self.horde_cooldown = data[0][7]
                self.gaiaslime = data[0][8]

            # ewutils.logMsg("EwDistrict object '" + self.name + "' created.  Controlling faction: " + self.controlling_faction + "; Capture progress: %d" % self.capture_points)
            else:  # create new entry
                bknd_core.execute_sql_query("REPLACE INTO districts ({id_server}, {district}) VALUES (%s, %s)".format(
                    id_server=ewcfg.col_id_server,
                    district=ewcfg.col_district
                ), (
                    id_server,
                    district
                ))

    def persist(self):
        bknd_core.execute_sql_query(
            "REPLACE INTO districts(id_server, {district}, {controlling_faction}, {capturing_faction}, {capture_points}, {slimes}, {time_unlock}, {cap_side}, {degradation}, {horde_cooldown}, {gaiaslime}) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(
                district=ewcfg.col_district,
                controlling_faction=ewcfg.col_controlling_faction,
                capturing_faction=ewcfg.col_capturing_faction,
                capture_points=ewcfg.col_capture_points,
                slimes=ewcfg.col_district_slimes,
                time_unlock=ewcfg.col_time_unlock,
                cap_side=ewcfg.col_cap_side,
                degradation=ewcfg.col_degradation,
                horde_cooldown=ewcfg.col_horde_cooldown,
                gaiaslime=ewcfg.col_gaiaslime,
            ), (
                self.id_server,
                self.name,
                self.controlling_faction,
                self.capturing_faction,
                self.capture_points,
                self.slimes,
                self.time_unlock,
                self.cap_side,
                self.degradation,
                self.horde_cooldown,
                self.gaiaslime
            ))
