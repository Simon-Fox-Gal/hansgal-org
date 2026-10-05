"""Edition and retailer labels shared by work pages and printable work notes."""
import json, pathlib

OFFERS = json.loads((pathlib.Path(__file__).resolve().parents[1] / 'config/score-retailers.json').read_text(encoding='utf8'))

def score_link_label(url, field, tr):
    offer = OFFERS.get(url, {})
    if field == 'hire_url':
        return tr('Hire materials', 'Leihmaterial')
    if offer.get('kind') == 'information':
        return tr('Publisher information / availability enquiry', 'Verlagsinformation / Verfügbarkeitsanfrage')
    label = tr('Buy digital sheet music', 'Digitale Noten kaufen') if field == 'score_purchase_download_url' else tr('Printed sheet music', 'Gedruckte Noten')
    region = offer.get('region')
    if region:
        label = tr('UK shop', 'Shop im Vereinigten Königreich') if region == 'UK' else tr('EU shop', 'Shop in der EU')
        label += ' · ' + (tr('Digital download', 'Digitaler Download') if field == 'score_purchase_download_url' else tr('Printed sheet music', 'Gedruckte Noten'))
    edition = offer.get('edition')
    if edition:
        de = {'Parts':'Stimmen','Score and parts':'Partitur und Stimmen','Full score':'Partitur','Study score':'Studienpartitur','Piano reduction and solo part':'Klavierauszug und Solostimme','Piano reduction for two pianos':'Klavierauszug für zwei Klaviere','Score':'Partitur','Performing score':'Spielpartitur','Book 1':'Band 1','Book 2':'Band 2'}
        label += ' · ' + tr(edition, de[edition])
    if offer.get('catalogue_number'):
        label += ' · ' + offer['catalogue_number']
    return label
