from databases.models import Admin
from tools.seguranca import hash_senha, verificar_senha


async def autenticar(usuario: str, senha: str) -> Admin | None:
    admin = await Admin.get_or_none(usuario=usuario, ativo=True)
    if not admin:
        return None
    if not verificar_senha(senha, admin.senha_hash):
        return None
    return admin


async def trocar_senha(usuario: str, senha_atual: str, senha_nova: str) -> bool:
    admin = await autenticar(usuario, senha_atual)
    if not admin:
        return False

    admin.senha_hash = hash_senha(senha_nova)
    await admin.save()
    return True


async def obter_admin(usuario: str) -> Admin | None:
    return await Admin.get_or_none(usuario=usuario, ativo=True)


async def criar_admin_se_nao_existe(usuario: str, senha: str) -> Admin:
    admin = await Admin.get_or_none(usuario=usuario)
    if admin:
        return admin
    return await Admin.create(usuario=usuario, senha_hash=hash_senha(senha))
