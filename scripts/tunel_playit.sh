#!/usr/bin/env bash
# ============================================================================
#  TÚNEL PLAYIT.GG - Compartilhamento de IP seguro sem abrir portas no roteador
#  - Baixa automaticamente o binário oficial para Linux (se ainda não existir).
#  - Inicia o túnel e exibe as orientações de conexão para o Pedro.
# ============================================================================
set -uo pipefail
cd "$(dirname "$0")" || exit 1

PLAYIT_BIN="./playit"

if [ ! -x "$PLAYIT_BIN" ]; then
    echo ">> [playit.gg] Binário não encontrado. Detectando arquitetura e baixando..."
    ARCH=$(uname -m)
    case "$ARCH" in
        x86_64)  TARGET="playit-linux-amd64" ;;
        aarch64) TARGET="playit-linux-aarch64" ;;
        armv7l)  TARGET="playit-linux-armv7" ;;
        *)       TARGET="playit-linux-amd64" ;;
    esac

    URL="https://github.com/playit-cloud/playit-agent/releases/download/v1.0.10/$TARGET"
    echo ">> Baixando de: $URL"
    curl -sSL -o "$PLAYIT_BIN" "$URL"
    chmod +x "$PLAYIT_BIN"
    echo ">> [playit.gg] Binário instalado com sucesso!"
fi

echo "===================================================================="
echo ">> INICIANDO O TÚNEL PLAYIT.GG..."
echo ">> Se for a 1ª execução:"
echo "   1) O terminal mostrará uma URL (ex: https://playit.gg/claim/...)."
echo "   2) Abra essa URL no navegador para vincular à sua conta gratuita."
echo "   3) Crie o túnel tipo 'Minecraft Java' apontando para 127.0.0.1:25565."
echo "   4) Copie o endereço gerado (ex: xxxx.joinmc.link) e envie ao Pedro."
echo "===================================================================="
exec "$PLAYIT_BIN"
