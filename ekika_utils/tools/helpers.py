# -*- coding: utf-8 -*-
######################################################################
#                                                                    #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: ekika.co).     #
# See LICENSE file for full copyright and licensing details.         #
#                                                                    #
######################################################################

from ast import literal_eval
from secrets import choice
import string
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import json
import re

from odoo.tools import file_open, date_utils


def extract_params(request):
    """
    Extract http_method, body, uri, headers parameters from odoo-request,
    """
    http_method = request.httprequest.method
    body = request.httprequest.form
    uri = request.httprequest.url
    headers = dict(request.httprequest.headers.to_wsgi_list())

    return http_method, body, uri, headers

def generate_string(length=32, characters=None):
    """Generate a random string of given length using characters.

    Args:
        length (int): Length of the secret key (default: 32).
        characters (str): Sequence of characters to use (if not given use a-z, A-Z, 0-9 and punctuation.)

    Returns:
        str: Generated random string.
    """
    characters = string.ascii_letters + string.digits
    return ''.join(choice(characters) for _ in range(length))


def get_manifest_as_dict(manifest):
    """Provide imported __manifest__ of any module function will return dict."""
    manifest_dict = None
    with file_open(manifest.__file__, mode='r') as f:
        manifest_dict = literal_eval(f.read())
    return manifest_dict


def query_param_modifier(url, query_values):
    """Update given query parameter with new value. If not present add it.
    Process: Parse the URL >> parse_qs >> adjust query >> manually join
        query >> unparse components with new query.

    Args:
        query_values (dict): Dictionary that contains Key as query-parameter and
                             Value as query-parameter value.
    """
    url_components = urlparse(url)
    query_params = parse_qs(url_components.query)
    for key,val in query_values.items():
        query_params[key] = [val]
    new_query_string = '&'.join(
        f"{param}={','.join(values)}"
        for param, values in query_params.items()
    )
    return urlunparse(url_components._replace(query=new_query_string))

def compare_dicts(dict1, dict2):
    """
    Compare two dictionaries for equality.

    Args:
        dict1 (dict): The first dictionary.
        dict2 (dict): The second dictionary.

    Returns:
        bool: True if the dictionaries are equal, False otherwise.
    """
    # Convert dictionaries to JSON strings and compare them
    return json.dumps(dict1, sort_keys=True, ensure_ascii=False, default=date_utils.json_default) == json.dumps(dict2, sort_keys=True, ensure_ascii=False, default=date_utils.json_default)

def capitalize_to_odoo_model(model):
    """
    return standard odoo model name from capitalize model name

    e.g: model = SaleOrder
        return => sale.order
    """
    model_list = re.findall('[A-Z][^A-Z]*', model)
    model_name = ".".join([r.lower() for r in model_list])
    return model_name

def convert_model_capitalize(model):
    """
    return Capitalize model name

    e.g: model = sale.order
        return => SaleOrder
    """
    word = ''
    for i in model.split('.'):
        word += i.capitalize()
    return word
