import pytest

from databases.models import Admin
from services.admin import autenticar, criar_admin_se_nao_existe, obter_admin, trocar_senha
from tools.seguranca import hash_senha


@pytest.mark.anyio
async def test_autenticar_sucesso():
    await Admin.create(usuario="admin", senha_hash=hash_senha("senha123"))
    admin = await autenticar("admin", "senha123")
    assert admin is not None
    assert admin.usuario == "admin"


@pytest.mark.anyio
async def test_autenticar_senha_errada():
    await Admin.create(usuario="admin", senha_hash=hash_senha("senha123"))
    assert await autenticar("admin", "errada") is None


@pytest.mark.anyio
async def test_autenticar_usuario_inexistente():
    assert await autenticar("ghost", "senha") is None


@pytest.mark.anyio
async def test_autenticar_admin_inativo():
    await Admin.create(usuario="admin", senha_hash=hash_senha("senha123"), ativo=False)
    assert await autenticar("admin", "senha123") is None


@pytest.mark.anyio
async def test_trocar_senha_sucesso():
    await Admin.create(usuario="admin", senha_hash=hash_senha("velha"))
    resultado = await trocar_senha("admin", "velha", "nova123")
    assert resultado is True

    admin = await autenticar("admin", "nova123")
    assert admin is not None


@pytest.mark.anyio
async def test_trocar_senha_atual_errada():
    await Admin.create(usuario="admin", senha_hash=hash_senha("velha"))
    resultado = await trocar_senha("admin", "errada", "nova123")
    assert resultado is False


@pytest.mark.anyio
async def test_obter_admin():
    await Admin.create(usuario="admin", senha_hash=hash_senha("s"))
    admin = await obter_admin("admin")
    assert admin is not None
    assert await obter_admin("ghost") is None


@pytest.mark.anyio
async def test_criar_admin_se_nao_existe():
    admin = await criar_admin_se_nao_existe("novo", "senha")
    assert admin.usuario == "novo"

    admin2 = await criar_admin_se_nao_existe("novo", "outra")
    assert admin2.id == admin.id
