# easeAfip

A simple to use lib to connect with hard to use AFIP Soap WS

This is a simple python package useful to easily connect with AFIP service without to pain og develop SOAP WS integrations. Just import the lib and start to code and consume the AFIP web services.

Its important to have a brief idea of AFIP service requests bodies at least. In the AFIP website you can find up-to-date docs useful to understand messages structure and responses.

- [Servicio de generacion de Tickets de acceso WSAA](https://www.afip.gob.ar/ws/WSAA/WSAAmanualDev.pdf)
- [Facturacion electronica WSFEV1](https://www.afip.gob.ar/ws/WSFEV1/documentos/manual-desarrollador-COMPG-v3-4-2.pdf)

For now, only WSAA works at 100% and WSFEV1 works only for type C invoices (solo and batch).

