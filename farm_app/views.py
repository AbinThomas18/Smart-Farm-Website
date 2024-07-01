from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate,login,logout
from .models import *
from django.contrib.auth.decorators import login_required
import os
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest
import cv2
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import joblib
import numpy as np
from django.templatetags.static import static
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.densenet import preprocess_input, decode_predictions

from django.contrib.auth.decorators import login_required
# Create your views here.

def home(request):
    return render(request,'indext.html')

################## farmer panel ########################3



########### weather prediction ############
import requests
from django.shortcuts import render
from datetime import datetime, timedelta

def predict_weather(request):
    if request.method == 'POST':
        try:
            # Make request to OpenWeather API
            api_key = '4668a68e8170a788cba0ed9362c58e3c'
            city = request.POST.get('city')  # Assuming you have a form field for city input
            url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric'  # Request temperature in Celsius
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                # Extract weather forecast for the next day
                forecast_data = []
                tomorrow = (datetime.now() + timedelta(days=1)).date()
                for forecast in data['list']:
                    forecast_date = datetime.strptime(forecast['dt_txt'], '%Y-%m-%d %H:%M:%S').date()
                    if forecast_date == tomorrow:
                        weather_description = forecast['weather'][0]['description']
                        temperature = forecast['main']['temp']  # Extract temperature in Celsius
                        forecast_data.append({'date': forecast_date.strftime('%Y-%m-%d'), 'description': weather_description, 'temperature': temperature})
                        break  # Break after finding the first forecast for the next day
                
                # Return the weather forecast data
                context = {'forecast_data': forecast_data}
                return render(request, 'farmr/weather_pred.html', context)
            else:
                return render(request, 'farmr/weather_pred.html', {'error': 'Failed to fetch weather data'})

        except Exception as e:
            return render(request, 'farmr/weather_pred.html', {'error': str(e)})
        
    return render(request, 'farmr/weather_pred.html')


############## predict rice ###################
# Load your saved model
model = load_model(os.path.join(settings.BASE_DIR, 'model.h5'))

def predict_symptom(image_path):
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    predictions = model.predict(img_array)
    predicted_class = np.argmax(predictions)

    class_names = ['Nitrogen(N)', 'Phosphorus(P)', 'Potassium(K)']  # Replace with your actual class names

    return class_names[predicted_class]



def neutrition_deficiency(request):
    if request.method == 'POST' and request.FILES['image']:
        uploaded_file = request.FILES['image']
        fs = FileSystemStorage()
        image_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
        fs.save(image_path, uploaded_file)

        predicted_symptom = predict_symptom(image_path)

        # Pass the predicted class to the template
        return render(request, 'farmr/rice_plant.html', {'predicted_symptom': predicted_symptom, 'image_path': static(image_path)})

    return render(request,'farmr/rice_plant.html')

############farmer login #################
def farm_login(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        passw = request.POST.get('password')

        user = User.objects.filter(username=uname).first()
        
        if user is not None and user.check_password(passw) and user.is_farmer:
            login(request, user)
            return redirect('farm_home')
        else:
            messages.error(request, 'Invalid login credentials.')

    return render(request,'farmr/login.html')

############farmer register #################
def farm_register(request):
    if request.method == "POST":
        uname = request.POST.get("username")
        passw = request.POST.get("Password")
        if User.objects.filter(username=uname).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'farmer/register.html')
        else:
            user = User.objects.create_user(
                username=uname,
                password=passw,
                is_farmer=True,
            )
            # Add a success message
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('farm_login')
    else:    
        return render(request,'farmr/register.html')
    
################# farmer home page #####################    
def farm_home(request):
    cate = Category.objects.all()
    farmerid=request.user.pk
    view = Product.objects.filter(farmer_id=farmerid)
    
    
    context={
        'cate':cate,
        'view':view
    }
    return render(request,'farmr/index.html',context)

###############  add farmer details ########################
def add_details(request):
    if request.method == "POST":
        # Retrieve form data from request.POST
        name = request.POST.get("name")
        mobile = request.POST.get("phone")
        address = request.POST.get("Address")      
        state = request.POST.get("state")
        district = request.POST.get("district")
        pan = request.POST.get("pan")
        bank = request.POST.get("Bank")

        # Create a new user or retrieve the current user (assuming the donor is logged in)
        if request.user.is_authenticated:
            current_user = request.user
        else:
            current_user = User.objects.create_user(username="a_random_username", password="a_random_password", is_farmer=True)
         # Update the user's details with the form data
        current_user.name = name
        current_user.mobile = mobile
        current_user.address = address
        
        
        current_user.state = state
        current_user.district = district
        current_user.pan = pan
        current_user.bank = bank
        # Save the user object with the updated details
        current_user.save()
        return redirect('farm_home')   
    
    return render(request,'farmr/add_profile.html')

############ view farmer details ########################
def view_detials(request,pk):
    view = get_object_or_404(User, pk=pk, is_farmer=True)
    context={
        'view':view
    }
    return render(request,'farmr/view_profile.html',context)

########## update farmer details ##############
def update_detials(request,pk):
    update = get_object_or_404(User, pk=pk, is_farmer=True)
    if request.method == 'POST':
        update.name=request.POST.get('name')
        update.mobile=request.POST.get('phone')
        update.address=request.POST.get('Address')
        
        
        update.state=request.POST.get('state')
        update.district=request.POST.get('district')
        update.pan=request.POST.get('pan')
        update.bank=request.POST.get('Bank')
        update.save()
        messages.success(request,"Update successfully")
        return redirect('view_detials',pk =update.id)
                
    context={
        'update':update
    }
    return render(request,'farmr/update_profile.html',context)

######## add and view category ###########

def add_category(request):
    add = Category.objects.all()
    if request.method == 'POST':
        add = Category()
        add.name = request.POST.get('name')
        if len(request.FILES)!= 0:
            add.image=request.FILES["img"]
        add.save()
        messages.success(request,'Successfully Complited')
        return redirect('add_category')
    
    context ={
        'add':add
    } 
    return render(request,'farmr/add_categories.html',context)

################### view Category###################

def farmer_view_category(request):
    view = Category.objects.all()
    context ={
        'view':view
    } 
    return render(request,'farmr/view_category.html',context)



############# add product details #################
@login_required
def add_product_details(request):
    category=Category.objects.all()
    if request.method == "POST":
        

        produc=Product()
        
        produc.name=request.POST.get('name')
        produc.stock_in_kg=request.POST.get('stock')

         # Get the category name from the form data
        category_name = request.POST.get('category')
         # Assuming you have a 'Category' model and a field 'name'
        # Retrieve the Category instance based on the name
        category_instance = Category.objects.get(name=category_name)

        produc.category = category_instance


        produc.expiration_date=request.POST.get('expiry')
        produc.price=request.POST.get('price')
        produc.description=request.POST.get('description')
        if len(request.FILES)!= 0:
            produc.images=request.FILES["img"]
        status = request.POST.get("status")
        if status is not None:
            produc.delivery_available = True  # Checkbox was selected
        else:
            produc.delivery_available = False  # Checkbox was not selected
        
        produc.farmer = request.user 

        produc.save()
        return redirect('view_product_details')
    
    context={
        'category':category
    }


    return render(request,'farmr/add_products.html',context)

############# view product details #################

def view_product_details(request):
    farmerid=request.user.pk
    view = Product.objects.filter(farmer_id=farmerid)
    
    context={
        'view':view
    }
    return render(request,'farmr/view_product.html',context)


def view_product(request,pk):
    
    view = Product.objects.get(id=pk)
    
    context={
        'view':view
    }
    return render(request,'farmr/product_details.html',context)
############# edit product details ############

def edit_product_details(request,pk):
    category=Category.objects.all()
    
    edit = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        edit.name=request.POST.get('name')
        edit.stock_in_kg=request.POST.get('stock')
        

         # Get the category name from the form data
        category_name = request.POST.get('category')
         # Assuming you have a 'Category' model and a field 'name'
        # Retrieve the Category instance based on the name
        category_instance = Category.objects.get(name=category_name)

        edit.category = category_instance

        expiration_date=request.POST.get('expiry')
        try:
            # Validate and set the expiration date if it's not empty
            if expiration_date:
                edit.expiration_date = expiration_date
        except ValidationError as e:
            # Handle validation error, e.g., return an error response
            return HttpResponseBadRequest("Invalid date format")


        edit.images=request.POST.get('district')
        edit.price=request.POST.get('price')
        edit.description=request.POST.get('description')

        status = request.POST.get("status")
        if status is not None:
            edit.delivery_available = True  
        else:
            edit.delivery_available = False 
        
        # Check if a new image is provided
        if 'img' in request.FILES:
            # Remove the old image file if it exists
            if edit.images:
                os.remove(edit.images.path)
            # Update the image field with the new file
            edit.images = request.FILES['img']
        edit.save()
        messages.success(request,"Update successfully")
        return redirect('view_product_details')

    context={
        'edit':edit,
        'category':category
        
    }
    return render(request,'farmr/update_products.html',context)

################### delete product ####################

def delete_product_details(request,pk):
    del_produc=Product.objects.filter(id=pk)
    del_produc.delete()
    return redirect('view_product_details')

############ view Sold Product ################
def view_buyer(request):
    if request.user.is_farmer:
        # Get all sold products for the current farmer
        sold_products = PurchaserProduct.objects.filter(product__farmer=request.user)
        context={
            'sold_products': sold_products
            }
    return render(request,'farmr/sold_product.html',context)

############### view sold Product details #################
def sold_product_detail(request, product_id):
    if request.user.is_farmer:
        # Get the details of a sold product
        sold_product = get_object_or_404(PurchaserProduct, id=product_id, product__farmer=request.user)
    return render(request, 'farmr/sold_prodct_details.html', {'sold_product': sold_product}) 

#################categry###############3

def cate_details(request,pk):
    if request.user.is_farmer:
        category = Category.objects.get(id=pk)
        # Get the products in the category added by the current farmer
        view = Product.objects.filter(category=category, farmer=request.user) 
    context ={
        'view':view,             
    } 
    return render(request,'farmr/cat_details.html',context)

############logout farmer ####################

def SignOut(request):
     logout(request)
     return redirect('buyer_home')


#################  ###  buyer panel #######################
######################################################

############Buyer register #################
def buyer_register(request):
    if request.method == "POST":
        uname = request.POST.get("username")
        passw = request.POST.get("Password")
        if User.objects.filter(username=uname).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'buyr/register.html')
        else:
            user = User.objects.create_user(
                username=uname,
                password=passw,
                is_buyer=True,
            )
            user.save()
            # Add a success message
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('buyer_login')
    else:    
        return render(request,'buyr/register.html')
    
############buyer login #################
def buyer_login(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        passw = request.POST.get('password')

        user = User.objects.filter(username=uname).first()
        
        if user is not None and user.check_password(passw) and user.is_buyer:
            login(request, user)
            return redirect('buyer_home')
        else:
            messages.error(request, 'Invalid login credentials.')

    return render(request,'buyr/login.html')

########## buyer home ############

def buyer_home(request):
    view =Product.objects.all()
    cate = Category.objects.all()
    user = request.user
    cart_items = []
    total_price = 0
    no_of_prd = 0
    if user.is_authenticated:
        
        cart, created = Cart.objects.get_or_create(user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        no_of_prd= cart_items.count()

        for item in cart_items:
            item.total = item.product.price * item.quantity

        total_price = sum(item.total for item in cart_items)

   
    context={
        'view':view,
        'cate':cate,
        'cart_items': cart_items,
        'total_price': total_price,
        'no_of_prd':no_of_prd
    }
    return render(request,'buyr/index.html',context)

###############  add buyer details ########################
@login_required(login_url='buyer_login')
def add_buyer_details(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    cart_items = CartItem.objects.filter(cart=cart)
    no_of_prd= cart_items.count()

    for item in cart_items:
        item.total = item.product.price * item.quantity

    total_price = sum(item.total for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'no_of_prd':no_of_prd
    }
    if request.method == "POST":
        # Retrieve form data from request.POST
        name = request.POST.get("name")
        mobile = request.POST.get("phone")
        address = request.POST.get("Address")      
        state = request.POST.get("state")
        district = request.POST.get("district")
        pan = request.POST.get("pan")
        bank = request.POST.get("Bank")

        # Create a new user or retrieve the current user (assuming the donor is logged in)
        if request.user.is_authenticated:
            current_user = request.user
        else:
            current_user = User.objects.create_user(username="a_random_username", password="a_random_password", is_buyer=True)
         # Update the user's details with the form data
        current_user.name = name
        current_user.mobile = mobile
        current_user.address = address
        
        
        current_user.state = state
        current_user.district = district
        current_user.pan = pan
        current_user.bank = bank
        # Save the user object with the updated details
        current_user.save()
        return redirect('buyer_home')   
    
    return render(request,'buyr/add_profile.html',context)

############ view buyer details ########################
@login_required(login_url='buyer_login')
def view_buyer_detials(request,pk):
    view = get_object_or_404(User, pk=pk, is_buyer=True)
    context={
        'view':view
    }
    return render(request,'buyr/view_profile.html',context)

########## update buyer details ##############
@login_required(login_url='buyer_login')
def update_buyer_detials(request,pk):
    update = get_object_or_404(User, pk=pk, is_buyer=True)
    if request.method == 'POST':
        update.name=request.POST.get('name')
        update.mobile=request.POST.get('phone')
        update.address=request.POST.get('Address')
        
        
        update.state=request.POST.get('state')
        update.district=request.POST.get('district')
        update.pan=request.POST.get('pan')
        update.bank=request.POST.get('Bank')
        update.save()
        messages.success(request,"Update successfully")
        return redirect('view_buyer_detials',pk =update.id)
                
    context={
        'update':update
    }
    return render(request,'buyr/update_profile.html',context)


####### view all products details############

def view_all_product(request,pk):
    user = request.user
    cart_items = []
    total_price = 0
    no_of_prd = 0
    if user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        no_of_prd= cart_items.count()

        for item in cart_items:
            item.total = item.product.price * item.quantity

        total_price = sum(item.total for item in cart_items)


    view =Product.objects.get(pk=pk)
    context={
        'view':view,
        'cart_items': cart_items,
        'total_price': total_price,
        'no_of_prd':no_of_prd
    }
    return render(request,'buyr/view_product_details.html',context)

################### view Category###################

def view_category(request,pk):
    user = request.user
    cart_items = []
    total_price = 0
    no_of_prd = 0
    if user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        no_of_prd= cart_items.count()

        for item in cart_items:
            item.total = item.product.price * item.quantity

        total_price = sum(item.total for item in cart_items)

    
    
    category = Category.objects.get(id=pk)

    view = Product.objects.filter(category=category)

    context ={
        'view':view,
        'cart_items': cart_items,
        'total_price': total_price,
        'no_of_prd':no_of_prd
        
    } 
    return render(request,'buyr/view_category.html',context)



############ add to cart ###############

@login_required(login_url='buyer_login')
def add_to_cart(request, product_id):
    product = Product.objects.get(pk=product_id)
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart_view')

@login_required(login_url='buyer_login')
def view_cart(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    cart_items = CartItem.objects.filter(cart=cart)
    no_of_prd= cart_items.count()
    

    for item in cart_items:
        item.total = item.product.price * item.quantity

    total_price = sum(item.total for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'no_of_prd':no_of_prd
    }

    return render(request, 'buyr/cart.html', context)

########increas quantity
from django.db.models import F
def increment_quantity(request, pk):
    cart_item = CartItem.objects.get(id=pk)
    cart_item.quantity += 1
    cart_item.save()

    # Update the total price of the item
    cart_item.total = F('product__price') * F('quantity')
    cart_item.save()

    # Update the total price of the cart
    cart = cart_item.cart
    cart_items = CartItem.objects.filter(cart=cart)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    cart.total_price = total_price
    cart.save()
    return redirect('cart_view')

############# decrease quantity

def decrement_quantity(request, pk):
    cart_item = CartItem.objects.get(id=pk)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()

        # Update the total price of the item
        cart_item.total = cart_item.product.price * cart_item.quantity
        cart_item.save()

        # Update the total price of the cart
        cart = cart_item.cart
        cart_items = CartItem.objects.filter(cart=cart)
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        cart.total_price = total_price
        cart.save()

    return redirect('cart_view')

########### checkout ################


@login_required(login_url='buyer_login')
def checkout(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    cart_items = CartItem.objects.filter(cart=cart)
    

    # Create PurchaserProduct instances for each item in the cart
    for item in cart_items:
        PurchaserProduct.objects.create(user=user, product=item.product, quantity=item.quantity)

    # Clear the cart after creating purchaser products
    cart.products.clear()

    # Redirect to the page displaying purchaser products
    # return redirect('purchased_products')
    return render(request,'buyr/place_order.html')


############ displaying purchaser products###############

@login_required(login_url='buyer_login')
def purchased_products(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    cart_items = CartItem.objects.filter(cart=cart)
    no_of_prd= cart_items.count()

    for item in cart_items:
        item.total = item.product.price * item.quantity

    total_price = sum(item.total for item in cart_items)

    
    user = request.user
    
    purchased_products = PurchaserProduct.objects.filter(user=user)
      
    context = {
        'purchased_products': purchased_products,
        'cart_items': cart_items,
        'total_price': total_price,
        'no_of_prd':no_of_prd
        
    }

    return render(request, 'buyr/purchased_product.html', context)

@login_required(login_url='buyer_login')
def check(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    cart_items = CartItem.objects.filter(cart=cart)
    no_of_prd= cart_items.count()

    for item in cart_items:
        item.total = item.product.price * item.quantity

    total_price = sum(item.total for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'no_of_prd':no_of_prd
    }
    return render(request,'buyr/checkout.html',context)


############ remove product from cart ################
@login_required(login_url='buyer_login')
def delete_product_cart(request,pk):
    del_produc=CartItem.objects.filter(id=pk)
    del_produc.delete()
    return redirect('cart_view')



########### about ##############

def about(request): 
    user = request.user
    cart_items = []
    total_price = 0
    no_of_prd = 0
    if user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        no_of_prd= cart_items.count()

        for item in cart_items:
            item.total = item.product.price * item.quantity

        total_price = sum(item.total for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'no_of_prd':no_of_prd
    }
    return render(request,'buyr/about.html',context)

########## gallery ###########

def gallery(request):
    user = request.user
    cart_items = []
    total_price = 0
    no_of_prd = 0
    if user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        no_of_prd= cart_items.count()

        for item in cart_items:
            item.total = item.product.price * item.quantity

        total_price = sum(item.total for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'no_of_prd':no_of_prd
    }
    return render(request,'buyr/gallery.html',context)

############ contact ###################

def contact(request):
    user = request.user
    cart_items = []
    total_price = 0
    no_of_prd = 0
    if user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        no_of_prd= cart_items.count()

        for item in cart_items:
            item.total = item.product.price * item.quantity

        total_price = sum(item.total for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'no_of_prd':no_of_prd
    }
    return render(request,'buyr/contact-us.html',context)

############Buyer Logout ####################
@login_required(login_url='buyer_login')
def Signout(request):
     logout(request)
     return redirect('buyer_home')
 
 ############ search product ############
 
def search(request):
    
    
    user = request.user
    cart_items = []
    total_price = 0
    no_of_prd = 0
    if user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        no_of_prd= cart_items.count()

        for item in cart_items:
            item.total = item.product.price * item.quantity

        total_price = sum(item.total for item in cart_items)
        
    query = request.GET.get('search', '')
    products = Product.objects.filter(name__icontains=query)
    categories = Category.objects.filter(name__icontains=query)
    
    context = {
        'query': query,
        'products': products,
        'categories': categories,
        'cart_items': cart_items,
        'total_price': total_price,
        'no_of_prd':no_of_prd
    }
    
    return render(request,'buyr/search_result.html', context)