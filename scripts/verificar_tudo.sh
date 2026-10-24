#!/usr/bin/env bash
# ============================================================================
#  VERIFICADOR DE INTEGRIDADE DO SERVIDOR - Cinzas de Aurelion (26.3)
# ============================================================================
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== DIAGNÓSTICO DO SERVIDOR CINZAS DE AURELION ==="
echo

# 1. Java
JAVA_VER=$(java -version 2>&1 | head -1)
if echo "$JAVA_VER" | grep -q "25"; then
    echo "[OK] Java Runtime: $JAVA_VER (Compatível com 26.3)"
else
    echo "[ALERTA] Java pode não ser a versão 25: $JAVA_VER"
fi

# 2. Paper Jar
if [ -f "paper.jar" ]; then
    SIZE=$(du -h paper.jar | awk '{print $1}')
    echo "[OK] paper.jar presente ($SIZE)"
else
    echo "[FALHA] paper.jar não encontrado!"
fi

# 3. EULA
if [ -f "eula.txt" ] && grep -q "eula=true" eula.txt; then
    echo "[OK] EULA da Mojang aceito (eula=true)"
else
    echo "[AVISO] EULA ainda não aceito. Rode: ./scripts/aceitar_eula.sh"
fi

# 4. Plugins
echo
echo "--- Verificação de Plugins ---"
PLUGINS_ESPERADOS=(
    "LuckPerms-Bukkit"
    "VaultUnlocked"
    "EssentialsX"
    "GriefPrevention"
    "DynamicShop"
    "QuickShop-Hikari"
    "Skript"
    "Chunky-Bukkit"
    "bluemap"
    "PlaceholderAPI"
)

for p in "${PLUGINS_ESPERADOS[@]}"; do
    if ls plugins/$p*.jar 1>/dev/null 2>&1; then
        echo "  [OK] Plugin: $p"
    else
        echo "  [FALTA] Plugin: $p não encontrado!"
    fi
done

# 5. Skripts
echo
echo "--- Verificação de Módulos Skript ---"
SCRIPTS_ESPERADOS=(
    "economia.sk"
    "banco.sk"
    "lapide.sk"
    "itens.sk"
    "bosses.sk"
    "progressao.sk"
    "diario.sk"
    "lore.sk"
    "skyrim.sk"
    "modelos.sk"
    "sistema_dados.sk"
    "racas_classes.sk"
    "profissoes.sk"
    "forja_artefatos.sk"
    "skins_itens.sk"
)

for s in "${SCRIPTS_ESPERADOS[@]}"; do
    if [ -f "plugins/Skript/scripts/$s" ]; then
        LINES=$(wc -l < "plugins/Skript/scripts/$s")
        echo "  [OK] Script: $s ($LINES linhas)"
    else
        echo "  [FALTA] Script: $s não encontrado!"
    fi
done

# 6. Datapacks & Banco de Dados
echo
echo "--- Datapacks e Banco de Dados SQLite ---"
if ls world/datapacks/Terralith*.zip 1>/dev/null 2>&1; then
    echo "  [OK] Terralith instalado em world/datapacks/"
else
    echo "  [FALTA] Datapack Terralith não encontrado!"
fi

if [ -f "world/datapacks/aurelion_modelos/pack.mcmeta" ]; then
    COUNT=$(find world/datapacks/aurelion_modelos -name "*.mcfunction" | wc -l)
    echo "  [OK] Datapack 3D 'aurelion_modelos' instalado ($COUNT mcfunctions de modelos, feixe sônico e animações)"
else
    echo "  [FALTA] Datapack 'aurelion_modelos' não encontrado! Rode: python3 scripts/gerar_modelos.py"
fi

if [ -f "resourcepack/aurelion_resourcepack.zip" ]; then
    RP_SIZE=$(du -h resourcepack/aurelion_resourcepack.zip | awk '{print $1}')
    echo "  [OK] Resource Pack 'aurelion_resourcepack.zip' presente ($RP_SIZE - 32 skins e modelos 1ª/3ª pessoa)"
else
    echo "  [FALTA] Resource Pack de skins não encontrado! Rode: ./scripts/instalar_skins.sh"
fi

if [ -f "dados/aurelion.db" ]; then
    DB_SIZE=$(du -h dados/aurelion.db | awk '{print $1}')
    echo "  [OK] Banco de Dados SQLite 'dados/aurelion.db' ativo ($DB_SIZE)"
else
    echo "  [AVISO] Banco SQLite ainda não inicializado. Rode: python3 scripts/banco_dados.py salvar"
fi

# 7. Túnel
echo
echo "--- Túnel / Rede ---"
if [ -x "scripts/playit" ]; then
    echo "  [OK] Binário playit.gg instalado e executável"
else
    echo "  [AVISO] Binário playit.gg não detectado (será baixado no primeiro uso do ./scripts/tunel_playit.sh)"
fi

echo
echo "=== TUDO PRONTO PARA O CO-OP COM O PEDRO ==="
echo "1. Aceite o EULA: ./scripts/aceitar_eula.sh"
echo "2. Inicie o servidor: ./start.sh"
echo "3. Em outro terminal, inicie o túnel: ./scripts/tunel_playit.sh"
echo "4. Bom jogo!"
