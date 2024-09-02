
import logging
from typing import List

from easyAfip.utils.messages import FECompUltimoAutorizadoResponse, WSFEVException, FECompTotXRequestResponse, FECAEDetRequest, \
    FECAEDetResponse, FECAEResultEnum, FECAESolicitarResult, FEError
from easyAfip.wsbase import WSBASE
from easyAfip.utils.xml_processor import XMLProcessor


logger = logging.getLogger(__name__)


class WSFEV(WSBASE):
    """
        Clase encargada de integrar el servicio de facturacion electronica de la AFIP (WSFEv1).

        Para utilizar cualquiera de los métodos disponibles en el presente WS es necesario un Ticket de
        Acceso provisto por el WS de Autenticación y Autorización (WSAA).
        Recordar que para consumir el WS de Autenticación y Autorización WSAA es necesario obtener
        previamente un certificado digital desde clave fiscal y asociarlo al ws de negocio "Facturación
        Electrónica".
        Al momento de solicitar un Ticket de Acceso por medio del WS de Autenticación y Autorización
        WSAA tener en cuenta que debe enviar el tag service con el valor "wsfe" y que la duración del mismo es de 12 hs.
        Para más información deberá redirigirse a los manuales www.afip.gob.ar/ws.
    """

    BASE_REQUEST = '''<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:ar="http://ar.gov.afip.dif.FEV1/"><soap:Header/><soap:Body></soap:Body></soap:Envelope>'''

    def __init__(self, token, sign, cuit, test_mode=None):
        super().__init__('wsfev1', test_mode=test_mode)
        self.token = token
        self.sign = sign
        self.cuit = cuit
    

    @WSBASE.non_none_nor_zero
    def fecompultimoautorizado(self, pto_vta, ct_tipo) -> FECompUltimoAutorizadoResponse:
        """
        Get the last authorized invoice number
        Afip's doc: Retorna el ultimo comprobante autorizado para el tipo de comprobante / cuit / punto de venta
        ingresado / Tipo de Emisión
        :param pto_vta: El punto de venta a consultar
        :param ct_tipo: El tipo de comprobante a consultar
        :return:
        """
        auth_xml_processor = self.build_base_request('FECompUltimoAutorizado')
        auth_xml_processor.add_child('PtoVta', tag_ns='ar', text= str(pto_vta), parent_element_path='ar:FECompUltimoAutorizado')
        auth_xml_processor.add_child('CbteTipo', tag_ns='ar', text= str(ct_tipo), parent_element_path='ar:FECompUltimoAutorizado')
        response_xml_processor = self.execute_request_and_check_response(auth_xml_processor, 'FECompUltimoAutorizado')
        pto_vta_rs = response_xml_processor.get_child_text('.//ar:PtoVta')
        ct_tipo_rs = response_xml_processor.get_child_text('.//ar:CbteTipo')
        nro_cbte = response_xml_processor.get_child_text('.//ar:CbteNro')
        response = FECompUltimoAutorizadoResponse(pto_vta_rs, ct_tipo_rs, nro_cbte)
        return response

    def fecomptotxrequest(self) -> FECompTotXRequestResponse:
        """
        gets the maximum number of invoices that can be included in a request to the method fecomptotxrequest
        Afip's doc: Retorna la cantidad máxima de registros que se podrá incluir en un request al método
        FECAESolicitar / FECAEARegInformativo.
        :return:
        """
        fecomptotxrequest = self.build_base_request('FECompTotXRequest')
        response_xml_processor = self.execute_request_and_check_response(fecomptotxrequest, 'FECompTotXRequest')
        reg_x_req = response_xml_processor.get_child_text('.//ar:RegXReq')
        response = FECompTotXRequestResponse(reg_x_req)
        return response


    def fecaesolicitar(self, pto_vta, ct_tipo, invoices: List[FECAEDetRequest]) -> None:
        """
        Send the request for create the given invoices for the given point of sale and invoice type
        Afip's doc: El cliente envía la información del comprobante/lote que desea autorizar mediante un requerimiento
        el cual es atendido por WSFEv1 pudiendo producirse las siguientes situaciones:
             Supere todas las validaciones, el comprobante es aprobado, se asigna el CAE y su
                respectiva fecha de vencimiento,
             No supera alguna de las validaciones no excluyentes, el comprobante es aprobado con
                observaciones, se le asigna el CAE con la fecha de vencimiento,
             No supere alguna de las validaciones excluyentes, el comprobante no es aprobado y la
                solicitud es rechazada.
        :param invoices: The invoices to create
        :param pto_vta: The point of sale to create the invoices
        :param ct_tipo: The invoice type
        :return:
        """
        fecomptotxrequest = self.build_base_request('FECAESolicitar')
        fecomptotxrequest.add_child('FeCAEReq', tag_ns='ar', parent_element_path='ar:FECAESolicitar')
        fecomptotxrequest.add_child('FeCabReq', tag_ns='ar', parent_element_path='.//ar:FeCAEReq')
        fecomptotxrequest.add_child('PtoVta', tag_ns='ar', text=str(pto_vta), parent_element_path='.//ar:FeCabReq')
        fecomptotxrequest.add_child('CbteTipo', tag_ns='ar', text=str(ct_tipo), parent_element_path='.//ar:FeCabReq')
        fecomptotxrequest.add_child('CantReg', tag_ns='ar', text=str(len(invoices)), parent_element_path='.//ar:FeCabReq')
        fecomptotxrequest.add_child('FeDetReq', tag_ns='ar', parent_element_path='.//ar:FeCAEReq')

        last_comp_rs = self.fecompultimoautorizado(pto_vta, ct_tipo)
        last_nro_cbte = last_comp_rs.nro_cbte

        for index, invoice in enumerate(invoices):
            if not invoice.cbte_desde:
                last_cbte = str(int(last_nro_cbte) + (index + 1))
                invoice.cbte_desde = last_cbte
                invoice.cbte_hasta = last_cbte
            new_node_xml_porcessor = XMLProcessor(namespaces=self.WS_NSMAP['wsfev1'])
            new_node_xml_porcessor.create_root(tag_name= 'FECAEDetRequest', tag_ns='ar')
            new_node_xml_porcessor.add_child('Concepto', tag_ns='ar', text=invoice.concepto)
            new_node_xml_porcessor.add_child('DocTipo', tag_ns='ar', text=invoice.doc_tipo)
            new_node_xml_porcessor.add_child('CbteDesde', tag_ns='ar', text=invoice.cbte_desde)
            new_node_xml_porcessor.add_child('CbteHasta', tag_ns='ar', text=invoice.cbte_hasta)
            new_node_xml_porcessor.add_child('CbteFch', tag_ns='ar', text=invoice.cbte_fch)
            new_node_xml_porcessor.add_child('ImpTotal', tag_ns='ar', text=invoice.imp_total)
            new_node_xml_porcessor.add_child('ImpTotConc', tag_ns='ar', text=invoice.imp_tot_conc)
            new_node_xml_porcessor.add_child('ImpNeto', tag_ns='ar', text=invoice.imp_neto)
            new_node_xml_porcessor.add_child('ImpOpEx', tag_ns='ar', text=invoice.imp_op_ex)
            new_node_xml_porcessor.add_child('ImpIVA', tag_ns='ar', text=invoice.imp_iva)
            new_node_xml_porcessor.add_child('FchServDesde', tag_ns='ar', text=invoice.fch_serv_desde)
            new_node_xml_porcessor.add_child('FchServHasta', tag_ns='ar', text=invoice.fch_serv_hasta)
            new_node_xml_porcessor.add_child('FchVtoPago', tag_ns='ar', text=invoice.fch_vto_pago)
            new_node_xml_porcessor.add_child('MonId', tag_ns='ar', text=invoice.mon_id)
            new_node_xml_porcessor.add_child('MonCotiz', tag_ns='ar', text=invoice.mon_cotiz)
            # optionals
            if invoice.imp_trib:
                new_node_xml_porcessor.add_child('ImpTrib', tag_ns='ar', text=invoice.imp_trib)
            if invoice.doc_nro:
                new_node_xml_porcessor.add_child('DocNro', tag_ns='ar', text=invoice.doc_nro)
            if invoice.tributos:
                new_node_xml_porcessor.add_child('Tributos', tag_ns='ar')
                for tributo in invoice.tributos:
                    new_node_xml_porcessor.add_child('Id', tag_ns='ar', text=tributo.id,parent_element_path='.//ar:Tributos')
                    new_node_xml_porcessor.add_child('Desc', tag_ns='ar', text=tributo.desc,parent_element_path='.//ar:Tributos')
                    new_node_xml_porcessor.add_child('BaseImp', tag_ns='ar', text=tributo.base_imp,parent_element_path='.//ar:Tributos')
                    new_node_xml_porcessor.add_child('Alic', tag_ns='ar', text=tributo.alic,parent_element_path='.//ar:Tributos')
                    new_node_xml_porcessor.add_child('Importe', tag_ns='ar', text=tributo.importe,parent_element_path='.//ar:Tributos')
            if invoice.cbtes_asoc:
                fecomptotxrequest.add_child('CbtesAsoc', tag_ns='ar')
                for cbte_asoc in invoice.cbtes_asoc:
                    new_node_xml_porcessor.add_child('CbteAsoc', tag_ns='ar', parent_element_path='.//ar:CbtesAsoc')
                    new_node_xml_porcessor.add_child('Tipo', tag_ns='ar', text=cbte_asoc.tipo,parent_element_path='.//ar:CbteAsoc')
                    new_node_xml_porcessor.add_child('PtoVta', tag_ns='ar', text=cbte_asoc.pto_vta,parent_element_path='.//ar:CbteAsoc')
                    new_node_xml_porcessor.add_child('Nro', tag_ns='ar', text=cbte_asoc.nro,parent_element_path='.//ar:CbteAsoc')
            fecomptotxrequest.add_child_from_xml(new_node_xml_porcessor.get_xml(), parent_element_path='.//ar:FeDetReq')
        
        response_xml_processor = self.execute_request_and_check_response(fecomptotxrequest, 'FECAESolicitar')
        errors = self.exctract_errors(response_xml_processor)

        fecaesolicitarresult = FECAESolicitarResult()
        fecaesolicitarresult.errors = errors

        if response_xml_processor.has_child('.//ar:FeCabResp'):
            fecaesolicitarresult.cuit = response_xml_processor.get_child_text('.//ar:Cuit', parent_node='.//ar:FeCabResp')
            fecaesolicitarresult.pto_vta = int(response_xml_processor.get_child_text('.//ar:PtoVta', parent_node='.//ar:FeCabResp'))
            fecaesolicitarresult.cbte_tipo = int(response_xml_processor.get_child_text('.//ar:CbteTipo', parent_node='.//ar:FeCabResp'))
            fecaesolicitarresult.fecha_proceso = response_xml_processor.get_child_text('.//ar:FchProceso', parent_node='.//ar:FeCabResp')
            fecaesolicitarresult.cant_reg = int(response_xml_processor.get_child_text('.//ar:CantReg', parent_node='.//ar:FeCabResp'))
            fecaesolicitarresult.resultado = FECAEResultEnum.get_by_value(
                response_xml_processor.get_child_text('.//ar:Resultado', parent_node='.//ar:FeCabResp'))
            fecaesolicitarresult.reproceso = response_xml_processor.get_child_text('.//ar:Reproceso', parent_node='.//ar:FeCabResp')

            children_nmr = response_xml_processor.get_children_count('.//ar:FECAEDetResponse')

            for child in range(children_nmr):
                child_xml_processor = response_xml_processor.get_child_xml_processor_by_group_index('.//ar:FECAEDetResponse', child)
                fecaedetresponse = FECAEDetResponse(
                    int(child_xml_processor.get_child_text('.//ar:Concepto')),
                    int(child_xml_processor.get_child_text('.//ar:DocTipo')),
                    child_xml_processor.get_child_text('.//ar:DocNro'),
                    int(child_xml_processor.get_child_text('.//ar:CbteDesde')),
                    int(child_xml_processor.get_child_text('.//ar:CbteHasta')),
                    child_xml_processor.get_child_text('.//ar:CbteFch'),
                    FECAEResultEnum.get_by_value(child_xml_processor.get_child_text('.//ar:Resultado')))
                fecaedetresponse.obs_l = self.exctract_obs(child_xml_processor)
                fecaesolicitarresult.details.append(fecaedetresponse)
        return fecaesolicitarresult


    def execute_request_and_check_response(self, xml_repr: XMLProcessor, method_name: str) -> XMLProcessor:
        """
        This method will execute the request to AFIP WS and check the response
        :param xml_repr: XMLProcessor object with the request to AFIP WS
        :param method_name: The name of the method to execute
        :return: XMLProcessor object with the response from AFIP WS
        """
        logger.info('Request to AFIP WS: %s', xml_repr.get_xml())
        result = self.afip_ws_connector.execute_request(xml_repr.get_xml(), {"SOAPAction": f'http://ar.gov.afip.dif.FEV1/{method_name}'})
        logger.info('Response from AFIP WS: %s', result)
        auth_response_xml_processor = XMLProcessor(result, self.WS_NSMAP['wsfev1'])
        # self.check_response(auth_response_xml_processor)
        return auth_response_xml_processor


    def build_base_request(self, method_name: str) -> XMLProcessor:
        """
        Build the base request with the main node for the required method and the auth node
        :param method_name: The name of the method to execute
        :return: XMLProcessor object with the base request
        """
        auth_xml_processor = XMLProcessor(self.BASE_REQUEST, namespaces=self.WS_NSMAP['wsfev1'])
        auth_xml_processor.add_child(method_name, tag_ns='ar')
        auth_node = super().get_auth_node(self.cuit, self.token, self.sign)
        auth_xml_processor.add_child_from_xml(auth_node, parent_element_path=f'ar:{method_name}')
        return auth_xml_processor
    

# TODO eliminar esto y crear una clase que lo represente, y cuando ocurra un error, inicializar dicha clase y retornar los errores del servicio.
    def check_response(self, xml_repr_rs: XMLProcessor) -> None:
        """
        This method will check the response from AFIP WS and raise an exception if the response is an error
        :param xml_repr_rs: XMLProcessor object with the response from AFIP WS
        :return:
        """
        errors = xml_repr_rs.get_errors_content('.//ar:Errors')
        if errors:
            # agregar codigo de error
            logger.error('Error Response from AFIP WS: %s', errors)
            raise WSFEVException(f"There are errors in the process.", errors)

    def exctract_errors(self, xml_repr_rs: XMLProcessor) -> list:
        """
        This method will check the response from AFIP WS and raise an exception if the response is an error
        :param xml_repr_rs: XMLProcessor object with the response from AFIP WS
        :return:
        """
        errors = xml_repr_rs.get_errors_content('.//ar:Errors')
        errors_list = []
        for error in errors:
            feerror = FEError(error[0], error[1])
            errors_list.append(feerror)
        return errors_list
    
    def exctract_obs(self, xml_repr_rs: XMLProcessor) -> list:
        """
        This method will check the response from AFIP WS and raise an exception if the response is an error
        :param xml_repr_rs: XMLProcessor object with the response from AFIP WS
        :return:
        """
        obs_l = xml_repr_rs.get_obs_content('.//ar:Observaciones')
        if not obs_l:
            return []
        obs_error_list = []
        for obs in obs_l:
            obs_error = FEError(obs[0], obs[1])
            obs_error_list.append(obs_error)
        return obs_error_list
