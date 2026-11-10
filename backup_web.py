#!/usr/bin/env python3
# Backup do servidor web com retencao de 7 dias (Fedora / RHEL).
# Uso: sudo python3 backup_web.py

import hashlib
import os
import sys
import tarfile
import time
from datetime import datetime

# Caminhos e configuracoes
ORIGEM = "/var/www/html/"
RAIZ_BACKUP = "/backup"
DESTINO = "/backup/web"
DIAS_RETENCAO = 7


def verificar_root():
    # O usuario root tem o numero 0. Se nao for ele, o script para.
    if os.geteuid() != 0:
        print("[ERRO] Execute como root: sudo python3 backup_web.py")
        sys.exit(1)


def criar_diretorio():
    # Etapa 1: cria /backup/web se ainda nao existir
    if os.path.isdir(DESTINO):
        print(f"[OK] Diretorio ja existe: {DESTINO}")
    else:
        os.makedirs(DESTINO)
        print(f"[OK] Diretorio criado: {DESTINO}")


def gerar_backup():
    # Etapa 2: compacta /var/www/html em um .tar.gz com data e hora no nome
    if not os.path.isdir(ORIGEM):
        print(f"[ERRO] Diretorio de origem nao encontrado: {ORIGEM}")
        sys.exit(1)

    agora = datetime.now()
    nome = "backup_web_" + agora.strftime("%Y-%m-%d_%H-%M") + ".tar.gz"
    caminho = os.path.join(DESTINO, nome)

    print(f"[..] Compactando {ORIGEM} ...")
    with tarfile.open(caminho, "w:gz") as tar:
        tar.add(ORIGEM, arcname="html")
    print(f"[OK] Backup gerado: {caminho}")
    return caminho


def gerar_checksum(caminho):
    # Etapa 3 (extra): calcula o SHA-256 e salva em um arquivo .sha256
    sha256 = hashlib.sha256()
    with open(caminho, "rb") as f:
        # le o arquivo aos poucos para nao usar muita memoria
        for bloco in iter(lambda: f.read(65536), b""):
            sha256.update(bloco)
    digest = sha256.hexdigest()

    caminho_hash = caminho + ".sha256"
    with open(caminho_hash, "w") as f:
        # formato que o comando "sha256sum -c" entende
        f.write(f"{digest}  {os.path.basename(caminho)}\n")
    print(f"[OK] SHA-256: {digest}")
    print(f"[OK] Hash salvo em: {caminho_hash}")


def aplicar_retencao():
    # Etapa 4: remove backups com mais de 7 dias
    limite = time.time() - DIAS_RETENCAO * 24 * 60 * 60
    removidos = []

    for nome in os.listdir(DESTINO):
        if not nome.endswith(".tar.gz"):
            continue
        caminho = os.path.join(DESTINO, nome)
        # usa a data de modificacao, que no backup equivale a de criacao
        if os.path.getmtime(caminho) < limite:
            os.remove(caminho)
            removidos.append(nome)
            hash_assoc = caminho + ".sha256"
            if os.path.exists(hash_assoc):
                os.remove(hash_assoc)
                removidos.append(nome + ".sha256")

    if removidos:
        print(f"[OK] Arquivos removidos (mais de {DIAS_RETENCAO} dias):")
        for nome in removidos:
            print(f"     - {nome}")
    else:
        print(f"[OK] Nenhum arquivo ultrapassou o periodo de retencao de {DIAS_RETENCAO} dias.")


def ajustar_permissoes():
    # Etapa 5 (extra): 700 nos diretorios e 600 nos arquivos de /backup
    for pasta, subpastas, arquivos in os.walk(RAIZ_BACKUP):
        os.chmod(pasta, 0o700)
        for arquivo in arquivos:
            os.chmod(os.path.join(pasta, arquivo), 0o600)
    print(f"[OK] Permissoes ajustadas em {RAIZ_BACKUP} (diretorios 700, arquivos 600)")


def main():
    verificar_root()
    print("=== Inicio do backup:", datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "===")
    criar_diretorio()
    arquivo = gerar_backup()
    gerar_checksum(arquivo)
    aplicar_retencao()
    ajustar_permissoes()
    print("=== Backup finalizado com sucesso ===")


if __name__ == "__main__":
    main()
