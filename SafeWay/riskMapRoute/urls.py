from django.conf.urls import url
from riskMapRoute import views
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^$', views.HomePageView.as_view()), 
	url(r'^divideMap/$',views.divideMap),
	url(r'^getSquares/$',views.getSquares),
	url(r'^getBestRoute/$',views.getBestRoute),
	url(r'^getMiddleRoute/$',views.getMiddleRoute),
	url(r'^getWorstRoute/$',views.getWorstRoute),
	url(r'^getGraphicValues/$',views.getGraphicValues),
	url(r'^setConfiguration/$',views.setConfiguration),
	url(r'^favicon\.ico$',RedirectView.as_view(url='/static/images/reload.gif')),
	url(r'^favicon\.ico$',RedirectView.as_view(url='/static/images/logo.png')),
]

