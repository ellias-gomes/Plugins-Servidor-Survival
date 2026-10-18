# Rede, otimização e backups

## Máquina e Java
- Java 25 (Temurin/OpenJDK) já instalado; Paper **26.3 build 202** em `paper.jar`.
- RAM padrão do `start.sh`: **5 GB** (máquina de 12 GB). Altere com `RAM=6G ./start.sh`.
- `start.sh` usa as flags Aikar e reinicia o servidor se ele cair (Ctrl+C para sair).
- `server.properties`: `view-distance=12`, `simulation-distance=8`, `sync-chunk-writes=false`, `white-list=true`, `online-mode=true`, `pvp=false`, `difficulty=hard`.

## Pré-geração e borda
No console, após o `/aurelionsetup` (borda de 12000 blocos):
```
chunky world world
chunky radius 3000
chunky start
```
Pré-gerar evita lag ao explorar (o Pedro é explorador). Expanda o raio aos poucos. A borda cresce +6000 no fim da campanha (`/final`).

## Túnel: playit.gg (recomendado)
1. Baixe o agente em https://playit.gg/download (Linux), salve em `scripts/playit` e `chmod +x`.
2. `./scripts/tunel_playit.sh` -> abre link para vincular à conta (grátis).
3. No painel: Tunnels > Add > **Minecraft Java** > `127.0.0.1:25565`.
4. Envie o endereço ao Pedro. **Só o host instala algo.**

Por que playit: funciona atrás de CGNAT, sem abrir portas no roteador, IP estável, sem instalação para o Pedro.
Alternativa: **Radmin VPN** (menor latência, ambos instalam; use o IP Radmin do host na porta 25565).
Evite Ngrok (TCP gratuito limitado, endereço muda).

Segurança: `white-list=true` + `online-mode=true`; adicione apenas Ellias e Pedro.

## Backups
- `./scripts/backup.sh` guarda os 10 últimos `.tar.gz` em `backups/`.
- Cron a cada 2 h: `0 */2 * * * /media/elliasgomes/HD_1TB/apps/servidor_minecraft/scripts/backup.sh`
- Rode dentro de `screen -S mc` para o script fazer `save-all flush` automaticamente.
- Faça backup **antes de atualizar qualquer plugin**. Mundos 26.x não voltam para versões anteriores.

## Monitoramento
`/spark profiler start` / `stop` (instale o plugin Spark se quiser; não vem incluso porque não havia build 26.3 no Modrinth). O Paper tem `/tps` e `/mspt`.
Mapa web: **BlueMap** (`plugins/BlueMap`, aceite os downloads na config e rode `/bluemap render`).
