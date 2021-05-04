
class EwQuadrantFlavor:
	id_quadrant = ""
	
	aliases = []

	resp_add_onesided = ""

	resp_add_relationship = ""

	resp_view_onesided = ""

	resp_view_onesided_self = ""

	resp_view_relationship = ""

	resp_view_relationship_self = ""

	def __init__(self,
		id_quadrant = "",
		aliases = [],
		resp_add_onesided = "",
		resp_add_relationship = "",
		resp_view_onesided = "",
		resp_view_onesided_self = "",
		resp_view_relationship = "",
		resp_view_relationship_self = ""
	    ):
		self.id_quadrant = id_quadrant
		self.aliases = aliases
		self.resp_add_onesided = resp_add_onesided
		self.resp_add_relationship = resp_add_relationship
		self.resp_view_onesided = resp_view_onesided
		self.resp_view_onesided_self = resp_view_onesided_self
		self.resp_view_relationship = resp_view_relationship
		self.resp_view_relationship_self = resp_view_relationship_self 

