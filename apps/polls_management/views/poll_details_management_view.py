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
import pdfkit
import datetime
from django.template.loader import get_template
from io import BytesIO
from xhtml2pdf import pisa
from django.views import View





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
        host_link: str = request.get_host()
        query_links: List[str] = PollTokenService.available_token_list(host_link, poll)["query_list"]
        token_links: List[str] = PollTokenService.available_token_list(host_link, poll)["token_list"]
        qr_codes: List[str] = []
        for token, query in zip(token_links, query_links):
            img = qrcode.make(token, image_factory=PyPNGImage)
            name_img :str= str(poll_id) + str(query[1:])+'.png'
            qr_codes.append(name_img)
            img.save(f'static/qr_codes/{name_img}')
        # Render vote form (with eventual error message)
        print(qr_codes)
        paginator = Paginator(qr_codes, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        #path_wkthmltopdf = b'apps/polls_management/templates/polls_management/print_qr_code.html'
        #config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
        #pdfkit.from_file('apps/polls_management/templates/polls_management/print_qr_code.html', 'out.pdf', configuration=config)
        return render(request, 'polls_management/print_qr_code.html', 
                      {'poll': poll, 'qr_codes':qr_codes,
                       'page_obj':page_obj})
    else:
        return render(request, 'polls_management/print_qr_code.html', {'poll': poll })

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
data = {
             'today': datetime.date.today(), 
             'amount': 39.99,
            'customer_name': 'Cooper Mann',
            'order_id': 1233434,
        }
class ViewPDF(View):
    def get(self, request, *args, **kwargs):
        pdf = render_to_pdf('apps/polls_management/templates/polls_management/print_qr_code.html',data)
        return pdf
    


