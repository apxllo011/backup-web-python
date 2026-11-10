# Script de backup e retenção com Python

Atividade prática de automação de backup, feita para a disciplina do professor Denilson Bonatti. O script copia o conteúdo do servidor web para um arquivo compactado, gera o hash de verificação, apaga backups antigos e protege a pasta de destino com permissões restritas.

Testado no SEU SISTEMA (exemplo: Fedora Linux 44 Server), com Python 3 e Apache (httpd) instalado.

## O que o script faz

O script executa as etapas nesta ordem:

1. Cria o diretório `/backup/web/` caso ele ainda não exista.
2. Compacta tudo o que está em `/var/www/html/` no arquivo `backup_web_AAAA-MM-DD_HH-MM.tar.gz`, usando a data e a hora do momento da execução.
3. Calcula o hash SHA-256 do arquivo gerado e salva em `backup_web_AAAA-MM-DD_HH-MM.tar.gz.sha256` (desafio extra).
4. Procura backups `.tar.gz` com mais de 7 dias em `/backup/web/` e remove esses arquivos junto com o `.sha256` correspondente. No terminal aparece a lista do que foi removido ou uma mensagem dizendo que nada passou do prazo.
5. Ajusta as permissões de `/backup/`: 700 nos diretórios e 600 nos arquivos (desafio extra).

O script precisa ser executado como root. Se for rodado sem `sudo`, ele mostra um aviso e encerra.

## Como usar

Instalar o necessário e criar uma página de teste, caso o servidor web esteja vazio:

```bash
sudo dnf install -y git python3 httpd
echo Teste de backup | sudo tee /var/www/html/index.html
```

Baixar o repositório e executar:

```bash
git clone https://github.com/SEU_USUARIO/backup-web-python.git
cd backup-web-python
sudo python3 backup_web.py
```

Para guardar a saída em um arquivo de log:

```bash
sudo python3 backup_web.py | tee execucao.log
```

### Conferir a integridade de um backup

```bash
sudo sh -c 'cd /backup/web && sha256sum -c backup_web_AAAA-MM-DD_HH-MM.tar.gz.sha256'
```

O resultado esperado é `SUCESSO` (ou `OK`, dependendo do idioma do sistema).

### Agendar execução automática (opcional)

Para rodar todo dia às 02:00, adicione esta linha em `sudo crontab -e`:

```
0 2 * * * /usr/bin/python3 /caminho/para/backup_web.py >> /var/log/backup_web.log 2>&1
```

## Bibliotecas usadas

Somente bibliotecas padrão do Python, sem instalar nada com pip:

- `os`: criação de diretórios, listagem de arquivos, remoção e permissões
- `tarfile`: criação do arquivo `.tar.gz`
- `hashlib`: cálculo do SHA-256
- `datetime` e `time`: nome do arquivo com data e hora e cálculo dos 7 dias

## Sobre a retenção

O Linux não guarda de forma confiável a data de criação de um arquivo, então a regra dos 7 dias usa a data da última modificação (`mtime`). Como um backup não é alterado depois de criado, essa data é equivalente à de criação.

## Evidências de execução

### 1. Execução do script

Primeira execução. O diretório `/backup/web` foi criado, o backup foi gerado, o SHA-256 foi calculado e salvo, nenhum arquivo passou do prazo de retenção e as permissões foram ajustadas.

![Execução do script](prints/execucao.png)

### 2. Arquivos gerados

Listagem de `/backup/web/` com o arquivo `.tar.gz` e o `.sha256` criados.

![Listagem dos arquivos](prints/listagem.png)

### 3. Validação do checksum

O `sha256sum -c` confirma que o arquivo `.tar.gz` bate com o hash salvo.

![Validação do checksum](prints/checksum.png)

### 4. Permissões

Os diretórios `/backup` e `/backup/web` aparecem como `drwx------` (700) e os arquivos como `-rw-------` (600), todos pertencentes ao root.

![Permissões](prints/permissoes.png)

### 5. Política de retenção

Para testar, criei dois arquivos falsos com data de 10 dias atrás usando `touch -d "10 days ago"`: um `.tar.gz` e o `.sha256` correspondente. Ao executar o script de novo, os dois foram listados como removidos e sobraram apenas os backups novos.

```bash
sudo touch -d "10 days ago" /backup/web/backup_web_2026-01-01_10-00.tar.gz /backup/web/backup_web_2026-01-01_10-00.tar.gz.sha256
sudo python3 backup_web.py | tee execucao_retencao.log
sudo ls -la /backup/web/
```

![Teste de retenção](prints/retencao.png)

## Estrutura do repositório

```
backup-web-python/
├── backup_web.py
├── README.md
└── prints/
    ├── execucao.png
    ├── listagem.png
    ├── checksum.png
    ├── permissoes.png
    └── retencao.png
```

## Autor

SEU NOME, estudante de Sistemas de Informação.
