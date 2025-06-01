
# import matplotlib
# matplotlib.use("Agg")  # Evita intentos de GUI en un entorno de servidor

import csv
import os
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from django.shortcuts import render
from django.db.models import Sum
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomerForm, SupplierForm, CustomLoginForm, CustomUserCreationForm, TransferProductForm, \
    SupplierDeliveryForm
from django.contrib.auth.decorators import login_required, permission_required

from .models import SupplierDelivery, Stock, Product, Store, Purchase, PurchaseDetail, Cart, CartItem, Supplier


def home(request):
    contexto = {
        'message': '¡Welcome to my technology supplies store!',
    }
    return render(request, 'core/home.html', contexto)


def store(request):
    stores = Store.objects.all()
    contexto = {
        'stores': stores,
    }
    return render(request, 'core/store.html', contexto)


def store_products(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    request.session['store_id'] = store.id
    # Filtrar productos que tengan stock disponible en alguna tienda
    products = Product.objects.filter(stock_entries__quantity__gt=0, stock_entries__store_id=store_id).distinct()
    for product in products:
        image_path = os.path.join(settings.MEDIA_ROOT, str(product.image))
        if not os.path.exists(image_path):
            product.image = "img/sin-imagen.jpg"  # 🔹 Imagen por defecto si no existe

    return render(request, 'core/list_product.html', {'store': store, 'products': products})


def register_customer(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)  # Creación del usuario
        customer_form = CustomerForm(request.POST)  # Creación del cliente

        if user_form.is_valid() and customer_form.is_valid():
            # 🔹 Primero guardamos el usuario
            user = user_form.save()
            user.set_password(request.POST['nif'])  # 🔹 Encripta la contraseña correctamente
            user.email = request.POST['email']
            user.save()

            # 🔹 Luego guardamos el Customer, pasándole el usuario como parámetro
            customer = customer_form.save(commit=False, user=user)
            customer.save()

            # 🔹 Asignamos el grupo correspondiente
            group = Group.objects.get(name='Customers')
            user.groups.clear()
            user.groups.add(group)

            print(f"✅ Usuario '{user.username}' asignado al grupo 'Customers'.")
            return redirect('home')
    else:
        user_form = CustomUserCreationForm()
        customer_form = CustomerForm()

    return render(request, 'core/register_customer.html', {'user_form': user_form, 'customer_form': customer_form})


def user_login(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Redirección basada en el grupo del usuario
            if user.groups.filter(name="Admins").exists():
                return redirect('admin_dashboard')
            elif user.groups.filter(name="Suppliers").exists():
                return redirect('supplier_dashboard')
            elif user.groups.filter(name="Customers").exists():
                return redirect('customer_dashboard')
            else:
                return redirect('home')
    else:
        form = CustomLoginForm()

    return render(request, 'core/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('home')  # Redirigir a la página principal tras cerrar sesión


@login_required
@permission_required('core.full_access', raise_exception=True)
def admin_dashboard(request):
    # Filtrar entregas que aún no han sido aprobadas
    pending_deliveries = SupplierDelivery.objects.filter(approved=False).order_by("-delivery_date")

    return render(request, "core/dashboard/admin.html", {
        "pending_deliveries": pending_deliveries
    })


@login_required
@permission_required('core.full_access', raise_exception=True)
def load_products(request):
    archivos = {
        "stores": "static/img/product_images/stores.csv",
        "products": "static/img/product_images/products.csv",
        "stock": "static/img/product_images/stock.csv"
    }
    for tipo, archivo in archivos.items():
        if os.path.exists(archivo):
            print(f"✅ Cargando {tipo} desde {archivo}")
            with open(archivo, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                # 🔹 Carga de tiendas (`stores.csv`)
                if tipo == "stores":
                    for row in reader:
                        store = Store.objects.create(
                            name=row['name'],
                            street=row['street'],
                            phone=row['phone']
                        )
                        store.save()
                        print(f"✅ Tienda {store.name} cargada correctamente.")

                # 🔹 Carga de productos (`products.csv`)
                elif tipo == "products":
                    for row in reader:
                        product = Product.objects.create(
                            name=row['name'],
                            description=row['description'],
                            price=row['price']
                        )
                        product.save()
                        print(f"✅ Producto {product.name} cargado correctamente.")

                # 🔹 Carga de stock (`stock.csv`)
                elif tipo == "stock":
                    for row in reader:
                        store = Store.objects.filter(name=row['store_name']).first()
                        product = Product.objects.filter(name=row['product_name']).first()
                        if store and product:
                            stock, created = Stock.objects.get_or_create(
                                store=store,
                                product=product
                            )
                            stock.quantity = int(row['quantity'])
                            stock.save()
                            print(f"✅ Stock actualizado: {stock.quantity} unidades de {product.name} en {store.name}.")
                        else:
                            print(
                                f"❌ Error: No se encontró la tienda/producto {row['store_name']} - {row['product_name']}.")
        else:
            print(f"❌ El archivo {archivo} no existe.")

    return redirect('home')


@login_required
@permission_required('core.full_access', raise_exception=True)
def store_dashboard(request):
    stores = Store.objects.all()
    stock_entries = Stock.objects.all()
    return render(request, 'core/dashboard/store_dashboard.html', {'stores': stores, 'stock_entries': stock_entries})


@login_required
@permission_required('core.full_access', raise_exception=True)
def transfer_product(request):
    if request.method == 'POST':
        form = TransferProductForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            from_store = form.cleaned_data['from_store']
            to_store = form.cleaned_data['to_store']
            quantity = form.cleaned_data['quantity']

            from_stock = Stock.objects.filter(product=product, store=from_store).first()
            to_stock, created = Stock.objects.get_or_create(product=product, store=to_store)

            if from_stock and from_stock.quantity >= quantity:
                from_stock.update_stock(quantity, 'OUT')  # Usa update_stock()
                to_stock.update_stock(quantity, 'IN')  # Usa update_stock()
                print(
                    f"✅ Transferencia exitosa: {quantity} unidades de '{product.name}' de '{from_store.name}' a '{to_store.name}'.")
                return redirect('store_dashboard')
            else:
                print("❌ Error: Stock insuficiente para la transferencia.")

    else:
        form = TransferProductForm()

    return render(request, 'core/dashboard/transfer_product.html', {'form': form})


@login_required
@permission_required('core.full_access', raise_exception=True)
def register_supplier(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)  # Creación del usuario
        supplier_form = SupplierForm(request.POST)  # Creación del proveedor

        if user_form.is_valid() and supplier_form.is_valid():
            # 🔹 Primero guardamos el usuario
            user = user_form.save()
            user.set_password(request.POST['nif'])  # 🔹 Encripta la contraseña correctamente
            user.email = request.POST['email']
            user.save()

            # 🔹 Luego guardamos el Customer, pasándole el usuario como parámetro
            customer = supplier_form.save(commit=False, user=user)
            customer.save()

            # 🔹 Asignamos el grupo correspondiente
            group = Group.objects.get(name='Suppliers')
            user.groups.clear()
            user.groups.add(group)

            return redirect('home')

    else:
        user_form = CustomUserCreationForm()
        supplier_form = SupplierForm()

    return render(request, 'core/register_supplier.html', {'user_form': user_form, 'supplier_form': supplier_form})


@staff_member_required
def approve_delivery(request, delivery_id):
    delivery = get_object_or_404(SupplierDelivery, id=delivery_id)

    if not delivery.approved:
        delivery.approved = True
        delivery.save()

    return redirect('admin_dashboard')  # Redirigir después de aprobar


@login_required
@permission_required('core.manage_products', raise_exception=True)
def supplier_dashboard(request):
    supplier = get_object_or_404(Supplier, user=request.user)

    # Obtener todas las entregas realizadas por el proveedor
    deliveries = SupplierDelivery.objects.filter(supplier=supplier).order_by('-delivery_date')
    form = SupplierDeliveryForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        delivery = form.save(commit=False)
        delivery.supplier = supplier
        delivery.save()
        return redirect('supplier_dashboard')  # Redirigir después de registrar la entrega

    return render(request, "core/dashboard/supplier.html", {
        "supplier": supplier,
        "deliveries": deliveries,
        "form": form
    })


@login_required
@permission_required('core.manage_supplier_deliveries', raise_exception=True)
def supplier_delivery_dashboard(request):
    deliveries = SupplierDelivery.objects.all()
    return render(request, 'core/supplier_deliveries.html', {'deliveries': deliveries})

def product_delivery_report(request):
    # Consultar entregas agrupadas por producto y tienda
    deliveries = SupplierDelivery.objects.values("store__name", "product__name").filter(approved=True).annotate(total_quantity=Sum("quantity")).order_by("-total_quantity")[:10]

    # Extraer los datos
    stores = [d["store__name"] for d in deliveries]
    products = [d["product__name"] for d in deliveries]
    quantities = [d["total_quantity"] for d in deliveries]

    # Crear gráfico de barras con los 10 primeros productos
    plt.figure(figsize=(12, 6))
    # plt.bar(products, quantities)
    sns.barplot(x=products, y=quantities, hue=stores)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.xlabel("Producto")
    plt.ylabel("Cantidad entregada")
    plt.title("Top 10 Productos más entregados por tienda")
    plt.tight_layout()

    # Guardar en un buffer de memoria
    bar_buffer = io.BytesIO()
    plt.savefig(bar_buffer, format="png")
    bar_buffer.seek(0)
    bar_chart = base64.b64encode(bar_buffer.getvalue()).decode("utf-8")
    bar_buffer.close()

    # Crear gráfico de pastel
    plt.figure(figsize=(7, 7))
    plt.pie(quantities, labels=products, autopct="%1.2f%%", colors=sns.color_palette("pastel"))
    plt.title("Distribución de productos entregados")

    # Guardar en otro buffer de memoria
    pie_buffer = io.BytesIO()
    plt.savefig(pie_buffer, format="png")
    pie_buffer.seek(0)
    pie_chart = base64.b64encode(pie_buffer.getvalue()).decode("utf-8")
    pie_buffer.close()

    return render(request, "core/reports/product_delivery_report.html", {
        "bar_chart": bar_chart,
        "pie_chart": pie_chart,
    })




@login_required
@permission_required('core.view_own_purchases', raise_exception=True)
def customer_dashboard(request):
    return render(request, 'core/dashboard/customer.html')


@login_required
def view_cart(request):
    # cart = Cart.objects.filter(user=request.user).first()
    cart = Cart.objects.get(user=request.user)
    store_id = cart.items.first().store.id if cart.items.exists() else None

    cart_items = cart.items.all()
    # Calcular el total del carrito
    total_cart = sum(item.total_price() for item in cart_items)

    return render(request, 'core/cart.html',
                  {'cart': cart, 'store_id': store_id, "cart_items": cart_items, "total_cart": total_cart})


@login_required
def add_to_cart(request, product_id, store_id):
    product = get_object_or_404(Product, id=product_id)
    store = get_object_or_404(Store, id=store_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Verificar si el producto ya está en el carrito dentro de esa tienda
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product, store=store)

    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    # Actualizar la sesión para reflejar el número de productos en el carrito
    request.session['count_cart'] = sum(item.quantity for item in cart.items.all())

    return JsonResponse({'count_cart': request.session['count_cart']})


@login_required
def purchase_history(request):
    purchases = request.user.customer.purchases.all().order_by('-date')
    return render(request, 'core/dashboard/purchase_history.html', {'purchases': purchases})


@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)

    cart_item.delete()

    # Actualizar la sesión para reflejar la nueva cantidad de productos en el carrito
    cart = Cart.objects.get(user=request.user)
    request.session['count_cart'] = sum(item.quantity for item in cart.items.all())

    return JsonResponse({'count_cart': request.session['count_cart']})


@login_required
def confirm_purchase(request):
    cart = Cart.objects.get(user=request.user)

    if not cart.items.exists():
        return redirect("cart_view")  # Evitar compras vacías

    # Crear la compra
    purchase = Purchase.objects.create(customer=request.user.customer, store=cart.items.first().store)

    # Registrar los detalles de compra
    for item in cart.items.all():
        PurchaseDetail.objects.create(
            purchase=purchase,
            product=item.product,
            quantity=item.quantity,
            unit_price=item.unit_price
        )

        # Actualizar stock del producto en la tienda
        stock = Stock.objects.get(product=item.product, store=item.store)

        if stock.quantity >= item.quantity:  # Evitar stock negativo
            stock.update_stock(item.quantity, 'OUT')  # Usa update_stock()

    # Vaciar el carrito después de la compra
    cart.items.all().delete()
    request.session['count_cart'] = 0  # Resetear contador

    return redirect("purchase_history")  # Redirigir al historial de compras
