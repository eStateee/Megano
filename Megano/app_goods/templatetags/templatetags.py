from django import template
from django.template import Context

register = template.Library()


@register.simple_tag
def define(val=None):
    return val


@register.simple_tag
def make_order_by_url(url, default_ordering, current_ordering, current_method):
    url = url.split('?')[0].split('sort')[0]
    separator = '&' if '?' in url else '?'

    if default_ordering != current_ordering:
        new_ordering = default_ordering + '_asc'
    else:
        new_ordering = default_ordering + ('_desc' if current_method == 'asc' else '_asc')

    return f"{url}{separator}sort={new_ordering}"


@register.simple_tag
def make_order_by_class(default_ordering, current_ordering, current_method):
    if default_ordering != current_ordering:
        return
    else:
        if current_method == "asc":
            return "Sort-sortBy_dec"
        else:
            return "Sort-sortBy_inc"


@register.simple_tag
def make_pagination_url(url, page):
    base_url, _, query_string = url.partition('?')
    query_params = query_string.split('&') if query_string else []

    filtered_params = [param for param in query_params if not param.startswith('page=')]
    filtered_query_string = '&'.join(filtered_params)

    separator = '&' if filtered_query_string else ''
    pagination_url = f"{base_url}?{filtered_query_string}{separator}page={page}"

    return pagination_url


@register.simple_tag
def receive_get_param(request, value):
    return request.GET.get("param_" + str(value))


@register.simple_tag(name="get_product_quantity_error", takes_context=True)
def get_product_quantity_error(context, produck_pk):
    name = f"error_{produck_pk}"
    context = Context(context)
    result = context.get(name)
    return result if result else ""
