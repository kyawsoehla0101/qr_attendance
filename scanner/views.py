# scanner/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import QRLog
import json, qrcode, io
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
import csv
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw


from django.utils.dateparse import parse_date
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect

def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('scan_page')  # Redirect after register
    else:
        form = UserCreationForm()
    return render(request, 'scanner/register.html', {'form': form})

@login_required
def scan_page(request):
    return render(request, "scanner/scan.html")

@csrf_exempt
def receive_qr(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        qr_text = data.get("code")
        try:
            user_id, name = qr_text.split('|')
            user = User.objects.get(id=int(user_id))
        except:
            return JsonResponse({'status': 'error', 'message': 'Invalid QR code'})

        last_log = QRLog.objects.filter(user=user).last()
        direction = 'in' if not last_log or last_log.direction == 'out' else 'out'

        QRLog.objects.create(user=user, direction=direction)
        return JsonResponse({'status': 'ok', 'direction': direction})
    return JsonResponse({'status': 'invalid'}, status=400)
@login_required
def users_list(request):
    users = User.objects.all()
    return render(request, "scanner/users.html", {"users": users})

def generate_qr(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = getattr(user, 'userprofile', None)
    qr_content = f"{user.id}|{user.get_full_name() or user.username}"

    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(qr_content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    if profile and profile.photo:
        try:
            photo_path = profile.photo.path
            logo = Image.open(photo_path).convert("RGBA")
            logo = logo.resize((img.size[0] // 4, img.size[1] // 4), Image.LANCZOS)

            # Create circular mask
            mask = Image.new('L', logo.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, logo.size[0], logo.size[1]), fill=255)

            circular_logo = Image.new("RGBA", logo.size)
            circular_logo.paste(logo, (0, 0), mask)

            pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
            img.paste(circular_logo, pos, mask=circular_logo)
        except Exception as e:
            print("Failed to insert circular photo:", e)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return HttpResponse(buf.read(), content_type="image/png")



@staff_member_required
def export_logs_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="qr_logs.pdf"'
    p = canvas.Canvas(response)

    logs = QRLog.objects.select_related('user').all()
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, 800, "QR Attendance Logs")

    y = 770
    p.setFont("Helvetica", 10)
    for log in logs:
        p.drawString(50, y, f"{log.user.username} - {log.direction} - {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        y -= 15
        if y < 50:
            p.showPage()
            y = 800
            p.setFont("Helvetica", 10)

    p.showPage()
    p.save()
    return response


@login_required
def qr_logs_view(request):
    logs = QRLog.objects.select_related('user').all()

    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    if start_date and end_date:
        logs = logs.filter(timestamp__date__range=(start_date, end_date))

    return render(request, "scanner/logs.html", {
        "logs": logs,
        "start": start_date,
        "end": end_date
    })