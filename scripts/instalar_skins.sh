#!/usr/bin/env bash
# ============================================================================
#  INSTALADOR DE SKINS & MODELOS 3D - Cinzas de Aurelion (26.3)
#  - Gera o pacote resourcepack/aurelion_resourcepack.zip (32 skins 1ª/3ª pessoa)
#  - Copia automaticamente para pastas .minecraft/resourcepacks locais encontradas
# ============================================================================
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== GERANDO SKINS E MODELOS 3D DE ITENS (1ª E 3ª PESSOA) ==="
python3 scripts/gerar_skins_itens.py

ZIP="$ROOT/resourcepack/aurelion_resourcepack.zip"
SHA=$(cat "$ROOT/resourcepack/aurelion_resourcepack.sha1" | tr -d '[:space:]')

# Procura pastas de resourcepacks do cliente Minecraft no computador local
DESTINOS=(
    "$HOME/.minecraft/resourcepacks"
    "$HOME/.var/app/com.mojang.Minecraft/.minecraft/resourcepacks"
    "$HOME/.var/app/org.prismlauncher.PrismLauncher/data/PrismLauncher/instances"
    "$HOME/.local/share/PrismLauncher/instances"
)

COPIADO=0
for d in "${DESTINOS[@]}"; do
    if [ -d "$d" ]; then
        if [[ "$d" == *"instances"* ]]; then
            for inst in "$d"/*/minecraft/resourcepacks "$d"/*/.minecraft/resourcepacks; do
                if [ -d "$inst" ]; then
                    cp -f "$ZIP" "$inst/aurelion_resourcepack.zip"
                    echo "[OK] Copiado para instância: $inst/aurelion_resourcepack.zip"
                    COPIADO=$((COPIADO + 1))
                fi
            done
        else
            cp -f "$ZIP" "$d/aurelion_resourcepack.zip"
            echo "[OK] Copiado para cliente local: $d/aurelion_resourcepack.zip"
            COPIADO=$((COPIADO + 1))
        fi
    fi
done

if [ "$COPIADO" -eq 0 ]; then
    mkdir -p "$HOME/.minecraft/resourcepacks"
    cp -f "$ZIP" "$HOME/.minecraft/resourcepacks/aurelion_resourcepack.zip"
    echo "[OK] Criado e copiado para: $HOME/.minecraft/resourcepacks/aurelion_resourcepack.zip"
fi

echo
echo "=== PRONTO! ==="
echo "• Pacote gerado: $ZIP"
echo "• SHA-1: $SHA"
echo "• No Minecraft: vá em Opções -> Pacotes de Recursos e ative 'aurelion_resourcepack.zip'"
echo "  (ou clique em 'Carregar Resource Pack de Skins' na Bancada de Trabalho / /skins dentro do jogo!)"
