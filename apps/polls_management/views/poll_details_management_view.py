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
from io import BytesIO
from xhtml2pdf import pisa
from django.views import View
import os

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

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result,link_callback=link_callback)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

class ViewPDF(View):
    def get(self, request:HttpRequest, poll_id:int, page_number:int, *args, **kwargs):
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
        pdf = render_to_pdf('polls_management/print_qr_code.html', 
                            {'poll': poll, 'page_obj':page_obj, 'print':True})
        return pdf

#Automaticly downloads to PDF file
class DownloadPDF(View):
    def get(self, request:HttpRequest, poll_id:int, page_number:int, *args, **kwargs):
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
        pdf = render_to_pdf('polls_management/print_qr_code.html', 
                            {'poll': poll, 'page_obj':page_obj, 'print':True})
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f'{poll.name} tokens ({page_number})'
        content = "attachment; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response