from odoo import http

class TestApi(http.Controller):

    @http.route("/api/test", methods=["GET"], type="http", auth="none", crsf=False)
    def test_endpoint(self):
        print("inside test endpoint")
        return "Test endpoint reached successfully!"
