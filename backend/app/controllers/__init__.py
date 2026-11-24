"""Controllers (the C in MVC): FastAPI routers, one module per resource.

A controller only deals with HTTP: it receives validated input (app.schemas), calls a service
(app.services) and returns a view (app.schemas). No database queries or business rules here.
"""
from app.controllers import brands, briefs, campaigns, content, dashboard, me, reviews

ROUTERS = [me.router, brands.router, campaigns.router, briefs.router, content.router,
           reviews.router, dashboard.router]
