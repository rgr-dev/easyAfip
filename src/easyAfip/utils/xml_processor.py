from typing import TypeVar

from lxml import etree
import logging
import re

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='XMLProcessor')

class XMLProcessor:
    """
    Clase encargada de procesar y manipular documentos XML.
    """

    def __init__(self, xml: str = None, namespaces: dict = {}):
        if xml:
            self.xml = XMLProcessor.escape_xml(xml)
            self.root = etree.fromstring(self.xml)
        self.namespaces = namespaces

    def create_root(self, tag_name: str, tag_ns=None, namespaces: dict ={}):
        self.namespaces = {**self.namespaces, **namespaces}
        element_tag_name = self._build_tag(tag_name, tag_ns)
        self.root = etree.Element(element_tag_name, nsmap=self.namespaces)
    
    def create_root_from_xml(self, xml: str, namespaces: dict =None):
        self.xml = XMLProcessor.escape_xml(xml)
        self.root = self.create_element_from_xml(xml, namespaces)
        self.namespaces = namespaces
    
    def create_element_from_xml(self, xml: str, namespaces: dict =None):
        return etree.fromstring(XMLProcessor.escape_xml(xml))
    
    def add_text_to_child(self, child_xpath, text):
        child_node = self.root.find(child_xpath, namespaces=self.namespaces)
        child_node.text = text
    
    def add_child_from_xml(self, xml: str, parent_element_path=None) -> None:
        """
        Add a new element child to the parent element based on the given xml string.
        Takes the xml string and parse it to a new Element object and append it to the parent element.
        :param xml: xml string to be parsed to an Element object
        :param parent_element_path: xpath of the parent element where the new element will be appended
        :return:
        """
        new_element = self.create_element_from_xml(xml)
        if parent_element_path:
            parent_element = self.root.find(parent_element_path, namespaces=self.namespaces)
            parent_element.append(new_element)
        else:
            self.root.append(new_element)
    
    def add_child(self, child_name, text=None, tag_ns=None, parent_element_path=None):
        tag_name = self._build_tag(child_name, tag_ns)
        new_element = etree.Element(tag_name, nsmap=self.namespaces)
        if text:
            new_element.text = text
        if parent_element_path:
            parent_element = self.root.find(parent_element_path, namespaces=self.namespaces)
            parent_element.append(new_element)
        else:
            self.root.append(new_element)
    
    def has_child(self, child_name, parent_node=None) -> bool:
        parent_el = self.root.find(parent_node, namespaces=self.namespaces) if parent_node else self.root
        return parent_el.find(child_name, namespaces=self.namespaces) is not None
    
    def get_child_text(self, child_name_path, namespaces={}, parent_node=None) -> str:
        parent_el = self.root.find(parent_node, namespaces=self.namespaces) if parent_node else self.root
        results = [el for el in parent_el.iterfind(child_name_path, namespaces={**self.namespaces, **namespaces})]
        return results[0].text if results else None
    
    def get_children_text(self, child_name_path, namespaces={}, parent_node=None) -> list:
        parent_el = parent_node if parent_node else self.root
        return [ child.text for child in [el for el in parent_el.iterfind(child_name_path, namespaces={**self.namespaces, **namespaces})]]

    def get_children_count(self, children_name_path, namespaces={}) -> int:
        return len([el for el in self.root.iterfind(children_name_path, namespaces={**self.namespaces, **namespaces})])

    def get_child_xml_processor_by_group_index(self, children_name_path, child_index=0, namespaces={}) -> T:
        children = [el for el in self.root.iterfind(children_name_path, namespaces={**self.namespaces, **namespaces})]
        xml = etree.tostring(children[child_index], xml_declaration=True, encoding='UTF-8')
        return XMLProcessor(xml.decode(), namespaces=self.namespaces)

    def get_errors_content(self, error_node_path, namespaces={}) -> list:
        parent_element = self.root.find(error_node_path, namespaces=self.namespaces)
        if not parent_element:
            return []
        return [(int(err.find('.//ar:Code', namespaces=self.namespaces).text), err.find('.//ar:Msg', namespaces=self.namespaces).text) for err in parent_element.findall('.//ar:Err', namespaces=self.namespaces)]

    def get_obs_content(self, obs_node_path, namespaces={}) -> list:
        parent_element = self.root.find(obs_node_path, namespaces=self.namespaces)
        if not parent_element:
            return []
        return [(int(err.find('.//ar:Code', namespaces=self.namespaces).text), err.find('.//ar:Msg', namespaces=self.namespaces).text) for err in parent_element.findall('.//ar:Obs', namespaces=self.namespaces)]

    def get_decoded_xml(self) -> str:
        return self._prettyprint()
    
    def get_xml(self) -> str:
        return self._prettyprint(xml_declaration=True, encoding='UTF-8')
    
    def _prettyprint(self, **kwargs) -> str:
        xml = etree.tostring(self.root, **kwargs)
        logger.info(xml)
        return xml.decode()

    def _build_tag(self, tag_name, tag_ns=None):
        return f"{{{self.namespaces[tag_ns]}}}{tag_name}" if tag_ns else tag_name

    @staticmethod
    def escape_xml(xml:str) -> str:
        # first_escape = xml.text.replace('''<?xml version="1.0" encoding="UTF-8"?>''', "")
        # return xml.text.replace('''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>''', "")
        return re.sub(r'<\?.*?\?>', '', xml, flags=re.DOTALL)