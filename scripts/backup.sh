#!/usr/bin/env bash
# Backup do mundo e configs. Uso: ./scripts/backup.sh   (cron: 0 */2 * * * /caminho/scripts/backup.sh)
# Mantém os 10 backups mais recentes. Se o servidor estiver rodando em screen/tmux, use `save-all` antes
# (o script tenta via screen "mc" se existir).
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/backups"; mkdir -p "$DEST"
screen -list 2>/dev/null | grep -q "\.mc" && { screen -S mc -p 0 -X stuff "save-off\nsave-all flush\n"; sleep 5; }
python3 "$ROOT/scripts/banco_dados.py" salvar "Snapshot de Backup" >/dev/null 2>&1 || true
STAMP=$(date +%Y%m%d-%H%M%S)
tar -czf "$DEST/backup-$STAMP.tar.gz" -C "$ROOT" dados world world_nether world_the_end plugins/Skript plugins/Essentials \
  plugins/DynamicShop plugins/QuickShop-Hikari plugins/GriefPreventionData plugins/LuckPerms server.properties 2>/dev/null
screen -list 2>/dev/null | grep -q "\.mc" && screen -S mc -p 0 -X stuff "save-on\n"
ls -1t "$DEST"/backup-*.tar.gz | tail -n +11 | xargs -r rm --
echo "Backup criado: backup-$STAMP.tar.gz (inclui dados/aurelion.db)"
