from ew.backend.quadrants import EwQuadrant
from ew.static import cfg as ewcfg
from ew.static import quadrants as quad_static


def get_quadrant(cmd, id_quadrant):
    author = cmd.message.author
    quadrant = quad_static.quadrants_map[id_quadrant]
    if cmd.mentions_count == 0:
        quadrant_data = EwQuadrant(id_server=author.guild.id, id_user=author.id, quadrant=quadrant.id_quadrant)
        if author.guild.get_member(quadrant_data.id_target) is None:
            quadrant_data.id_target = -1
        if author.guild.get_member(quadrant_data.id_target2) is None:
            quadrant_data.id_target2 = -1

        quadrant_data.persist()

        if quadrant_data.id_target == -1:
            response = "You have no one in this quadrant."
        else:
            onesided = quadrant_data.check_if_onesided()

            if quadrant.id_quadrant == ewcfg.quadrant_policitous and quadrant_data.id_target2 != -1:
                target_name = "{} and {}".format(author.guild.get_member(quadrant_data.id_target).display_name, author.guild.get_member(quadrant_data.id_target2).display_name)
            else:
                target_name = author.guild.get_member(quadrant_data.id_target).display_name

            if not onesided:
                response = quadrant.resp_view_relationship_self.format(target_name)
            else:
                response = quadrant.resp_view_onesided_self.format(target_name)

    else:
        member = cmd.mentions[0]
        quadrant_data = EwQuadrant(id_server=member.guild.id, id_user=member.id, quadrant=quadrant.id_quadrant)

        if author.guild.get_member(quadrant_data.id_target) is None:
            quadrant_data.id_target = -1
        if author.guild.get_member(quadrant_data.id_target2) is None:
            quadrant_data.id_target2 = -1

        quadrant_data.persist()

        if quadrant_data.id_target == "":
            response = "They have no one in this quadrant."
        else:

            onesided = quadrant_data.check_if_onesided()

            if quadrant.id_quadrant == ewcfg.quadrant_policitous and quadrant_data.id_target2 != -1:
                target_name = "{} and {}".format(author.guild.get_member(quadrant_data.id_target).display_name, author.guild.get_member(quadrant_data.id_target2).display_name)
            else:
                target_name = author.guild.get_member(quadrant_data.id_target).display_name

            if not onesided:
                response = quadrant.resp_view_relationship.format(member.display_name, target_name)
            else:
                response = quadrant.resp_view_onesided.format(member.display_name, target_name)

    return response
