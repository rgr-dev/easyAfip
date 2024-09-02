
from functools import wraps
from xml.etree.ElementTree import Element
from easyAfip.utils.xml_processor import XMLProcessor
from easyAfip.utils.afip_ws_connector import AfipWSConnector


class WSBASE:
    """
    Clase encargada de actuar como base para las clases que interactúan con los servicios de la AFIP.
    """

    ENDPOINTS = {
        'wsaa': {
            'homo': '''https://wsaahomo.afip.gov.ar/ws/services/LoginCms''',
            'prod': '''https://wsaa.afip.gov.ar/ws/services/LoginCms'''
        },
        'wsfev1': {
            'homo': '''https://wswhomo.afip.gov.ar/wsfev1/service.asmx''',
            'prod': '''https://servicios1.afip.gov.ar/wsfev1/service.asmx'''
        }
    }

    WS_NSMAP = {
    'wsaa': {
        'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
        'ns': 'http://wsaa.view.sua.dvadac.desein.afip.gov',
        'wsaa': 'http://wsaa.view.sua.dvadac.desein.afip.gov'
    },
    'wsfev1': {
        'soapenv': 'http://www.w3.org/2003/05/soap-envelope',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsd': 'http://www.w3.org/2001/XMLSchema-instance',
        'ar': 'http://ar.gov.afip.dif.FEV1/'
    }
    }

    def __init__(self, service, test_mode=None) -> None:
        self.ws_endpoint = self.ENDPOINTS[service]['homo'] if test_mode else self.ENDPOINTS[service]['prod']
        self.afip_ws_connector = AfipWSConnector(self.ws_endpoint)
        self.service = service


    def get_auth_node(self, cuit: str, token: str, sign: str) -> str:
        auth_xml_processor = XMLProcessor()
        auth_xml_processor.create_root('Auth', tag_ns='ar', namespaces=self.WS_NSMAP['wsfev1'])
        auth_xml_processor.add_child('Token', tag_ns='ar', text= token)
        auth_xml_processor.add_child('Sign', tag_ns='ar', text= sign)
        auth_xml_processor.add_child('Cuit', tag_ns='ar', text=cuit)
        return auth_xml_processor.get_xml()
    

    def non_none_nor_zero(funcion):
        @wraps(funcion)
        def wrapper(*args, **kwargs):
            # Verificar los parámetros posicionales (args)
            for index, arg in enumerate(args):
                assert arg is not None and arg != 0, f"The argument in position {index} cannot be neither None nor cero"

            # Verificar los parámetros nombrados (kwargs)
            for key, value in kwargs.items():
                assert value is not None and value != 0, f"The arg '{key}' cannot be neither None nor cero"

            # Si todo es válido, ejecutar la función original
            return funcion(*args, **kwargs)
        
        return wrapper