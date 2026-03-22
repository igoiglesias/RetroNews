from tortoise import fields
from tortoise.models import Model


class Feed(Model):
    id = fields.IntField(primary_key=True)
    nome = fields.CharField(max_length=200)
    url_rss = fields.CharField(max_length=500, unique=True)
    url_site = fields.CharField(max_length=500)
    ativo = fields.BooleanField(default=True)
    criado_em = fields.DatetimeField(auto_now_add=True)
    atualizado_em = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "feed"

    def __str__(self) -> str:
        return self.nome


class Tag(Model):
    id = fields.IntField(primary_key=True)
    nome = fields.CharField(max_length=100, unique=True)

    class Meta:
        table = "tag"

    def __str__(self) -> str:
        return self.nome


class Noticia(Model):
    id = fields.IntField(primary_key=True)
    feed = fields.ForeignKeyField("models.Feed", related_name="noticias")
    titulo = fields.CharField(max_length=500)
    titulo_pt = fields.CharField(max_length=500, null=True)
    url = fields.CharField(max_length=1000, unique=True)
    resumo_original = fields.TextField(default="")
    resumo_ia = fields.TextField(null=True)
    tentativas_ia = fields.IntField(default=0)
    erro_ia = fields.TextField(null=True)
    autor = fields.CharField(max_length=200, null=True)
    data_publicacao = fields.DatetimeField(null=True)
    tags = fields.ManyToManyField("models.Tag", related_name="noticias", through="noticia_tag")
    criado_em = fields.DatetimeField(auto_now_add=True)
    atualizado_em = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "noticia"
        ordering = ["-data_publicacao", "-criado_em"]

    def __str__(self) -> str:
        return self.titulo


class LogProcessamento(Model):
    id = fields.IntField(primary_key=True)
    tipo = fields.CharField(max_length=50)
    mensagem = fields.TextField()
    detalhes = fields.TextField(null=True)
    criado_em = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "log_processamento"
        ordering = ["-criado_em"]

    def __str__(self) -> str:
        return f"[{self.tipo}] {self.mensagem}"


class ConfigIA(Model):
    id = fields.IntField(primary_key=True)
    chave = fields.CharField(max_length=100, unique=True)
    valor = fields.TextField()
    atualizado_em = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "config_ia"

    def __str__(self) -> str:
        return self.chave


class Sugestao(Model):
    id = fields.IntField(primary_key=True)
    nome_site = fields.CharField(max_length=200)
    url_site = fields.CharField(max_length=500)
    url_rss = fields.CharField(max_length=500, default="")
    motivo = fields.TextField(default="")
    status = fields.CharField(max_length=20, default="pendente")
    ip_remetente = fields.CharField(max_length=45, default="")
    criado_em = fields.DatetimeField(auto_now_add=True)
    atualizado_em = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "sugestao"
        ordering = ["-criado_em"]

    def __str__(self) -> str:
        return self.nome_site


class Admin(Model):
    id = fields.IntField(primary_key=True)
    usuario = fields.CharField(max_length=100, unique=True)
    senha_hash = fields.CharField(max_length=255)
    ativo = fields.BooleanField(default=True)
    criado_em = fields.DatetimeField(auto_now_add=True)
    atualizado_em = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "admin"

    def __str__(self) -> str:
        return self.usuario
