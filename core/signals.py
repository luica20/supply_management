from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import Customer, Supplier, Product, Purchase, SupplierDelivery


@receiver(post_migrate)
def create_permissions(sender, **kwargs):
    print("📌 Creando permisos y grupos automáticamente...")

    # Definir tipos de contenido
    customer_content_type = ContentType.objects.get_for_model(Customer)
    supplier_content_type = ContentType.objects.get_for_model(Supplier)

    # Crear permisos
    permissions = [
        ('view_own_purchases', 'Can view own purchases', customer_content_type),
        ('manage_own_products', 'Can manage products', supplier_content_type),
        ('manage_deliveries', 'Can manage deliveries', supplier_content_type),
        ('full_access', 'Can access full admin features', ContentType.objects.get_for_model(Customer))
    ]

    for codename, name, content_type in permissions:
        Permission.objects.get_or_create(codename=codename, name=name, content_type=content_type)

    permissions = [
        ('manage_products', 'Can manage products', ContentType.objects.get_for_model(Product)),
        ('view_purchases', 'Can view purchases', ContentType.objects.get_for_model(Purchase)),
    ]

    for codename, name, content_type in permissions:
        Permission.objects.get_or_create(codename=codename, name=name, content_type=content_type)

    delivery_content_type = ContentType.objects.get_for_model(SupplierDelivery)

    # Crear permiso de gestión de entregas
    Permission.objects.get_or_create(
        codename="manage_supplier_deliveries",
        name="Can manage supplier deliveries",
        content_type=delivery_content_type
    )

    # Crear grupos y asignar permisos
    groups = {
        'Customers': ['view_own_purchases', 'view_purchases'],
        'Suppliers': ['manage_own_products', 'manage_deliveries', 'manage_supplier_deliveries', 'manage_products'],
        'Admins': ['full_access']
    }

    for group_name, permission_codenames in groups.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        for codename in permission_codenames:
            permission = Permission.objects.get(codename=codename)
            group.permissions.add(permission)

    print("✅ Permisos y grupos creados correctamente.")

