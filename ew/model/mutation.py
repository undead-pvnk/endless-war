class EwMutationFlavor:
    # The mutation's name
    id_mutation = ""

    # The mutation's name for use in strings
    str_name = ""

    # String used to describe the mutation when you !data yourself
    str_describe_self = ""

    # String used to describe the mutation when you !data another player
    str_describe_other = ""

    # String used when you acquire the mutation
    str_acquire = ""

    # The level of the mutation
    tier = 0

    incompatible = {}

    # String used when you transplant a mutation
    str_transplant = ""

    # Alternate names for the mutation
    alias = []

    def __init__(self,
                 id_mutation = "",
                 str_name = "",
                 str_describe_self = "",
                 str_describe_other = "",
                 str_acquire = "",
                 tier = 1,
                 incompatible = {},
                 str_transplant = "",
                 alias = None):

        self.id_mutation = id_mutation

        self.str_name = str_name

        if str_describe_self == "":
            str_describe_self = "You have the {} mutation.".format(self.id_mutation)
        self.str_describe_self = str_describe_self

        if str_describe_other == "":
            str_describe_other = "They have the {} mutation.".format(self.id_mutation)
        self.str_describe_other = str_describe_other

        if str_acquire == "":
            str_acquire = "You have acquired the {} mutation.".format(self.id_mutation)
        self.str_acquire = str_acquire

        if tier == "":
            tier = 5
        self.tier = tier

        self.incompatible = incompatible

        if str_transplant == "":
            str_transplant = "Auntie Dusttrap injects a syringe full of carcinogens into your back. You got the {} mutation!".format(self.id_mutation)
        self.str_transplant = str_transplant

        if alias == None:
            alias = []
        self.alias = alias
