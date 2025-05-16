from abc import ABC, abstractmethod
from datetime import datetime

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, cpf, data_nascimento, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        if valor <= 0 or valor > self._saldo:
            print("@@@ Operação inválida! @@@")
            return False
        self._saldo -= valor
        print("\n=== Saque realizado com sucesso! ===")
        return True

    def depositar(self, valor):
        if valor <= 0:
            print("@@@ Valor inválido para depósito! @@@")
            return False
        self._saldo += valor
        print("\n=== Depósito realizado com sucesso! ===")
        return True

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques
        self._saques_realizados = 0

    def sacar(self, valor):
        if self._saques_realizados >= self._limite_saques:
            print("@@@ Limite de saques atingido. @@@")
            return False
        if valor > self._limite:
            print("@@@ Valor excede o limite de saque. @@@")
            return False
        if super().sacar(valor):
            self._saques_realizados += 1
            return True
        return False

class Historico:
    def __init__(self):
        self.transacoes = []

    def adicionar_transacao(self, transacao):
        self.transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        })

    def gerar_relatorio(self, tipo_transacao=None):
        if tipo_transacao:
            return [t for t in self.transacoes if t['tipo'].lower() == tipo_transacao.lower()]
        return self.transacoes

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.sacar(self._valor):
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.depositar(self._valor):
            conta.historico.adicionar_transacao(self)

class ContasIterador:
    def __init__(self, contas):
        self.contas = contas
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self.contas):
            raise StopIteration
        conta = self.contas[self._index]
        self._index += 1
        return f"""
        Agência:	{conta.agencia}
        Número:		{conta.numero}
        Titular:	{conta.cliente.nome}
        Saldo:		R$ {conta.saldo:.2f}
"""

def validar_cpf(cpf):
    return cpf.isdigit() and len(cpf) == 11

def filtrar_cliente(cpf, clientes):
    return next((cliente for cliente in clientes if cliente.cpf == cpf), None)

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return None
    print("\n=== Contas do cliente ===")
    for i, conta in enumerate(cliente.contas, 1):
        print(f"[{i}] Agência: {conta.agencia} | Número: {conta.numero}")
    try:
        escolha = int(input("Escolha a conta pelo número: ")) - 1
        return cliente.contas[escolha]
    except (ValueError, IndexError):
        print("\n@@@ Opção inválida! @@@")
        return None

def menu():
    opcoes = """
[d]	Depositar
[s]	Sacar
[e]	Extrato
[nc]	Nova conta
[lc]	Listar contas
[nu]	Novo usuário
[r]	Relatório de transações
[q]	Sair
=> """
    return input(opcoes)

def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            cpf = input("Informe o CPF do cliente: ")
            cliente = filtrar_cliente(cpf, clientes)
            if not cliente:
                print("\n@@@ Cliente não encontrado! @@@")
                continue
            conta = recuperar_conta_cliente(cliente)
            if not conta:
                continue
            valor = float(input("Informe o valor do depósito: "))
            transacao = Deposito(valor)
            cliente.realizar_transacao(conta, transacao)

        elif opcao == "s":
            cpf = input("Informe o CPF do cliente: ")
            cliente = filtrar_cliente(cpf, clientes)
            if not cliente:
                print("\n@@@ Cliente não encontrado! @@@")
                continue
            conta = recuperar_conta_cliente(cliente)
            if not conta:
                continue
            valor = float(input("Informe o valor do saque: "))
            transacao = Saque(valor)
            cliente.realizar_transacao(conta, transacao)

        elif opcao == "e":
            cpf = input("Informe o CPF do cliente: ")
            cliente = filtrar_cliente(cpf, clientes)
            if not cliente:
                print("\n@@@ Cliente não encontrado! @@@")
                continue
            conta = recuperar_conta_cliente(cliente)
            if not conta:
                continue
            print("\n================ EXTRATO ================")
            transacoes = conta.historico.transacoes
            if not transacoes:
                print("Não foram realizadas movimentações.")
            else:
                for t in transacoes:
                    print(f"{t['data']} - {t['tipo']}: R$ {t['valor']:.2f}")
            print(f"\nSaldo:	R$ {conta.saldo:.2f}")
            print("========================================")

        elif opcao == "nu":
            cpf = input("Informe o CPF (somente número): ")
            if not validar_cpf(cpf):
                print("\n@@@ CPF inválido! @@@")
                continue
            if filtrar_cliente(cpf, clientes):
                print("\n@@@ Já existe cliente com esse CPF! @@@")
                continue
            nome = input("Informe o nome completo: ")
            data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
            endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")
            cliente = PessoaFisica(nome, cpf, data_nascimento, endereco)
            clientes.append(cliente)
            print("\n=== Cliente criado com sucesso! ===")

        elif opcao == "nc":
            cpf = input("Informe o CPF do cliente: ")
            cliente = filtrar_cliente(cpf, clientes)
            if not cliente:
                print("\n@@@ Cliente não encontrado! @@@")
                continue
            numero = len(contas) + 1
            conta = ContaCorrente.nova_conta(cliente, numero)
            cliente.adicionar_conta(conta)
            contas.append(conta)
            print("\n=== Conta criada com sucesso! ===")

        elif opcao == "lc":
            for conta in ContasIterador(contas):
                print(conta)

        elif opcao == "r":
            cpf = input("Informe o CPF do cliente: ")
            cliente = filtrar_cliente(cpf, clientes)
            if not cliente:
                print("\n@@@ Cliente não encontrado! @@@")
                continue
            conta = recuperar_conta_cliente(cliente)
            if not conta:
                continue
            tipo = input("Filtrar por tipo de transação (Saque/Deposito) ou Enter para todas: ")
            print("\n======= RELATÓRIO DE TRANSAÇÕES =======")
            for transacao in conta.historico.gerar_relatorio(tipo_transacao=tipo or None):
                print(f"{transacao['data']} - {transacao['tipo']}: R$ {transacao['valor']:.2f}")
            print("=======================================")

        elif opcao == "q":
            break

        else:
            print("\n@@@ Operação inválida, selecione novamente. @@@")

if __name__ == "__main__":
    main()