from django.urls import path
from . import views
urlpatterns = [
    path('buyer_home',views.home, name="home"),
    
   

############# farmer section start ###############
    path('neutrition_deficiency',views.neutrition_deficiency, name="neutrition_deficiency"),
    path('predict_weather',views.predict_weather, name="predict_weather"),

    path('farm_login',views.farm_login, name="farm_login"),
    path('farm_register',views.farm_register, name="farm_register"),
    path('SignOut',views.SignOut, name="SignOut"),
    path('farm_home',views.farm_home, name="farm_home"),
    path('add_details',views.add_details, name="add_details"),

    path('view_detials//<int:pk>',views.view_detials, name="view_detials"),

    path('update_detials//<int:pk>',views.update_detials, name="update_detials"),

    path('add_category',views.add_category, name="add_category"),

    path('farmer_view_category',views.farmer_view_category, name="farmer_view_category"),

    path('add_product_details',views.add_product_details, name="add_product_details"),

    path('view_product_details',views.view_product_details, name="view_product_details"),

    path('view_product//<int:pk>',views.view_product, name="view_product"),
    

    path('edit_product_details//<int:pk>',views.edit_product_details, name="edit_product_details"),

    path('delete_product_details//<int:pk>',views.delete_product_details, name="delete_product_details"),

    path('view_buyer', views.view_buyer, name="view_buyer"),

    path('sold-product/<int:product_id>/', views.sold_product_detail, name='sold_product_detail'),

    path('cate_details/<int:pk>/', views.cate_details, name='cate_details'),

    
    
############## famer section end ######################

#############buyer section start ###################
    path('buyer_login',views.buyer_login, name="buyer_login"),
    path('buyer_register',views.buyer_register, name="buyer_register"),
    path('',views.buyer_home, name="buyer_home"),


    path('add_buyer_details',views.add_buyer_details, name="add_buyer_details"),

    path('view_buyer_detials//<int:pk>',views.view_buyer_detials, name="view_buyer_detials"),

    path('update_buyer_detials//<int:pk>',views.update_buyer_detials, name="update_buyer_detials"),

    path('view_all_product//<int:pk>',views.view_all_product, name="view_all_product"),

    path('view_category//<int:pk>',views.view_category, name="view_category"),

    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    path('increment_quantity/<int:pk>/', views.increment_quantity, name='increment_quantity'),
    path('decrement_quantity/<int:pk>/', views.decrement_quantity, name='decrement_quantity'),

    path('cart/',views.view_cart, name='cart_view'),

    path('checkout/',views.checkout, name='checkout'),
    path('purchased-products/',views.purchased_products, name='purchased_products'),

    path('check/',views.check, name='check'),
    path('delete_product_cart//<int:pk>',views.delete_product_cart, name='delete_product_cart'),

    path('about/',views.about, name='about'),

    path('gallery/',views.gallery, name='gallery'),

    path('contact/',views.contact, name='contact'),

    path('Signout',views.Signout, name="Signout"),
    
    path('search/',views.search, name='search'),






]