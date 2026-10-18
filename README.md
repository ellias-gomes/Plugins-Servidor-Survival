# Cinzas de Aurelion - Servidor Survival Co-op (Minecraft 26.3)

Servidor privado para **Ellias** e **Pedro**: Paper 26.3 + Java 25, economia dinâmica com moedas físicas e câmbio de Villagers, bosses naturais com mecânicas interativas (pilares, raios, rasantes), missões secundárias estilo Skyrim com feitiços e semi-bosses, lápides sagradas, pets e Diário de Bordo.

## Início rápido
```bash
./scripts/verificar_tudo.sh      # diagnóstico completo dos arquivos, binários e plugins
./scripts/aceitar_eula.sh        # aceita o EULA da Mojang (leia antes: https://aka.ms/MinecraftEULA)
./start.sh                       # 1ª execução: gera mundo (com Terralith) e configs. Digite 'stop' após carregar
./scripts/pos_setup.sh           # ajusta economia nos configs gerados (servidor parado)
./start.sh                       # inicia de novo
# No console: cole os comandos de scripts/comandos_iniciais.txt (whitelist, grupos, permissões e claims)
# Dentro do jogo (como Ellias/OP):  /aurelionsetup
./scripts/tunel_playit.sh        # túnel playit.gg para o Pedro conectar (ver docs/REDE.md)
```

## Documentação Completa
| Arquivo | Conteúdo |
|---|---|
| [docs/REDE.md](docs/REDE.md) | Setup local, otimização, túnel (playit.gg), backups e Aikar flags |
| [docs/PLUGINS.md](docs/PLUGINS.md) | Stack de plugins, sinergias e atendimento aos perfis do Pedro e do Ellias |
| [docs/ECONOMIA.md](docs/ECONOMIA.md) | Moedas físicas, câmbio com Villagers, inflação, juros e lojas (/shop e /qs) |
| [docs/LORE.md](docs/LORE.md) | Crônicas em Livro escrito, os Gêmeos, memórias e os Finais (Restaurar vs Libertar) |
| [docs/ROADMAP.md](docs/ROADMAP.md) | 10 objetivos, caçadas Skyrim, feitiços e mecânicas dos 5 Guardiões |

## Comandos Principais no Jogo
- **Missões e Lore:** `/lore livro` (receber o livro físico), `/diario`, `/mentor`, `/memorias`, `/final`
- **Caçadas e Feitiços (Skyrim):** `/cacadas` (mural de semi-bosses e artefatos), `/missoes`
- **Economia e Comércio:** `/economia`, `/banco`, `/moeda` (sacar/depositar moedas físicas), `/cambio` (Villagers), `/lojas` (guia do /shop e /qs), `/shop`, `/sell`, `/qs`
- **Busca aos Guardiões e Combate:** `/guardioes` ou `/bussola` (rastreia o próximo Guardião no mapa natural), `/despertar` (desperta no Altar), `/lapide`, `/pet`, `/runas`
- **Banco de Dados e Reset de Avanço:** `/db` (painel GUI de banco de dados e reset), `/salvarbanco` (salva imediatamente), `/resetarprogresso confirmar [kit]` (zera todo o avanço do mapa)
- **Administração:** `/aurelionsetup`, `/ecoadmin`, `/aurelion`, `/modelos <teste 1..12|limpar>` (inspecionar modelos 3D e animações)

## Estrutura do Projeto
- `plugins/Skript/scripts/` - Módulos de regras (`economia.sk`, `banco.sk`, `lapide.sk`, `itens.sk`, `bosses.sk`, `progressao.sk`, `diario.sk`, `lore.sk`, `skyrim.sk`, `modelos.sk`, `sistema_dados.sk`).
- `dados/aurelion.db` - Banco de dados relacional SQLite com fichas de jogadores, estado econômico, bosses, objetivos e histórico de snapshots restauráveis.
- `scripts/` - Automação (`verificar_tudo.sh`, `banco_dados.py`, `resetar_avanco.sh`, `gerar_modelos.py`, `baixar_plugins.sh`, `backup.sh`, `tunel_playit.sh`, `pos_setup.sh`, `aceitar_eula.sh`, `comandos_iniciais.txt`).
- `world/datapacks/` - `Terralith` (biomas épicos) + `aurelion_modelos` (12 modelos 3D multi-partes com animações interpoladas + feixe sônico direcional `fus_ro_dah`, 100% server-side).
- `backups/` - Diretório de rotação de backups automáticos (últimos 10 snapshots).
