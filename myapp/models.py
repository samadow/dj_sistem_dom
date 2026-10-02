from django.db import models


class User(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
        ('manager', 'Manager'),
    )

    role = models.CharField(max_length=20,choices=ROLE_CHOICES,default='user')
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=50)

    def __str__(self):
        return self.username


class Building(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255)
    map_url = models.URLField(blank=True)
    total_floors = models.PositiveIntegerField()
    status = models.CharField(max_length=30, default="building")
    handover_date = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to="buildings/", blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Apartment(models.Model):
    STATUS_CHOICES = (
        ('available', 'Озод'),
        ('booked', 'Брон шудааст'),
        ('sold', 'Фурӯхта шудааст'),
    )

    building = models.ForeignKey(
        Building, on_delete=models.PROTECT, related_name="apartments"
    )
    number = models.PositiveIntegerField()
    floor = models.PositiveIntegerField()
    rooms = models.PositiveIntegerField()
    area = models.DecimalField(max_digits=8, decimal_places=2)
    price = models.DecimalField(max_digits=14, decimal_places=2)
    description = models.TextField(blank=True)
    balcony = models.BooleanField(default=False)
    image = models.ImageField(upload_to="apartments/", blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["building", "number"],
                name="unique_apartment_number",
            )
        ]

    def __str__(self):
        return f"{self.building.name} — хона №{self.number}"


class Inquiry(models.Model):
    apartment = models.ForeignKey(Apartment, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} — {self.apartment}"


class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Дар интизорӣ'),
        ('confirmed', 'Тасдиқшуда'),
        ('rejected', 'Радшуда'),
        ('cancelled', 'Бекоршуда'),
    )

    apartment = models.ForeignKey(Apartment, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} — {self.apartment}"


class Sale(models.Model):
    apartment = models.OneToOneField(Apartment, on_delete=models.PROTECT)
    buyer = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,)
    buyer_name = models.CharField(max_length=100)
    buyer_phone = models.CharField(max_length=30)
    final_price = models.DecimalField(max_digits=14, decimal_places=2)
    sold_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.apartment} — {self.buyer_name}"
