from ..backend.player import EwPlayer

def format_ad_response(ad_data):
    sponsor_player = EwPlayer(id_user=ad_data.id_sponsor)
    sponsor_disclaimer = "Paid for by {}".format(sponsor_player.display_name)
    ad_response = "A billboard catches your eye:\n\n{}\n\n*{}*".format(ad_data.content, sponsor_disclaimer)

    return ad_response
