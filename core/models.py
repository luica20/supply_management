from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.contrib.contenttypes.models import ContentType
from PIL import Image


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False)  # Auth relation
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    street = models.CharField(max_length=250, blank=True, null=True)
    nif = models.CharField(max_length=20, unique=True)  # Tax ID
    registration_date = models.DateTimeField(auto_now_add=True)

    def total_purchases(self):
        """Devuelve el número total de compras de este cliente"""
        return self.purchases.count()

    def __str__(self):
        return f"{self.name} (Compras: {self.total_purchases()})"


class Supplier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # Auth relation
    name = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True)
    street = models.CharField(max_length=250, blank=True, null=True)
    nif = models.CharField(max_length=20, unique=True)  # Tax ID

    def total_deliveries(self):
        """Cantidad total de productos entregados por este proveedor"""
        return sum(delivery.quantity for delivery in self.supplierdelivery_set.all())

    def __str__(self):
        return f"{self.name} (Entregas totales: {self.total_deliveries()} unidades)"


class Store(models.Model):
    name = models.CharField(max_length=100)
    street = models.CharField(max_length=250)
    phone = models.CharField(max_length=15, blank=True, null=True)
    image = models.ImageField(
        upload_to="img/product_images/",
        blank=True,
        null=True,
        default="img/sin-imagen.jpg",
        validators=[FileExtensionValidator(["jpg", "png", "jpeg"])]
    )

    def total_stock(self):
        """Calcula el stock total de todos los productos en la tienda"""
        return sum(stock_entry.quantity for stock_entry in self.stock_entries.all())

    def __str__(self):
        # return f"{self.name} (Stock total: {self.total_stock()})"
        return f"{self.name} ({self.street})"


class SupplierStoreRelation(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)
    contract_terms = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('supplier', 'store')  # Evita duplicados de relación

    def __str__(self):
        return f"{self.supplier.name} - {self.store.name}"


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(
        upload_to="img/product_images/",
        blank=True,
        null=True,
        # default="img/sin-imagen.jpg",
        validators=[FileExtensionValidator(["jpg", "png", "jpeg"])]
    )  # 🔹 Agregar campo de imagen

    def save(self, *args, **kwargs):
        """Redimensiona la imagen antes de guardarla"""
        super().save(*args, **kwargs)  # Guarda primero el producto

        if self.image:  # Si hay una imagen, redimensionarla
            image_path = self.image.path
            img = Image.open(image_path)
            img.thumbnail((500, 500))  # Ajusta a 500x500px
            img.save(image_path)

    def __str__(self):
        return self.name


class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_entries')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='stock_entries')
    quantity = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])

    def update_stock(self, amount, movement_type):
        """Actualizar stock y registrar el movimiento"""
        if movement_type == 'OUT' and self.quantity < amount:
            raise ValueError("No hay suficiente stock disponible.")

        self.quantity += amount if movement_type == 'IN' else -amount
        self.save()

        # Registrar movimiento
        StockMovement.objects.create(
            product=self.product,
            store=self.store,
            quantity=amount,
            movement_type=movement_type
        )

    def __str__(self):
        return f"{self.product.name} - {self.store.name}: {self.quantity} unidades"


class StockMovement(models.Model):
    INCREASE = 'IN'
    DECREASE = 'OUT'
    MOVEMENT_CHOICES = [
        (INCREASE, 'Increase'),
        (DECREASE, 'Decrease'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_CHOICES)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.movement_type} {self.quantity} of {self.product.name} at {self.store.name}"


class Purchase(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='purchases')
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def total_amount(self):
        """Calcula el total de la compra sumando los detalles"""
        return sum(detail.total_price() for detail in self.details.all())

    def __str__(self):
        return f"Compra {self.id} - {self.customer.name} (Total: {self.total_amount()}€)"


class PurchaseDetail(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Guardar precio unitario

    def total_price(self):
        """Calcula el total basado en cantidad y precio unitario"""
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity} - {self.unit_price}€ c/u"


class SupplierDelivery(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    delivery_date = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)  # Nuevo campo para aprobación

    def save(self, *args, **kwargs):
        """Actualizar stock en la tienda tras la entrega"""
        super().save(*args, **kwargs)  # Guarda la entrega primero

        if self.approved:
            stock, created = Stock.objects.get_or_create(product=self.product, store=self.store)
            stock.update_stock(self.quantity, "IN")  # Usamos la función update_stock()

    def __str__(self):
        return f"Entrega {self.supplier.name} -> {self.store.name} ({self.quantity} unidades)"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        """Calcula el precio total del carrito"""
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"Carrito de {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Guardar precio unitario

    def total_price(self):
        """Calcula el precio total basado en cantidad y precio unitario"""
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        """Captura el precio del producto al momento de agregarlo al carrito"""
        if not self.unit_price:
            self.unit_price = self.product.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} en {self.store.name}"
