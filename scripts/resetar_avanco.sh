#!/usr/bin/env bash
# ============================================================================
#  RESETADOR DE AVANÇO E MAPA - Cinzas de Aurelion (26.3)
#  Uso:
#    ./scripts/resetar_avanco.sh                 -> Zera todo o avanço (bosses, diário, banco, caçadas, saldos), mantendo o mapa construído
#    ./scripts/resetar_avanco.sh --mapa-completo -> Zera todo o avanço E recria o mundo do zero (preservando os datapacks Terralith e aurelion_modelos)
# ============================================================================
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MODO="${1:---progresso}"

echo "=== RESET DE AVANÇO - CINZAS DE AURELION ==="
echo "1. Salvando snapshot de segurança no Banco de Dados SQLite (dados/aurelion.db)..."
python3 scripts/banco_dados.py resetar

if [ "$MODO" = "--mapa-completo" ]; then
    echo "2. Removendo regiões antigas do mundo (preservando datapacks Terralith e aurelion_modelos)..."
    TMP_DP="$(mktemp -d)"
    if [ -d "world/datapacks" ]; then
        cp -r world/datapacks/* "$TMP_DP/" 2>/dev/null || true
    fi
    rm -rf world world_nether world_the_end
    mkdir -p world/datapacks
    cp -r "$TMP_DP"/* world/datapacks/ 2>/dev/null || true
    rm -rf "$TMP_DP"
    rm -f plugins/GriefPreventionData/ClaimData/* 2>/dev/null || true
    echo "[OK] Mundo, dimensões e avanço totalmente resetados (datapacks mantidos em world/datapacks/)!"
else
    echo "[OK] Avanço da campanha, bosses, diário, caçadas, banco e saldos resetados (construções do mapa mantidas)!"
    echo "     (Dica: se o servidor estiver aberto no momento, use /resetarprogresso confirmar dentro do jogo!)"
fi
