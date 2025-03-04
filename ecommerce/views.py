from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now  # ตรวจสอบว่า import แล้ว
from django.http import JsonResponse
from .models import Product, Category
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .models import User
from .models import Product
from .models import Order, OrderItem
from .forms import RegisterForm, ProductForm, OrderUpdateForm
from django.db.models import Sum, Count
import plotly.graph_objects as go
from django.db.models.functions import TruncMonth

def home(request):
    products = Product.objects.all()

    return render(request, 'home.html', {'products': products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store_admin/product_detail.html', {'product': product})


from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import RegisterForm


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "กรุณากรอกข้อมูลให้ถูกต้อง")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


from django.shortcuts import render
from .models import Cart


def cart_view(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = []

    return render(request, "cart.html", {"cart_items": cart_items})


from django.shortcuts import render
from .models import Order


def order_status_view(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
    else:
        orders = []

    return render(request, "order_status.html", {"orders": orders})


@login_required
def add_product_view(request):
    if request.user.role != 'admin':  # ✅ จำกัดเฉพาะ admin เท่านั้น
        messages.error(request, "คุณไม่มีสิทธิ์เพิ่มสินค้า")
        return redirect('home')

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "เพิ่มสินค้าสำเร็จ!")
            return redirect('home')
    else:
        form = ProductForm()

    return render(request, "add_product.html", {"form": form})


@login_required
def manage_orders(request):
    if request.user.role != 'admin':
        return redirect('home')

    orders = Order.objects.all().order_by('-created_at')
    return render(request, "admin/manage_orders.html", {"orders": orders})


def custom_admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            messages.error(request, "กรุณากรอกชื่อผู้ใช้และรหัสผ่าน")
            return render(request, "store_admin/login.html")  # ✅ Correct path

        user = authenticate(request, username=username, password=password)

        if user and (user.is_superuser or getattr(user, "role", "") == "admin"):
            login(request, user)
            messages.success(request, "เข้าสู่ระบบสำเร็จ!")
            return redirect("admin_dashboard")  # Ensure this URL exists
        else:
            messages.error(request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

    return render(request, "store_admin/login.html")  # ✅ Ensure correct template path


def admin_register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = "admin"
            user.save()
            return redirect("admin_login")
    else:
        form = RegisterForm()
    return render(request, "admin/register.html", {"form": form})


# ✅ 2️⃣ Logout Admin
@login_required
def admin_logout(request):
    logout(request)
    return redirect("admin_login")


@login_required
def admin_dashboard2(request):
    if request.user.role != 'admin':  # ✅ จำกัดเฉพาะแอดมิน
        return redirect('home')

    total_sales = Order.objects.filter(status='completed').count()
    pending_orders = Order.objects.filter(status='preparing').count()
    low_stock_products = Product.objects.filter(stock__lt=10).count()
    products = Product.objects.all()  # ✅ ดึงสินค้าทั้งหมด

    return render(request, "admin/dashboard.html", {
        "total_sales": total_sales,
        "pending_orders": pending_orders,
        "low_stock_products": low_stock_products,
        "products": products
    })


@login_required
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "เพิ่มสินค้าสำเร็จ!")
            return redirect('admin_dashboard')
    else:
        form = ProductForm()

    categories = Category.objects.all()  # ✅ ดึงหมวดหมู่ทั้งหมดมาให้เลือก
    return render(request, "admin/add_product.html", {"form": form, "categories": categories})


@login_required
def manage_products(request):
    if request.user.role != "admin":
        return redirect("home")

    products = Product.objects.all()
    return render(request, "admin/manage_products.html", {"products": products})


@login_required
def edit_product(request, product_id):
    if request.user.role != 'admin':
        return redirect('admin_dashboard')

    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "อัปเดตสินค้าสำเร็จ!")
            return redirect('admin_dashboard')
    else:
        form = ProductForm(instance=product)

    return render(request, "admin/edit_product.html", {"form": form, "product": product})


@login_required
def manage_orders(request):
    if request.user.role != "admin":
        return redirect("home")

    orders = Order.objects.all().order_by("-created_at")
    return render(request, "admin/manage_orders.html", {"orders": orders})


@login_required
def delete_product(request, product_id):
    if request.user.role != 'admin':
        return redirect('admin_dashboard')

    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, "ลบสินค้าสำเร็จ!")
    return redirect('admin_dashboard')


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # ตรวจสอบว่าสินค้ายังมีอยู่ในสต็อกหรือไม่
    if product.stock < 1:
        messages.error(request, f"ขออภัย สินค้า {product.name} หมดสต็อกแล้ว!")
        return redirect("home")

    # ค้นหาในตะกร้าของผู้ใช้ ถ้ามีอยู่แล้วให้เพิ่มจำนวน
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.error(request, f"คุณเพิ่ม {product.name} ถึงจำนวนสูงสุดแล้ว!")
            return redirect("home")

    messages.success(request, f"เพิ่ม {product.name} ลงตะกร้าแล้ว!")
    return redirect("home")


@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total_price": total_price
    })


@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if not cart_items:
        messages.error(request, "ตะกร้าของคุณว่างเปล่า กรุณาเลือกสินค้าก่อน")
        return redirect("home")

    if request.method == "POST":
        pickup_time = request.POST.get("pickup_time")
        payment_method = request.POST.get("payment_method")
        slip_image = request.FILES.get("slip_image") if payment_method == "transfer" else None

        if not pickup_time or not payment_method:
            messages.error(request, "กรุณากรอกข้อมูลให้ครบถ้วน")
            return redirect("checkout")

        # ตรวจสอบว่าสินค้ายังมีในสต็อกหรือไม่
        for item in cart_items:
            if item.quantity > item.product.stock:
                messages.error(request, f"สินค้า {item.product.name} มีสต็อกไม่เพียงพอ!")
                return redirect("cart")

        # ✅ ตรวจสอบว่ามีฟิลด์ `order_date` หรือไม่ ถ้าไม่มีให้ใช้ `created_at`
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            status="preparing",
            payment_method=payment_method,
            slip_image=slip_image,
            pickup_time=pickup_time,
            created_at=now()  # ✅ ใช้ created_at แทน order_date
        )

        # ✅ ลดสต็อกสินค้า
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            item.product.stock -= item.quantity
            item.product.save()

        # ✅ ล้างตะกร้าหลังจากทำการสั่งซื้อ
        cart_items.delete()

        messages.success(request, "ทำการสั่งซื้อสำเร็จ! กรุณารอการดำเนินการ")
        return redirect("order_status")

    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "total_price": total_price
    })


@login_required
def my_orders(request):
    if request.user.role == "admin":  # ✅ ตรวจสอบ role ว่าเป็น admin
        orders = Order.objects.all().order_by("-created_at")  # ✅ แอดมินเห็นออเดอร์ทั้งหมด
    else:
        orders = Order.objects.filter(user=request.user).order_by("-created_at")  # ✅ ผู้ใช้ทั่วไปเห็นเฉพาะของตัวเอง

    return render(request, "admin/my_orders.html", {"orders": orders})  # ✅ ใช้เทมเพลตที่เหมาะสม


@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)  # ✅ ป้องกัน error ถ้า order ไม่มีอยู่จริง

    if request.user.role != "admin":  # ✅ ให้เฉพาะ admin เปลี่ยนสถานะได้
        messages.error(request, "คุณไม่มีสิทธิ์แก้ไขคำสั่งซื้อ")
        return redirect("my_orders")

    if request.method == "POST":
        new_status = request.POST.get("status")  # ✅ ดึงค่าที่เลือกจากฟอร์ม
        order.status = new_status  # ✅ อัปเดตสถานะได้ทุกค่า
        order.save()
        messages.success(request, f"✅ อัปเดตสถานะคำสั่งซื้อ {order.id} เป็น {new_status} สำเร็จ!")

    return redirect("my_orders")


@login_required
def remove_from_cart(request, product_id):
    cart_item = Cart.objects.filter(user=request.user, product_id=product_id).first()

    if cart_item:
        cart_item.delete()
        messages.success(request, "ลบสินค้าออกจากตะกร้าแล้ว!")
    else:
        messages.error(request, "ไม่พบสินค้านี้ในตะกร้าของคุณ")

    return redirect("cart")  # ✅ กลับไปที่หน้าตะกร้า





def product_list(request):
    products = Product.objects.all()  # ดึงสินค้าทั้งหมดจากฐานข้อมูล
    return render(request, 'admin/product_list.html', {'products': products})



def product_form(request):


    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')  # กลับไปยังหน้ารายการสินค้า
    else:
        form = ProductForm()

    return render(request, 'admin/product_form.html', {'form': form})



def product_update(request, pk):


    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "อัปเดตสินค้าสำเร็จ!")
            return redirect('product_list')  # เปลี่ยนเส้นทางกลับไปหน้ารายการสินค้า
    else:
        form = ProductForm(instance=product)
    return render(request, 'admin/product_form.html', {'form': form})


def product_delete(request, pk):

    # ค้นหาสินค้า
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        # ถ้าผู้ใช้ยืนยันการลบ
        product.delete()
        return redirect('product_list')  # เปลี่ยนเส้นทางไปที่หน้ารายการสินค้า

    return render(request, 'admin/product_confirm_delete.html', {'product': product})



def admin_dashboard(request):
    # คำนวณยอดขายรวม
    total_sales = Order.objects.filter(status='completed').aggregate(Sum('total_price'))['total_price__sum'] or 0
    # คำนวณจำนวนคำสั่งซื้อที่รอดำเนินการ
    pending_orders = Order.objects.filter(status='preparing').count()
    # คำนวณจำนวนลูกค้า
    total_customers = Order.objects.values('user').distinct().count()
    # ดึงสินค้าที่เหลือน้อยกว่า 15 ชิ้น
    low_stock_products = Product.objects.filter(stock__lt=15)
    low_stock_count = low_stock_products.count()  # จำนวนสินค้าที่ใกล้หมด


    # กราฟยอดขายรายเดือน
    monthly_sales = Order.objects.filter(status='completed') \
        .annotate(month=TruncMonth('created_at')) \
        .values('month') \
        .annotate(total_sales=Sum('total_price')) \
        .order_by('month')
    months = [sale['month'].strftime('%B %Y') for sale in monthly_sales]
    sales_values = [sale['total_sales'] for sale in monthly_sales]
    monthly_sales_graph = go.Figure(
        data=[go.Scatter(x=months, y=sales_values, mode='lines+markers', marker=dict(color='green'))])


    # สินค้าขายดี 10 อันดับแรก
    top_products = OrderItem.objects.filter(order__status='completed')\
                    .values('product__name')\
                    .annotate(total_sold=Sum('quantity'))\
                    .order_by('-total_sold')[:10]
    product_names = [item['product__name'] for item in top_products]
    product_sold = [item['total_sold'] for item in top_products]
    top_products_graph = go.Figure(data=[go.Bar(x=product_names, y=product_sold, marker=dict(color='blue'))])

    # หมวดหมู่สินค้าที่ขายดีที่สุด
    top_categories = OrderItem.objects.filter(order__status='completed') \
                         .values('product__category') \
                         .annotate(total_sold=Sum('quantity')) \
                         .order_by('-total_sold')[:10]
    category_names = [item['product__category'] for item in top_categories]
    category_sold = [item['total_sold'] for item in top_categories]
    top_categories_graph = go.Figure(data=[go.Bar(x=category_names, y=category_sold, marker=dict(color='red'))])



    # วิธีการชำระเงินที่ผู้ใช้ใช้บ่อยที่สุด
    # วิธีการชำระเงินที่ผู้ใช้ใช้บ่อยที่สุด
    payment_methods = Order.objects.exclude(payment_method=None) \
        .values('payment_method') \
        .annotate(count=Count('payment_method')) \
        .order_by('-count')

    # ตรวจสอบว่าไม่ใช่ค่าที่ว่างเปล่า
    if payment_methods.exists():
        payment_names = [item['payment_method'] for item in payment_methods]
        payment_counts = [item['count'] for item in payment_methods]

        payment_graph = go.Figure(data=[go.Pie(labels=payment_names, values=payment_counts)])
        payment_graph.update_layout(title='วิธีการชำระเงินที่ใช้บ่อยที่สุด')

        payment_graph_html = payment_graph.to_html(full_html=False)
    else:
        payment_graph_html = "<p>ไม่มีข้อมูลการชำระเงิน</p>"

    top_customers = Order.objects.filter(status='completed') \
                        .values('user__username') \
                        .annotate(total_spent=Sum('total_price')) \
                        .order_by('-total_spent')[:10]

    customer_names = [item['user__username'] for item in top_customers]
    customer_spending = [item['total_spent'] for item in top_customers]

    top_customers_graph = go.Figure(data=[go.Bar(
        x=customer_names, y=customer_spending,
        name='ลูกค้า', marker=dict(color='purple')
    )])
    top_customers_graph.update_layout(
        title='ผู้ใช้ที่มียอดสั่งซื้อรวมสูงที่สุด 10 อันดับแรก', xaxis_title='ลูกค้า', yaxis_title='ยอดสั่งซื้อ (บาท)',
        template='plotly'
    )
















    # ดึงข้อมูลหมวดหมู่ทั้งหมดจาก Product และนับจำนวนสินค้าที่อยู่ในหมวดหมู่นั้นๆ
    category_counts = Product.objects.values('category') \
        .annotate(count=Count('id'))  # นับจำนวนสินค้าในแต่ละหมวดหมู่

    # แปลงข้อมูลให้อยู่ในรูปของชื่อหมวดหมู่และจำนวนสินค้า
    category_names = [dict(Product.CATEGORY_CHOICES).get(item['category'], item['category']) for item in
                      category_counts]
    category_quantities = [item['count'] for item in category_counts]

    # สร้างกราฟแสดงจำนวนสินค้าตามหมวดหมู่
    category_graph = go.Figure(data=[go.Bar(
        x=category_names,  # ชื่อหมวดหมู่ทั้งหมดที่ดึงจากฐานข้อมูล
        y=category_quantities,  # จำนวนสินค้าในหมวดหมู่ต่างๆ
        name='สินค้าตามหมวดหมู่',
        marker=dict(color='orange')
    )])

    category_graph.update_layout(
        title='จำนวนสินค้าตามหมวดหมู่',
        xaxis_title='หมวดหมู่สินค้า',
        yaxis_title='จำนวนสินค้า',
        template='plotly',
        xaxis=dict(tickangle=45)  # หมุนแกน X เพื่อให้ชื่อหมวดหมู่แสดงได้ชัดเจน
    )



    # ส่งข้อมูลไปยัง template
    return render(request, 'admin/dashboard.html', {
        'total_sales': total_sales,
        'pending_orders': pending_orders,
        'total_customers': total_customers,
        'monthly_sales_graph': monthly_sales_graph.to_html(full_html=False),
        'top_products_graph': top_products_graph.to_html(full_html=False),
        'category_graph': category_graph.to_html(full_html=False),  # ส่งกราฟจำนวนสินค้าตามหมวดหมู่
        'top_categories_graph': top_categories_graph.to_html(full_html=False),
        'payment_graph': payment_graph_html,
        'low_stock_count': low_stock_count,  # ส่งจำนวนสินค้าใกล้หมด
        'top_customers_graph': top_customers_graph.to_html(full_html=False)
    })

