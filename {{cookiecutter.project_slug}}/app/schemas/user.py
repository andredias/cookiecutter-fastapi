from datetime import date
from string import ascii_letters
from typing import Optional

from pydantic import BaseModel, validator

from .utils import remove_symbols


def valida_cep(value: str) -> str:  # noqa: N805
    cep = remove_symbols(value)
    if len(cep) != 8:
        raise ValueError(f'{cep} não é um CEP válido')
    return cep


def valida_uf(value: str) -> str:  # noqa: N805
    if len(value) != 2 or any(True for v in value if v not in ascii_letters):
        raise ValueError(f'{value} não é um valor válido de UF')
    return value.upper()


def valida_cpf(value: str) -> str:  # noqa: N805
    cpf = remove_symbols(value)
    if len(cpf) != 11:
        raise ValueError('CPF deve ter 11 digitos')

    error_msg = f'{cpf} não é um valor válido de CPF'

    # validação de dígitos repetidos
    if cpf == (cpf[0] * 11):
        raise ValueError(error_msg)

    # valida primeiro dígito
    sum = 0
    for i in range(9):
        sum += int(cpf[i]) * (10 - i)
    remaining = (sum * 10) % 11
    if remaining == 10:
        remaining = 0
    if str(remaining) != cpf[-2]:
        raise ValueError(error_msg)

    # valida segundo dígito
    sum = 0
    for i in range(10):
        sum += int(cpf[i]) * (11 - i)
    remaining = (sum * 10) % 11
    if str(remaining) != cpf[-1]:
        raise ValueError(error_msg)

    return cpf


class Endereco(BaseModel):
    logradouro: str
    bairro: str
    cidade: str
    uf: str
    cep: str

    _uf = validator('uf', allow_reuse=True)(valida_uf)
    _cep = validator('cep', allow_reuse=True)(valida_cep)


class User(Endereco):
    cpf: str
    nome: str
    nascimento: date

    _cpf = validator('cpf', allow_reuse=True)(valida_cpf)


class UserIn(BaseModel):
    cpf: str
    nome: Optional[str]
    nascimento: Optional[date]
    logradouro: Optional[str]
    bairro: Optional[str]
    cidade: Optional[str]
    uf: Optional[str]
    cep: Optional[str]

    _uf = validator('uf', allow_reuse=True)(valida_uf)
    _cep = validator('cep', allow_reuse=True)(valida_cep)
    _cpf = validator('cpf', allow_reuse=True)(valida_cpf)
