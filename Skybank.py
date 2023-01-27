import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
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
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


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
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\nVocê não possui saldo o suficiente para esta transação.")

        elif valor > 0:
            self._saldo -= valor
            print("\nSaque Realizado! \nTransação concluída!")
            return True

        else:
            print("\nOperação falhou! \nValor inserido é inválido.")

        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\nDepósito Realizado! \nTransação concluída!")

        else:
            print("\nOperação falhou! \nValor inserido é inválido.")
            return False

        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):

        numero_saques = len([transacao for transacao in self.historico.transacoes if
                             transacao["tipo_de_transacao"]] == Saque.__name__)  # poderia ser == "Saque"
        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques >= self.limite_saques

        if excedeu_limite:
            print("\n Operação falhou! \nO valor do saque excede o limite da sua conta.")

        elif excedeu_saques:
            print("\n Operação falhou! \nO número máximo de saques excedido.")

        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        return f""" Agência :\t{self.agencia}
                    ContaCorrente:\t\t{self.numero}
                    Titular:\t{self.cliente}"""


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo_de_transacao": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d/%m/%Y--------%H:%M:%s"),
            }
        )


class Transacao(ABC):

    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(cls, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self.valor = valor

    @property
    def valor(self):
        return self.valor()

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self.valor = valor

    @property
    def valor(self):
        return self.valor()

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


def depositar(clientes):
    cpf = input("\nInforme o cpf do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\nCliente não encontrado.")
        return

    valor = float(input("\nInforme o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def sacar(clientes):
    cpf = input("\nInforme o cpf do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\nCliente não encontrado.")
        return

    valor = float(input("\nInforme o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)
    # FIXME: sacar e depositar estão iguais, fazer uma diferenciação de string entre saque ou deposito para reuso de código e ficar mais limpo.


def exibir_extrato(clientes):
    cpf = input("\nInforme o cpf do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\nCliente não encontrado.")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n============================== EXTRATO ==============================")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "\nNão foram realizadas transações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo_de_transacao']}:\n\tR${transacao['valor']:.2f}"

    print(extrato)
    print(f"\nSaldo:\n\tR${conta.saldo:.2f}")
    print("\n=====================================================================")


def criar_cliente(clientes):
    cpf = input("Informe o CPF (digite somente números): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\nERROR\nJá existe um cliente com esse CPF! ")
        return

    nome = input("\nInforme seu nome completo: ")
    data_nascimento = input("\nInforme a data de nascimento (dd/mm/aaaa): ")
    endereco = input("\nInforme o endereco (logradouro, numero - bairro - cidade/sigla do estado): ")
    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)

    clientes.append(cliente)

    print("\nCliente Cadastrado no banco com sucesso!")
    # se fosse uma pessoa juridica, usaria um cnpj, etc


def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o cpf do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    #FIXME: criar um filtro para contas, 1 cliente nao pode ter mais do que 1 conta corrente, etc

    if not cliente:
        print("\nCliente não encontrado, encerrado processo de criação de conta...")
        return
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)
    print("\nConta criada com sucesso.")


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\nCliente não possui contas.")
        return
    # FIXME: não permite o cliente escolher a conta que procura
    return cliente.contas[0]


def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))


def menu():
    menu = """\n
    =-=-=-=-=-=-=-=-=-=-=-=-=-= SKYBANK =-=-=-=-=-=-=-=-=-=-=-=-=-=
    1.\t Depositar
    2.\t Sacar
    3.\t Extrato
    4.\t Novo Usuário (é necessário ser um usuário do banco para poder ter uma conta)
    5.\t Nova Conta (é necessário ter uma conta para fazer depósitos e pagamentos)
    6.\t Listar Contas 
    7.\t Sair
    =>insira a opção: 
    """
    return int(input(textwrap.dedent(menu)))


def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == 1:
            depositar(clientes)

        elif opcao == 2:
            sacar(clientes)

        elif opcao == 3:
            exibir_extrato(clientes)

        elif opcao == 4:
            criar_cliente(clientes)

        elif opcao == 5:
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == 6:
            listar_contas(contas)

        elif opcao == 7:
            print("Encerrando programa do banco skybank...\n Aguarde...\nFechado com êxito, volte sempre!!")
            break

        else:
            print("Operação inválida, por favor selecione novamente a operação desejada.")


main()
