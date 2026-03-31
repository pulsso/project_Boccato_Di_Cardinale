from decimal import Decimal


ZONE_CHOICES = [
    ('norte', 'Santiago Norte'),
    ('sur', 'Santiago Sur'),
    ('oriente', 'Santiago Oriente'),
    ('poniente', 'Santiago Poniente'),
    ('centro', 'Santiago Centro'),
]

SECTOR_CHOICES = [
    ('las-condes', 'Las Condes'),
    ('providencia', 'Providencia'),
    ('nunoa', 'Nunoa'),
    ('vitacura', 'Vitacura'),
    ('la-reina', 'La Reina'),
    ('santiago-centro', 'Santiago Centro'),
    ('maipu', 'Maipu'),
    ('puente-alto', 'Puente Alto'),
    ('san-miguel', 'San Miguel'),
    ('la-florida', 'La Florida'),
]

SECTOR_COORDS = {
    'las-condes': {'lat': -33.4080, 'lng': -70.5670},
    'providencia': {'lat': -33.4311, 'lng': -70.6093},
    'nunoa': {'lat': -33.4569, 'lng': -70.5979},
    'vitacura': {'lat': -33.3832, 'lng': -70.5642},
    'la-reina': {'lat': -33.4423, 'lng': -70.5502},
    'santiago-centro': {'lat': -33.4489, 'lng': -70.6693},
    'maipu': {'lat': -33.5107, 'lng': -70.7580},
    'puente-alto': {'lat': -33.6117, 'lng': -70.5758},
    'san-miguel': {'lat': -33.4964, 'lng': -70.6514},
    'la-florida': {'lat': -33.5227, 'lng': -70.5983},
}

SECTOR_APPROX_DISTANCE_KM = {
    'las-condes': Decimal('12.0'),
    'providencia': Decimal('7.0'),
    'nunoa': Decimal('8.0'),
    'vitacura': Decimal('13.0'),
    'la-reina': Decimal('11.0'),
    'santiago-centro': Decimal('4.0'),
    'maipu': Decimal('18.0'),
    'puente-alto': Decimal('24.0'),
    'san-miguel': Decimal('9.0'),
    'la-florida': Decimal('16.0'),
}

INTERNAL_DELIVERY_FEE_ABOVE_10KM = Decimal('3000')
EXTERNAL_DELIVERY_PERCENTAGE = Decimal('0.12')
STORE_ORIGIN_ADDRESS = 'Boccato di Cardinale, Santiago, Chile'
STORE_ORIGIN_LAT = -33.4489
STORE_ORIGIN_LNG = -70.6693


def get_sector_coordinates(sector):
    return SECTOR_COORDS.get(sector, {'lat': -33.4489, 'lng': -70.6693})


def get_sector_distance_km(sector):
    return SECTOR_APPROX_DISTANCE_KM.get(sector, Decimal('0'))


def get_zone_label(zone):
    return dict(ZONE_CHOICES).get(zone, zone or 'Sin zona')


def get_sector_label(sector):
    return dict(SECTOR_CHOICES).get(sector, sector or 'Sin sector')
