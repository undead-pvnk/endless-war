""" A weather object. Pure flavor. """


class EwWeather:
    # The identifier for this weather pattern.
    name = ""

    str_sunrise = ""
    str_day = ""
    str_sunset = ""
    str_night_new = ""
    str_night_waxing_start = ""
    str_night_waxing_end = ""
    str_night_full = ""
    str_night_waning_start = ""
    str_night_waning_end = ""
    str_night_special = ""

    def __init__(
            self,
            name = "",
            sunrise = "",
            day = "",
            sunset = "",
            night_new = "",
            night_waxing_start = "",
            night_waxing_end = "",
            night_full = "",
            night_waning_start = "",
            night_waning_end = "",
            night_special = ""
    ):
        self.name = name
        self.str_sunrise = sunrise
        self.str_day = day
        self.str_sunset = sunset
        self.str_night_new_ = night_new
        self.str_night_waxing_start = night_waxing_start
        self.str_night_waxing_end = night_waxing_end
        self.str_night_full = night_full
        self.str_night_waning_start = night_waning_start
        self.str_night_waning_end = night_waning_end
        self.str_night_special = night_special
