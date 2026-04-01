import pytest
from dlp import PIIDetector

d = PIIDetector()

def types(text):
    return {v.type for v in d.scan(text)}

def test_dni_con_puntos():
    assert "ARGENTINE_DNI" in types("Mi DNI es 32.456.789")

def test_dni_sin_puntos():
    assert "ARGENTINE_DNI" in types("DNI 32456789")

def test_email():
    assert "EMAIL" in types("Escribime a juan@empresa.com")

def test_visa_valida():
    assert "CREDIT_CARD" in types("Tarjeta: 4532015112830366")

def test_luhn_invalida_rechazada():
    assert "CREDIT_CARD" not in types("Número: 4532015112830000")

def test_cuit():
    assert "CUIL_CUIT" in types("CUIT: 20-32456789-1")

def test_prompt_limpio():
    assert d.scan("Explicá el ciclo del agua.") == []

def test_multi_pii():
    found = types("Mail ana@test.com y DNI 30.123.456")
    assert "EMAIL" in found
    assert "ARGENTINE_DNI" in found