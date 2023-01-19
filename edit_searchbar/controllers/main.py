from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website

class CustomWebsite(Website):  
    @http.route('/website/snippet/autocomplete', type='json', auth='public', website=True)
    
    def autocomplete(self, search_type=None, term=None, order=None, limit=5, max_nb_chars=999, options=None):
        """
        Returns list of results according to the term and options

        :param str search_type: indicates what to search within, 'all' matches all available types
        :param str term: search term written by the user
        :param str order:
        :param int limit: number of results to consider, defaults to 5
        :param int max_nb_chars: max number of characters for text fields
        :param dict options: options map containing
            allowFuzzy: enables the fuzzy matching when truthy
            fuzzy (boolean): True when called after finding a name through fuzzy matching

        :returns: dict (or False if no result) containing
            - 'results' (list): results (only their needed field values)
                    note: the monetary fields will be strings properly formatted and
                    already containing the currency
            - 'results_count' (int): the number of results in the database
                    that matched the search query
            - 'parts' (dict): presence of fields across all results
            - 'fuzzy_search': search term used instead of requested search
        """
        #Define search_type as "products_only"
        search_type = "products_only"
        order = self._get_search_order(order)
        options = options or {}
        results_count, search_results, fuzzy_term = request.website._search_with_fuzzy(search_type, term, limit, order, options)
        if not results_count:
            return {
                'results': [],
                'results_count': 0,
                'parts': {},
            }
        term = fuzzy_term or term
        search_results = request.website._search_render_results(search_results, limit)
        mappings = []
        results_data = []
        for search_result in search_results:
            results_data += search_result['results_data']
            mappings.append(search_result['mapping'])
        if search_type == 'all':
            # Only supported order for 'all' is on name
            results_data.sort(key=lambda r: r.get('name', ''), reverse='name desc' in order)
        results_data = results_data[:limit]
        result = []

        def get_mapping_value(field_type, value, field_meta):
            if field_type == 'text':
                if value and field_meta.get('truncate', True):
                    value = shorten(value, max_nb_chars, placeholder='...')
                if field_meta.get('match') and value and term:
                    pattern = '|'.join(map(re.escape, term.split()))
                    if pattern:
                        parts = re.split(f'({pattern})', value, flags=re.IGNORECASE)
                        if len(parts) > 1:
                            value = request.env['ir.ui.view'].sudo()._render_template(
                                "website.search_text_with_highlight",
                                {'parts': parts}
                            )
                            field_type = 'html'

            if field_type not in ('image', 'binary') and ('ir.qweb.field.%s' % field_type) in request.env:
                opt = {}
                if field_type == 'monetary':
                    opt['display_currency'] = options['display_currency']
                elif field_type == 'html':
                    opt['template_options'] = {}
                value = request.env[('ir.qweb.field.%s' % field_type)].value_to_html(value, opt)
            return escape(value)

        for record in results_data:
            mapping = record['_mapping']
            mapped = {
                '_fa': record.get('_fa'),
            }
            for mapped_name, field_meta in mapping.items():
                value = record.get(field_meta.get('name'))
                if not value:
                    mapped[mapped_name] = ''
                    continue
                field_type = field_meta.get('type')
                if field_type == 'dict':
                    # Map a field with multiple values, stored in a dict with values type: item_type
                    item_type = field_meta.get('item_type')
                    mapped[mapped_name] = {}
                    for key, item in value.items():
                        mapped[mapped_name][key] = get_mapping_value(item_type, item, field_meta)
                else:
                    mapped[mapped_name] = get_mapping_value(field_type, value, field_meta)
            result.append(mapped)

        return {
            'results': result,
            'results_count': results_count,
            'parts': {key: True for mapping in mappings for key in mapping},
            'fuzzy_search': fuzzy_term,
        }