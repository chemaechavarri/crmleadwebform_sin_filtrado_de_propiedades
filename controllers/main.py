from odoo import http
from odoo.http import request
from datetime import datetime, timedelta

class WebsiteLeadWebForm(http.Controller):

    @http.route('/lead', type='http', auth='public', website=True)
    def lead_form(self, **kw):
    
        company_id = kw.get('company_id')

        move_in_date = kw.get('move_in_date')
        
        parsed_move_in_date = False
        if move_in_date:
            try:
                parsed_move_in_date = datetime.strptime(move_in_date, "%Y-%m-%d").date()
            except ValueError:
                parsed_move_in_date = False
    
        try:
            company_id = int(company_id)
        except (TypeError, ValueError):
            company_id = False
    
        # Diccionario empresa -> nombre propiedad
        company_property_map = {
            "URBANHUB MEXICO SPV1": "Joaquina",
            "URBANHUB MEXICO SPV2": "Matilde",
            "URBANHUB MEXICO SPV3": "Magda",
            "URBANHUB SPV4": "Ines",
            "URBANHUB SPV5": "Amalia",
            "URBANHUB MEXICO SPV6": "Josefa",
            "URBANHUB MEXICO SPV8": "Leona",
            "EDIFICIO INDIANILLA": "Natalia",
        }

        allowed_company_names = [
            "URBANHUB MEXICO SPV1",
            "URBANHUB MEXICO SPV2",
            "URBANHUB MEXICO SPV3",
            "URBANHUB SPV4",
            "URBANHUB SPV5",
            "URBANHUB MEXICO SPV6",
            "URBANHUB MEXICO SPV8",
            "EDIFICIO INDIANILLA",
        ]
        
        # Diccionario nombre real -> nombre visible en web
        company_display_name_map = {
            "URBANHUB MEXICO SPV1": "Joaquina",
            "URBANHUB MEXICO SPV2": "Matilde",
            "URBANHUB MEXICO SPV3": "Magda",
            "URBANHUB SPV4": "Ines",
            "URBANHUB SPV5": "Amalia",
            "URBANHUB MEXICO SPV6": "Josefa",
            "URBANHUB MEXICO SPV8": "Leona",
            "EDIFICIO INDIANILLA": "Natalia",
        }
        

    
        base_domain = [
            ('x_is_property', '=', True),
        ]
        
        if company_id:
            company = request.env['res.company'].sudo().browse(company_id)
        
            for key in company_property_map:
                if key in company.name:
                    property_name = company_property_map[key]
                    base_domain.append(('name', 'ilike', property_name))
                    break
        
        allowed_companies = request.env['res.company'].sudo().search([
            ('name', 'in', allowed_company_names)
        ])
        allowed_company_ids = allowed_companies.ids

        base_domain.append(('company_id', 'in', allowed_company_ids))
        
        all_properties = request.env['account.analytic.account'].sudo().with_context(
            allowed_company_ids=allowed_company_ids
        ).search(base_domain)
                
        properties = all_properties.with_context(allowed_company_ids=allowed_company_ids)


        countries = request.env['res.country'].sudo().search([], order='name')
        
        return request.render('crmleadwebform.website_lead_form', {
            'properties': properties,
            'selected_company_id': company_id,
            'allowed_companies': allowed_companies,
            'company_display_name_map': company_display_name_map,
            'countries': countries,
            'move_in_date': move_in_date,
        })


    @http.route('/lead/submit', type='http', auth='public', website=True, csrf=True)
    def lead_submit(self, **post):

        country_code = post.get('phone_country_code', '+52')
        phone_number = (post.get('phone') or '').strip()
        full_phone = f"{country_code} {phone_number}" if phone_number else False

        vals = {
            'name': post.get('name'),
            'contact_name': post.get('contact_name'),
            'phone': full_phone,
            'email_from': post.get('email_from'),
            'date_deadline': post.get('date_deadline'),
            'x_studio_periodo_de_renta_solicitado': post.get('date_deadline'),
            'description': post.get('description'),
        }

        # Empresa
        if post.get('company_id'):
            vals['company_id'] = int(post.get('company_id'))

        # Propiedad → Departamento de Interés
        if post.get('x_property_id'):
            vals['x_property_id'] = int(post.get('x_property_id'))

        if post.get('contact_name') or post.get('email_from') or post.get('phone'):
            partner = request.env['res.partner'].sudo().create({
                'name': post.get('contact_name') or post.get('name'),
                'email': post.get('email_from'),
                'phone': full_phone,
            })
            vals['partner_id'] = partner.id

        request.env['crm.lead'].sudo().create(vals)

        return request.redirect('/lead/thank-you')

    @http.route('/lead/thank-you', type='http', auth='public', website=True)
    def lead_thank_you(self, **kw):
        return request.render('crmleadwebform.website_lead_thank_you')
