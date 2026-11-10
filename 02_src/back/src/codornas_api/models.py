from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class IdMixin:
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class Codorna(IdMixin, Base):
    __tablename__ = "codornas"

    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    sexo: Mapped[str | None] = mapped_column(String(20))
    data_nascimento: Mapped[date | None] = mapped_column(Date)
    peso_atual: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="ativa")
    raca_id: Mapped[int | None] = mapped_column(ForeignKey("racas.id", ondelete="RESTRICT"))
    lote_id: Mapped[int | None] = mapped_column(ForeignKey("lotes.id", ondelete="SET NULL"))
    gaiola_id: Mapped[int | None] = mapped_column(ForeignKey("gaiolas.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    raca: Mapped[Raca | None] = relationship(back_populates="codornas")
    lote: Mapped[Lote | None] = relationship(back_populates="codornas")
    gaiola: Mapped[Gaiola | None] = relationship(back_populates="codornas")
    pesagens: Mapped[list[Pesagem]] = relationship(back_populates="codorna", cascade="all, delete-orphan", passive_deletes=True)
    mortalidades: Mapped[list[Mortalidade]] = relationship(back_populates="codorna", cascade="all, delete-orphan", passive_deletes=True)


class Raca(IdMixin, Base):
    __tablename__ = "racas"

    nome: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    origem: Mapped[str | None] = mapped_column(String(100))
    peso_medio: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))

    codornas: Mapped[list[Codorna]] = relationship(back_populates="raca")


class Lote(IdMixin, Base):
    __tablename__ = "lotes"

    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    data_criacao: Mapped[date] = mapped_column(Date, nullable=False)
    quantidade_inicial: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="ativo")
    raca_id: Mapped[int | None] = mapped_column(ForeignKey("racas.id", ondelete="SET NULL"))
    galpao_id: Mapped[int | None] = mapped_column(ForeignKey("galpoes.id", ondelete="SET NULL"))

    codornas: Mapped[list[Codorna]] = relationship(back_populates="lote")
    galpao: Mapped[Galpao | None] = relationship(back_populates="lotes")
    raca: Mapped[Raca | None] = relationship()


class Galpao(IdMixin, Base):
    __tablename__ = "galpoes"

    nome: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    localizacao: Mapped[str | None] = mapped_column(String(255))
    capacidade: Mapped[int | None] = mapped_column(Integer)

    lotes: Mapped[list[Lote]] = relationship(back_populates="galpao")
    gaiolas: Mapped[list[Gaiola]] = relationship(back_populates="galpao", cascade="all, delete-orphan", passive_deletes=True)


class Gaiola(IdMixin, Base):
    __tablename__ = "gaiolas"

    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    capacidade: Mapped[int] = mapped_column(Integer, nullable=False)
    galpao_id: Mapped[int] = mapped_column(ForeignKey("galpoes.id", ondelete="CASCADE"), nullable=False)
    lote_id: Mapped[int | None] = mapped_column(ForeignKey("lotes.id", ondelete="SET NULL"))

    galpao: Mapped[Galpao] = relationship(back_populates="gaiolas")
    lote: Mapped[Lote | None] = relationship()
    codornas: Mapped[list[Codorna]] = relationship(back_populates="gaiola")


class Alimento(IdMixin, Base):
    __tablename__ = "alimentos"

    nome: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    tipo: Mapped[str | None] = mapped_column(String(60))
    unidade: Mapped[str] = mapped_column(String(30), nullable=False, default="kg")
    proteina_percentual: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    estoque: Mapped[EstoqueAlimento | None] = relationship(back_populates="alimento", cascade="all, delete-orphan", passive_deletes=True, uselist=False)
    alimentacoes: Mapped[list[Alimentacao]] = relationship(back_populates="alimento")


class EstoqueAlimento(IdMixin, Base):
    __tablename__ = "estoque_alimentos"

    alimento_id: Mapped[int] = mapped_column(ForeignKey("alimentos.id", ondelete="CASCADE"), unique=True, nullable=False)
    quantidade: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False, default=0)
    quantidade_minima: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False, default=0)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    alimento: Mapped[Alimento] = relationship(back_populates="estoque")


class Alimentacao(IdMixin, Base):
    __tablename__ = "alimentacoes"

    data_hora: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    quantidade: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    unidade: Mapped[str] = mapped_column(String(30), nullable=False, default="kg")
    alimento_id: Mapped[int] = mapped_column(ForeignKey("alimentos.id", ondelete="RESTRICT"), nullable=False)
    codorna_id: Mapped[int | None] = mapped_column(ForeignKey("codornas.id", ondelete="CASCADE"))
    lote_id: Mapped[int | None] = mapped_column(ForeignKey("lotes.id", ondelete="CASCADE"))

    alimento: Mapped[Alimento] = relationship(back_populates="alimentacoes")
    codorna: Mapped[Codorna | None] = relationship()
    lote: Mapped[Lote | None] = relationship()


class Fornecedor(IdMixin, Base):
    __tablename__ = "fornecedores"

    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    documento: Mapped[str | None] = mapped_column(String(30), unique=True)
    email: Mapped[str | None] = mapped_column(String(255))
    telefone: Mapped[str | None] = mapped_column(String(40))
    endereco: Mapped[str | None] = mapped_column(String(255))

class Veterinario(IdMixin, Base):
    __tablename__ = "veterinarios"

    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    registro_profissional: Mapped[str | None] = mapped_column(String(60), unique=True)
    telefone: Mapped[str | None] = mapped_column(String(40))
    email: Mapped[str | None] = mapped_column(String(255))

class ConsultaVeterinaria(IdMixin, Base):
    __tablename__ = "consultas_veterinarias"

    data_consulta: Mapped[date] = mapped_column(Date, nullable=False)
    diagnostico: Mapped[str | None] = mapped_column(Text)
    tratamento: Mapped[str | None] = mapped_column(Text)
    custo: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    codorna_id: Mapped[int] = mapped_column(ForeignKey("codornas.id", ondelete="CASCADE"), nullable=False)
    veterinario_id: Mapped[int | None] = mapped_column(ForeignKey("veterinarios.id", ondelete="SET NULL"))

    codorna: Mapped[Codorna] = relationship()
    veterinario: Mapped[Veterinario | None] = relationship()


class Vacina(IdMixin, Base):
    __tablename__ = "vacinas"

    nome: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    dose: Mapped[str | None] = mapped_column(String(60))
    intervalo_dias: Mapped[int | None] = mapped_column(Integer)

class Vacinacao(IdMixin, Base):
    __tablename__ = "vacinacoes"

    data_aplicacao: Mapped[date] = mapped_column(Date, nullable=False)
    proxima_aplicacao: Mapped[date | None] = mapped_column(Date)
    codorna_id: Mapped[int] = mapped_column(ForeignKey("codornas.id", ondelete="CASCADE"), nullable=False)
    vacina_id: Mapped[int] = mapped_column(ForeignKey("vacinas.id", ondelete="RESTRICT"), nullable=False)
    veterinario_id: Mapped[int | None] = mapped_column(ForeignKey("veterinarios.id", ondelete="SET NULL"))

    codorna: Mapped[Codorna] = relationship()
    vacina: Mapped[Vacina] = relationship()
    veterinario: Mapped[Veterinario | None] = relationship()


class Reproducao(IdMixin, Base):
    __tablename__ = "reproducoes"

    data_acasalamento: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="planejada")
    observacoes: Mapped[str | None] = mapped_column(Text)
    macho_id: Mapped[int | None] = mapped_column(ForeignKey("codornas.id", ondelete="SET NULL"))
    femea_id: Mapped[int | None] = mapped_column(ForeignKey("codornas.id", ondelete="SET NULL"))

    macho: Mapped[Codorna | None] = relationship(foreign_keys=[macho_id])
    femea: Mapped[Codorna | None] = relationship(foreign_keys=[femea_id])


class Incubacao(IdMixin, Base):
    __tablename__ = "incubacoes"

    data_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    data_prevista_eclosao: Mapped[date | None] = mapped_column(Date)
    quantidade_ovos: Mapped[int] = mapped_column(Integer, nullable=False)
    temperatura: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    umidade: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="em_andamento")
    reproducao_id: Mapped[int | None] = mapped_column(ForeignKey("reproducoes.id", ondelete="SET NULL"))

    reproducao: Mapped[Reproducao | None] = relationship()


class ProducaoOvos(IdMixin, Base):
    __tablename__ = "producao_ovos"

    data_producao: Mapped[date] = mapped_column(Date, nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    quantidade_quebrados: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    lote_id: Mapped[int | None] = mapped_column(ForeignKey("lotes.id", ondelete="SET NULL"))
    gaiola_id: Mapped[int | None] = mapped_column(ForeignKey("gaiolas.id", ondelete="SET NULL"))

    lote: Mapped[Lote | None] = relationship()
    gaiola: Mapped[Gaiola | None] = relationship()


class Cliente(IdMixin, Base):
    __tablename__ = "clientes"

    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    documento: Mapped[str | None] = mapped_column(String(30), unique=True)
    email: Mapped[str | None] = mapped_column(String(255))
    telefone: Mapped[str | None] = mapped_column(String(40))
    endereco: Mapped[str | None] = mapped_column(String(255))

class Venda(IdMixin, Base):
    __tablename__ = "vendas"

    data_venda: Mapped[date] = mapped_column(Date, nullable=False, server_default=func.current_date())
    valor_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="aberta")
    cliente_id: Mapped[int | None] = mapped_column(ForeignKey("clientes.id", ondelete="SET NULL"))
    cliente: Mapped[Cliente | None] = relationship()
    itens: Mapped[list[ItemVenda]] = relationship(back_populates="venda", cascade="all, delete-orphan", passive_deletes=True)


class ItemVenda(IdMixin, Base):
    __tablename__ = "itens_venda"

    venda_id: Mapped[int] = mapped_column(ForeignKey("vendas.id", ondelete="CASCADE"), nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    quantidade: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    valor_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    codorna_id: Mapped[int | None] = mapped_column(ForeignKey("codornas.id", ondelete="SET NULL"))

    venda: Mapped[Venda] = relationship(back_populates="itens")
    codorna: Mapped[Codorna | None] = relationship()


class Despesa(IdMixin, Base):
    __tablename__ = "despesas"

    data_despesa: Mapped[date] = mapped_column(Date, nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    categoria: Mapped[str | None] = mapped_column(String(80))
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    fornecedor_id: Mapped[int | None] = mapped_column(ForeignKey("fornecedores.id", ondelete="SET NULL"))

    fornecedor: Mapped[Fornecedor | None] = relationship()


class Compra(IdMixin, Base):
    __tablename__ = "compras"

    data_compra: Mapped[date] = mapped_column(Date, nullable=False, server_default=func.current_date())
    valor_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="recebida")
    fornecedor_id: Mapped[int | None] = mapped_column(ForeignKey("fornecedores.id", ondelete="SET NULL"))
    fornecedor: Mapped[Fornecedor | None] = relationship()
    itens: Mapped[list[ItemCompra]] = relationship(back_populates="compra", cascade="all, delete-orphan", passive_deletes=True)


class ItemCompra(IdMixin, Base):
    __tablename__ = "itens_compra"

    compra_id: Mapped[int] = mapped_column(ForeignKey("compras.id", ondelete="CASCADE"), nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    quantidade: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    custo_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    alimento_id: Mapped[int | None] = mapped_column(ForeignKey("alimentos.id", ondelete="SET NULL"))

    compra: Mapped[Compra] = relationship(back_populates="itens")
    alimento: Mapped[Alimento | None] = relationship()


class Mortalidade(IdMixin, Base):
    __tablename__ = "mortalidades"

    data_morte: Mapped[date] = mapped_column(Date, nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    causa: Mapped[str | None] = mapped_column(String(255))
    codorna_id: Mapped[int | None] = mapped_column(ForeignKey("codornas.id", ondelete="CASCADE"))
    lote_id: Mapped[int | None] = mapped_column(ForeignKey("lotes.id", ondelete="CASCADE"))

    codorna: Mapped[Codorna | None] = relationship(back_populates="mortalidades")
    lote: Mapped[Lote | None] = relationship()


class Pesagem(IdMixin, Base):
    __tablename__ = "pesagens"

    data_pesagem: Mapped[date] = mapped_column(Date, nullable=False)
    peso: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    observacoes: Mapped[str | None] = mapped_column(Text)
    codorna_id: Mapped[int] = mapped_column(ForeignKey("codornas.id", ondelete="CASCADE"), nullable=False)

    codorna: Mapped[Codorna] = relationship(back_populates="pesagens")


class Eclosao(IdMixin, Base):
    __tablename__ = "ecloses"

    data_eclosao: Mapped[date] = mapped_column(Date, nullable=False)
    quantidade_nascidos: Mapped[int] = mapped_column(Integer, nullable=False)
    quantidade_nao_eclodidos: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    incubacao_id: Mapped[int] = mapped_column(ForeignKey("incubacoes.id", ondelete="CASCADE"), nullable=False)

    incubacao: Mapped[Incubacao] = relationship()


MODEL_CLASSES = (
    Codorna, Raca, Lote, Galpao, Gaiola, Alimento, EstoqueAlimento, Alimentacao,
    Fornecedor, Veterinario, ConsultaVeterinaria, Vacina, Vacinacao, Reproducao,
    Incubacao, ProducaoOvos, Venda, ItemVenda, Cliente, Despesa, Compra,
    ItemCompra, Mortalidade, Pesagem, Eclosao,
)
