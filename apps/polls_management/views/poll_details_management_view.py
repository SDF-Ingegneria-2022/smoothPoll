import datetime
from typing import List
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_service import PollService
from apps.polls_management.services.poll_token_service import PollTokenService
import qrcode
from qrcode.image.pure import PyPNGImage
from django.core.paginator import Paginator
from django.template.loader import get_template
from django.views import View
import os
import io
from django.http import FileResponse
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm


def link_callback(uri, rel):
    # harcoded to escape the first /
    return uri[1:]
        

def poll_details(request: HttpRequest, poll_id: int):
    """Render the details page for a poll"""
    try:
        # Retrieve poll
        poll: PollModel = PollService.get_poll_by_id(poll_id)
    except Exception:
        raise Http404(f"Poll with id {poll_id} not found.")
    
    if poll.is_votable_token():
        host_link: str = request.get_host()
        token_links: List[str] = PollTokenService.available_token_list(host_link, poll)
        invalid_tokens: List[str] = PollTokenService.unavailable_token_list(host_link, poll)
        return render(request, 'votes_results/poll_details.html', {'poll': poll, 'token_list': token_links, 'invalid_tokens': invalid_tokens})
    else:
        # Render vote form (with eventual error message)
        return render(request, 'votes_results/poll_details.html', {'poll': poll})

def poll_qr_code(request: HttpRequest, poll_id: int):
    """Render the details page for a poll"""
    try:
        # Retrieve poll
        poll: PollModel = PollService.get_poll_by_id(poll_id)
    except Exception:
        raise Http404(f"Poll with id {poll_id} not found.")
    
    if poll.is_votable_token():
        path = 'static/qr_codes/'
        if not os.path.exists(path):
            os.makedirs(path)
        host_link: str = request.get_host()
        query_links: List[str] = PollTokenService.available_token_list(host_link, poll)["query_list"]
        token_links: List[str] = PollTokenService.available_token_list(host_link, poll)["token_list"]
        qr_codes: List[str] = []
        for link, query in zip(token_links, query_links):
            img = qrcode.make(link, image_factory=PyPNGImage)
            name_img :str= str(poll_id) + str(query[1:])+'.png'
            qr_codes.append({'name_img':name_img,'link':link, 'token':query[7:]})
            img.save(f'static/qr_codes/{name_img}')
        paginator = Paginator(qr_codes, 20)
        page_number = request.GET.get('page')
        if(page_number is None):
            page_number=1
        page_obj = paginator.get_page(page_number)
        return render(request, 'polls_management/print_qr_code.html', 
                      {'poll': poll, 'page_obj':page_obj, 'print':False, 'page_number':page_number})
    else:
        return render(request, 'polls_management/print_qr_code.html', {'poll': poll })


def pdf_download(request,poll_id:int, page_number:int):
    try:
        # Retrieve poll
        poll: PollModel = PollService.get_poll_by_id(poll_id)
    except Exception:
        raise Http404(f"Poll with id {poll_id} not found.")
    if poll.is_votable_token():
        path = 'static/qr_codes'
        if not os.path.exists(path):
            os.makedirs(path)
        host_link: str = request.get_host()
        query_links: List[str] = PollTokenService.available_token_list(host_link, poll)["query_list"]
        token_links: List[str] = PollTokenService.available_token_list(host_link, poll)["token_list"]
        qr_codes: List[str] = []
        for link, query in zip(token_links, query_links):
            name_img :str= str(poll_id) + str(query[1:])+'.png'
            qr_codes.append({'name_img':name_img,'link':link, 'token':query[7:]})
        paginator = Paginator(qr_codes, 20)
        page_obj = paginator.get_page(page_number)

    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)
    p.setPageSize(A4)
    p.setTitle("Qr code")
    document_width, document_height = A4
    image_width, image_height = 2.5*cm, 2.5*cm
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    y1 = document_height
    for index in range(len(page_obj.object_list)):
        if(index%2==0):
            x1 = 0*cm
            y1 = y1 - image_height - 0.3*cm 
            p.line(x1,y1-0.1*cm,document_width/2,y1-0.1*cm)
        else:
            x1 = document_width/2
            p.line(document_width/2,y1-0.1*cm,document_width,y1-0.1*cm)
        image = path+'/'+page_obj.object_list[index]['name_img']
        p.setFont("Helvetica-Bold", 8, leading=None)
        p.drawString(x1+3.5*cm,y1+2*cm,poll.name)
        p.setFont("Helvetica", 8, leading=None)
        p.drawString(x1+3.2*cm,y1+1.5*cm,"Scansiona il QR-Code oppure usa il link.")
        p.drawString(x1+3*cm,y1+1*cm,"Se ti viene chiesto, inserisci questo codice:")
        p.setFont("Helvetica-Bold", 8, leading=None)
        p.drawString(x1+3*cm,y1+0.5*cm,page_obj.object_list[index]['token'])
        p.drawString(x1+2.5*cm,y1+0.2,page_obj.object_list[index]['link'])
        p.drawImage(image, x=x1,y=y1,width=image_width,height=image_height)
    p.line(document_width/2, document_height,document_width/2, y1)


    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    filename = f'{poll.name} pagina {page_number}.pdf'
    return FileResponse(buffer, as_attachment=True, filename=filename)


def pdf_view(request,poll_id:int, page_number:int):
    try:
        # Retrieve poll
        poll: PollModel = PollService.get_poll_by_id(poll_id)
    except Exception:
        raise Http404(f"Poll with id {poll_id} not found.")
    if poll.is_votable_token():
        path = 'static/qr_codes'
        if not os.path.exists(path):
            os.makedirs(path)
        host_link: str = request.get_host()
        query_links: List[str] = PollTokenService.available_token_list(host_link, poll)["query_list"]
        token_links: List[str] = PollTokenService.available_token_list(host_link, poll)["token_list"]
        qr_codes: List[str] = []
        for link, query in zip(token_links, query_links):
            name_img :str= str(poll_id) + str(query[1:])+'.png'
            qr_codes.append({'name_img':name_img,'link':link, 'token':query[7:]})
        paginator = Paginator(qr_codes, 20)
        page_obj = paginator.get_page(page_number)

    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)
    p.setPageSize(A4)
    p.setTitle("Qr code")
    document_width, document_height = A4
    image_width, image_height = 2.5*cm, 2.5*cm
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    y1 = document_height
    for index in range(len(page_obj.object_list)):
        if(index%2==0):
            x1 = 0*cm
            y1 = y1 - image_height - 0.3*cm 
            p.line(x1,y1-0.1*cm,document_width/2,y1-0.1*cm)
        else:
            x1 = document_width/2
            p.line(document_width/2,y1-0.1*cm,document_width,y1-0.1*cm)
        image = path+'/'+page_obj.object_list[index]['name_img']
        p.setFont("Helvetica-Bold", 8, leading=None)
        p.drawString(x1+3.5*cm,y1+2*cm,poll.name)
        p.setFont("Helvetica", 8, leading=None)
        p.drawString(x1+3.2*cm,y1+1.5*cm,"Scansiona il QR-Code oppure usa il link.")
        p.drawString(x1+3*cm,y1+1*cm,"Se ti viene chiesto, inserisci questo codice:")
        p.setFont("Helvetica-Bold", 8, leading=None)
        p.drawString(x1+3*cm,y1+0.5*cm,page_obj.object_list[index]['token'])
        p.drawString(x1+2.5*cm,y1+0.2,page_obj.object_list[index]['link'])
        p.drawImage(image, x=x1,y=y1,width=image_width,height=image_height)
    p.line(document_width/2, document_height,document_width/2, y1)


    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    #buffer.seek(0)
    #return FileResponse(buffer, as_attachment=True, filename='hello.pdf')
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename"hello.pdf"'
    response.write(pdf)
    return response