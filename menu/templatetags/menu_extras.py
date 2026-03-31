"""
menu/templatetags/menu_extras.py
Filtros y tags personalizados para los templates de la carta Boccato.
"""
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Accede a un diccionario en el template.
    Uso: {{ mi_dict|get_item:mi_clave }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter
def porcentaje_descuento(precio_original, precio_oferta):
    """
    Calcula el porcentaje de descuento entre dos precios.
    Uso: {{ item.precio|porcentaje_descuento:item.precio_oferta }}
    """
    try:
        original = float(precio_original)
        oferta   = float(precio_oferta)
        if original > 0 and oferta < original:
            return int(((original - oferta) / original) * 100)
    except (TypeError, ValueError, ZeroDivisionError):
        pass
    return 0


@register.filter
def precio_formato(valor):
    """
    Formatea un precio con separador de miles chileno.
    Uso: {{ item.precio|precio_formato }}  → $14.900
    """
    try:
        v = int(float(valor))
        return f'${v:,.0f}'.replace(',', '.')
    except (TypeError, ValueError):
        return f'${valor}'


@register.filter
def tipo_icon(tipo):
    """
    Retorna el emoji icon para cada tipo de menú.
    Uso: {{ seccion.tipo|tipo_icon }}
    """
    icons = {
        'desayuno': '☕',
        'brunch':   '🥐',
        'almuerzo': '🍽️',
        'cena':     '🌙',
        'postres':  '🍮',
        'terraza':  '🧀',
        'vinos':    '🍷',
        'licores':  '🥃',
        'cocteles': '🍹',
        'catering': '🎪',
        'eventos':  '🎉',
    }
    return icons.get(tipo, '✦')


@register.simple_tag
def estrella_dorada():
    """Tag para mostrar el separador dorado de Boccato."""
    return mark_safe('<span style="color:#d4af37;font-size:10px;">✦</span>')


@register.filter
def truncar_descripcion(texto, largo=80):
    """
    Trunca una descripción a un largo máximo de palabras completas.
    Uso: {{ item.descripcion|truncar_descripcion:80 }}
    """
    if not texto:
        return ''
    if len(texto) <= largo:
        return texto
    truncado = texto[:largo].rsplit(' ', 1)[0]
    return truncado + '…'