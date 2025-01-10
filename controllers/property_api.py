import json
import math
from urllib.parse import parse_qs
from odoo import http
from odoo.http import request

# handle valid response structure
def valid_response(data, status, pagination_info):
    response_body = {
        "data": data,
        "message": "success"
    }
    if pagination_info:
        response_body['pagination_info'] = pagination_info
    return request.make_json_response(response_body, status=status)


# handle valid response structure
def invalid_response(error, status):
    response_body = {
        "error": error
    }
    return request.make_json_response(response_body, status=status)
class PropertyApi(http.Controller):

    # using CRUD Methods
    # create operation using http
    @http.route('/v1/property', methods=["POST"], type="http", auth="none", csrf=False)
    def post_property(self):
        # values send by user
        args = request.httprequest.data.decode()
        # transfer args variable (json to dict)
        vals = json.loads(args)
        # add validation layer for name
        if not vals.get('name'):
            return invalid_response({
               "message": "name is required",
           }, status=400)
        # create by super admin
        # handel error using(try except)
        try:
            res = request.env['property'].sudo().create(vals)
            if res:
                # dict for response, status=200 > success, retrieve data based on record that created
                return valid_response({
                    "message": "property created successfully",
                    "id": res.id,
                    "name": res.name,
                }, status=201)
        except Exception as error:
            return invalid_response({
                "error": error,
            }, status=400)

    # create operation using json
    @http.route('/v1/property/json', methods=["POST"], type="json", auth="none", csrf=False)
    def post_property_json(self):
        args = request.httprequest.data.decode()
        vals = json.loads(args)
        res = request.env['property'].sudo().create(vals)
        if res:
            # not need to handel response, retrieve data based on record that created
            return {
                "message": "property created successfully",
                "id": res.id,
                "name": res.name,
            }

    # update operation, using id to access record to update it as a parameter (variable)
    # /v1/property/dynamic(variable and type)
    @http.route("/v1/property/<int:property_id>", methods=["PUT"], type="http", auth="none", csrf=False)
    def update_property(self, property_id):
        try:
            # access record
            property_id = request.env['property'].sudo().search([('id', '=', property_id)])
            # validation if no record by this id
            if not property_id:
                return invalid_response({
                    "error": "ID doesn't exist",
                }, status=400)
            # values that update in record
            args = request.httprequest.data.decode()
            vals = json.loads(args)
            # update(write) new value in record
            property_id.write(vals)
            # handle response for third-party app interact
            return valid_response({
                "message": "property has been updated successfully",
                "id": property_id.id,
                "name": property_id.name
            }, status=200)
        except Exception as error:
            return invalid_response({
                "error": error,
            }, status=400)

    # Read operation, using id to read or retrieve record data as a parameter (variable)
    # /v1/property/dynamic(variable and type)
    @http.route('/v1/property/<int:property_id>', methods=['GET'], type="http", auth="none", csrf=False)
    def read_property(self, property_id):
        try:
            property_id = request.env['property'].sudo().search([('id', '=', property_id)])
            if not property_id:
                return invalid_response({
                    "error": "There is no property match this ID"
                }, status=400)
            return valid_response({
                "id": property_id.id,
                "name": property_id.name,
                "ref": property_id.ref,
                "post_code": property_id.postcode,
                "garden_area": property_id.garden_area,
                "bedrooms": property_id.bedrooms
            }, status=200)
        except Exception as error:
            return invalid_response({
                "error": error,
            }, status=400)

    # Delete Operation using id to delete record as a parameter (variable)
    # /v1/property/dynamic(variable and type)
    @http.route("/v1/property/<int:property_id>", methods=["DELETE"], type="http", auth="none", csrf=False)
    def delete_property(self, property_id):
        try:
            property_id = request.env['property'].sudo().search([('id', '=', property_id)])
            if not property_id:
                return invalid_response({
                    "error": "ID not exist",
                }, status=400)
            # delete record
            property_id.unlink()
            return valid_response({
                "message": "property has been deleted successfully",
            }, status=200)
        except Exception as error:
            return invalid_response({
                "error": error,
            }, status=400)

    # Get list of records with filtration (return all records)
    @http.route('/v1/properties', methods=['GET'], type="http", auth="none", csrf=False)
    def read_property_list(self):
        try:
            # receive user parameters to use it in filtration
            params = parse_qs(request.httprequest.query_string.decode('utf-8'))
            property_domain = []
            # third-party generate offset and limit, user give page to count offset and limit
            page = offset = None
            # add default value to limit if user not add page and limit
            limit = 3
            if params:
                if params.get('limit'):
                    limit = int(params.get('limit')[0])
                if params.get('page'):
                    page = int(params.get('page')[0])
            # count offset by using page and limit
            if page:
                offset = (page * limit) - limit
            if params.get('state'):
                property_domain += [("state", "=", params.get("state")[0])]
                # add pagination
            property_ids = request.env['property'].sudo().search(property_domain, offset=offset, limit=limit, order="id desc")
            # to know num of record
            property_count = request.env['property'].sudo().search_count(property_domain)
            if not property_ids:
                return invalid_response({
                    "error": "There are not records"
                }, status=400)
            # read all records using list and loop
            return valid_response([{
                "id": property_id.id,
                "name": property_id.name,
                "ref": property_id.ref,
                "post_code": property_id.postcode,
                "garden_area": property_id.garden_area,
                "bedrooms": property_id.bedrooms
            } for property_id in property_ids], pagination_info= {
                # start from page 1 if user don't add page num
                "page": page if page else 1,
                "limit": limit,
                # add num of pages depend on num of recod, use math.ceil transfer num to int
                "pages": math.ceil(property_count/limit if limit else 1),
                "count": property_count
            } ,status=200)
        except Exception as error:
            return invalid_response({
                "error": error,
            }, status=400)


        # # using Sql Queries
        # # create operation
        # @http.route('/v1/property', methods=["POST"], type="http", auth="none", csrf=False)
        # def post_property(self):
        #     # values send by user
        #     args = request.httprequest.data.decode()
        #     # transfer args variable (json to dict)
        #     vals = json.loads(args)
        #     # add validation layer for name
        #     if not vals.get('name'):
        #         return invalid_response({
        #             "message": "name is required",
        #         }, status=400)
        #     # create by super admin
        #     # handel error using(try except)
        #     try:
        #         # res = request.env['property'].sudo().create(vals)
        #         # Execute sql query
        #         # reach to curser
        #         cr = request.env.cr
        #         # query here between ("""here"""), transfers fields and values to dynamic
        #         columns = ', '.join(vals.keys())
        #         values = ', '.join(['%s'] * len(vals))
        #         query = f"""INSERT INTO property ({columns})
        #                     VALUES ({values})
        #                     RETURNING id, name, postcode;
        #                     """
        #         # execute query
        #         cr.execute(query, tuple(vals.values()))
        #         # assign return to variable (fetch)
        #         res = cr.fetchone()
        #         print(res)
        #         if res:
        #             # dict for response, status=200 > success, retrieve data based on record that created
        #             return valid_response({
        #                 "message": "property created successfully",
        #                 # return values
        #                 "id": res[0],
        #                 "name": res[1],
        #                 "postcode": res[2],
        #             }, status=201)
        #     except Exception as error:
        #         return invalid_response({
        #             "error": error,
        #         }, status=400)

