from datetime import datetime, timedelta
import random
import pytz
import re

from easyAfip.wsbase import WSBASE
from easyAfip.utils.afip_ws_connector import AfipWSConnector
from easyAfip.utils.signer import Signer
from easyAfip.utils.xml_processor import XMLProcessor


class WSAA(WSBASE):
    """
        Clase encargada de interactuar con el servicio de autenticación de la AFIP WSAA.
        https://www.afip.gob.ar/ws/WSAA/WSAAmanualDev.pdf
    """

    BASE_TICKET_XML = '''<loginTicketRequest><header><uniqueId>UNIQUE_ID</uniqueId><generationTime>YYYY-mm-ddTHH:mm:ss</generationTime><expirationTime>YYYY-mm-ddTHH:mm:ss</expirationTime></header><service>PUT_SERVICE_HERE</service></loginTicketRequest>'''
    BASE_TA_REQUEST = '''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsaa="http://wsaa.view.sua.dvadac.desein.afip.gov"><soapenv:Header/><soapenv:Body></soapenv:Body></soapenv:Envelope>'''

    def __init__(self, pem, key, service_to_auth, test_mode=None):
        super().__init__('wsaa', test_mode=test_mode)
        self.service_to_auth = service_to_auth
        self.pem = pem.encode('utf-8')
        self.key = key.encode('utf-8')

    
    def get_access_ticket(self) -> list:
        xml_ticket = self.get_pre_ticket_xml()
        xml_ticket_signed = self._sign_ticket(xml_ticket)
        cleaned_xml_ticket_signed = re.sub(r'-----BEGIN [^-]+-----|-----END [^-]+-----', '', xml_ticket_signed.decode('utf-8'))
        ws_wsaa_request = self.build_ta_request(cleaned_xml_ticket_signed)
        result = self.afip_ws_connector.execute_request(ws_wsaa_request, {"SOAPAction": "urn:LoginCms"})
        passport = self.extract_ta(result)
        return passport

    def get_pre_ticket_xml(self):
        xml_processor = XMLProcessor(self.BASE_TICKET_XML)
        generation_time, expiration_time = self._get_ticket_dates()
        unique_id = self._generate_unique_id()
        xml_processor.add_text_to_child('.//uniqueId', str(unique_id))
        xml_processor.add_text_to_child('.//generationTime', generation_time)
        xml_processor.add_text_to_child('.//expirationTime', expiration_time)
        xml_processor.add_text_to_child('service', self.service_to_auth)
        return xml_processor.get_decoded_xml()
    
    def build_ta_request(self, ticket: str) -> str:
        ta_rq_processor = XMLProcessor(self.BASE_TA_REQUEST, self.WS_NSMAP['wsaa'])
        ta_rq_processor.add_child("loginCms", tag_ns='wsaa', parent_element_path=".//soapenv:Body")
        ta_rq_processor.add_child("in0", tag_ns='wsaa', text=ticket, parent_element_path=".//wsaa:loginCms")
        return ta_rq_processor.get_xml()

    def extract_ta(self, response: str) -> dict:
        xml_processor = XMLProcessor(response, self.WS_NSMAP['wsaa'])
        logincms_content = xml_processor.get_child_text('.//ns:loginCmsReturn', namespaces=self.WS_NSMAP['wsaa'])
        logincms_content = XMLProcessor.escape_xml(logincms_content)
        logincms_content_processor = XMLProcessor(logincms_content, self.WS_NSMAP['wsaa'])
        token = logincms_content_processor.get_child_text('.//token')
        sign = logincms_content_processor.get_child_text('.//sign')
        return {'token': token, 'sign': sign}

    
    def _sign_ticket(self, ticket):
        signer = Signer(self.pem, self.key)
        return signer.sign_cms(ticket.encode('utf-8'))


    def _generate_unique_id(self):
        return random.randint(1, 2**32 - 1)


    def _get_ticket_dates(self):
        argentina_tz = pytz.timezone('America/Argentina/Buenos_Aires')
        actual_date = datetime.now(argentina_tz)
        fecha_plus_ten_minutes = actual_date + timedelta(minutes=10)
        
        # Formatear las fechas en el formato deseado
        date_format = "%Y-%m-%dT%H:%M:%S"
        date_from = actual_date.strftime(date_format)
        date_to = fecha_plus_ten_minutes.strftime(date_format)
        return [date_from, date_to]