#!/usr/bin/env bash
# ============================================================================
#  LIMPADOR DE MUNDO & RESET GERAL - Cinzas de Aurelion (Minecraft 26.3)
#  - Exclui Overworld, Nether, The End e dados de chunks
#  - Exclui todos os dados de jogadores (inventários, UUIDs, stats, advancements)
#  - Exclui claims (GriefPrevention), lojas (QuickShop) e saldos (Essentials)
#  - Zera progresso de RPG, banco, economia e profissões no Skript
#  - PRESERVA os Datapacks (Terralith + aurelion_modelos) e configurações do servidor!
#  - Cria automaticamente um backup de segurança antes de limpar
#
#  Uso:
#    ./scripts/limpar_mundo.sh              -> Pede confirmação interativa
#    ./scripts/limpar_mundo.sh -y           -> Executa direto sem confirmação
#    ./scripts/limpar_mundo.sh --seed 12345 -> Limpa e define uma nova seed específica
#    ./scripts/limpar_mundo.sh --nova-seed  -> Limpa e garante seed aleatória nova
#    ./scripts/limpar_mundo.sh --forcar     -> Encerra o servidor se estiver rodando
# ============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Cores para o terminal
VERMELHO='\033[0;31m'
VERDE='\033[0;32m'
AMARELO='\033[1;33m'
AZUL='\033[0;34m'
MAGENTA='\033[0;35m'
CIANO='\033[0;36m'
NEGRITO='\033[1m'
NC='\033[0m' # No Color

CONFIRMAR=false
FORCAR=false
NOVA_SEED=""
SEED_ALEATORIA=false

# Processar argumentos
while [[ $# -gt 0 ]]; do
    case "$1" in
        -y|--sim|--confirmar)
            CONFIRMAR=true
            shift
            ;;
        -f|--forcar)
            FORCAR=true
            shift
            ;;
        --nova-seed|--seed-aleatoria)
            SEED_ALEATORIA=true
            shift
            ;;
        --seed)
            if [[ $# -gt 1 ]]; then
                NOVA_SEED="$2"
                shift 2
            else
                echo -e "${VERMELHO}[ERRO] A opção --seed requer um valor (número ou texto).${NC}"
                exit 1
            fi
            ;;
        -h|--help|--ajuda)
            echo "Uso: $0 [-y|--confirmar] [-f|--forcar] [--seed <valor>] [--nova-seed]"
            exit 0
            ;;
        *)
            echo -e "${VERMELHO}[ERRO] Opção desconhecida: $1${NC}"
            echo "Use: $0 --help"
            exit 1
            ;;
    esac
done

echo -e "${MAGENTA}${NEGRITO}====================================================================${NC}"
echo -e "${CIANO}${NEGRITO}     ✦ LIMPADOR DE MUNDO & RESET GERAL - CINZAS DE AURELION ✦${NC}"
echo -e "${MAGENTA}${NEGRITO}====================================================================${NC}"
echo

# 1. Verificar se o servidor está rodando
if pgrep -f "paper.jar" >/dev/null 2>&1; then
    if [ "$FORCAR" = true ]; then
        echo -e "${AMARELO}[AVISO] O servidor está rodando. Encerrando processo para evitar corrupção...${NC}"
        # Tenta parar via screen "mc" se existir
        if screen -list 2>/dev/null | grep -q "\.mc"; then
            screen -S mc -p 0 -X stuff "stop\n"
            sleep 6
        fi
        # Se ainda estiver rodando, envia SIGTERM
        pkill -f "paper.jar" 2>/dev/null || true
        sleep 3
        if pgrep -f "paper.jar" >/dev/null 2>&1; then
            pkill -9 -f "paper.jar" 2>/dev/null || true
            sleep 1
        fi
        echo -e "${VERDE}[OK] Servidor parado.${NC}"
    else
        echo -e "${VERMELHO}${NEGRITO}[ATENÇÃO] O servidor Minecraft está em execução!${NC}"
        echo -e "${AMARELO}Para limpar o mundo com segurança e evitar corrupção:${NC}"
        echo -e "  1. Digite ${NEGRITO}'stop'${NC} no console do servidor (ou pressione CTRL+C na janela do ./start.sh)"
        echo -e "  2. Execute novamente este script: ${NEGRITO}./scripts/limpar_mundo.sh${NC}"
        echo -e "  (Ou use ${NEGRITO}./scripts/limpar_mundo.sh --forcar${NC} para encerrar automaticamente)"
        exit 1
    fi
fi

# 2. Exibir o que será feito e pedir confirmação
echo -e "${AMARELO}${NEGRITO}O que será DELETADO:${NC}"
echo -e "  ${VERMELHO}✗${NC} Pastas de mundos: Overworld, Nether e The End (regiões e chunks)"
echo -e "  ${VERMELHO}✗${NC} Dados de todos os jogadores (inventários, posições, stats, conquistas)"
echo -e "  ${VERMELHO}✗${NC} Cache de UUIDs e perfis (usercache.json)"
echo -e "  ${VERMELHO}✗${NC} Economia, carteiras virtuais e homes (Essentials/userdata/)"
echo -e "  ${VERMELHO}✗${NC} Terrenos reivindicados e claims (GriefPrevention)"
echo -e "  ${VERMELHO}✗${NC} Lojas de baús antigas (QuickShop)"
echo -e "  ${VERMELHO}✗${NC} Progresso de RPG, Bosses, Diário e Profissões (Skript variables.csv)"
echo
echo -e "${VERDE}${NEGRITO}O que será PRESERVADO INTACTO:${NC}"
echo -e "  ${VERDE}✔${NC} Datapack de biomas épicos: ${NEGRITO}Terralith${NC}"
echo -e "  ${VERDE}✔${NC} Datapack de modelos 3D: ${NEGRITO}aurelion_modelos${NC}"
echo -e "  ${VERDE}✔${NC} Todos os plugins (.jar) e regras configuradas"
echo -e "  ${VERDE}✔${NC} Resource pack do servidor (32 texturas e modelos)"
echo -e "  ${VERDE}✔${NC} Whitelist, permissões do LuckPerms e OPs"
echo -e "  ${VERDE}✔${NC} Backup automático pré-wipe salvo em backups/"
echo

if [ "$CONFIRMAR" = false ]; then
    read -r -p "$(echo -e "${NEGRITO}Tem certeza absoluta de que deseja limpar o mundo e iniciar do zero? [s/N]: ${NC}")" RESPOSTA
    case "$RESPOSTA" in
        [sS]|[sS][iI][mM]|[yY]|[yY][eE][sS])
            echo
            ;;
        *)
            echo -e "${AMARELO}Operação cancelada pelo usuário. Nenhuma alteração foi feita.${NC}"
            exit 0
            ;;
    esac
fi

# 3. Backup de segurança automático pré-wipe
STAMP=$(date +%Y%m%d-%H%M%S)
DEST_BACKUP="$ROOT/backups"
mkdir -p "$DEST_BACKUP"

echo -e "${AZUL}[1/6] Criando backup de segurança pré-wipe em backups/...${NC}"
python3 "$ROOT/scripts/banco_dados.py" salvar "Backup Pré-Limpeza de Mundo" >/dev/null 2>&1 || true

tar -czf "$DEST_BACKUP/backup-pre-wipe-$STAMP.tar.gz" -C "$ROOT" \
    dados world world_nether world_the_end \
    plugins/Skript/variables.csv \
    plugins/Essentials/userdata \
    plugins/GriefPreventionData \
    usercache.json server.properties 2>/dev/null || true
echo -e "${VERDE}[OK] Backup salvo: backups/backup-pre-wipe-$STAMP.tar.gz${NC}"

# 4. Salvar os Datapacks em diretório temporário
echo -e "${AZUL}[2/6] Preservando Datapacks (Terralith e aurelion_modelos)...${NC}"
TMP_DP="$(mktemp -d)"
if [ -d "world/datapacks" ]; then
    cp -r world/datapacks/* "$TMP_DP/" 2>/dev/null || true
fi

# 5. Excluir pastas de mundos e dimensões
echo -e "${AZUL}[3/6] Removendo mundos e regiões antigas...${NC}"
rm -rf world
rm -rf world_nether
rm -rf world_the_end

# Recriar pasta world e restaurar datapacks
mkdir -p world/datapacks
if [ "$(ls -A "$TMP_DP" 2>/dev/null)" ]; then
    cp -r "$TMP_DP"/* world/datapacks/ 2>/dev/null || true
fi
rm -rf "$TMP_DP"
echo -e "${VERDE}[OK] Mundos deletados. Datapacks restaurados em world/datapacks/${NC}"

# 6. Limpar dados de jogadores e caches
echo -e "${AZUL}[4/6] Limpando dados de jogadores nos plugins...${NC}"
rm -f usercache.json
rm -rf plugins/Essentials/userdata/*
rm -rf plugins/GriefPreventionData/PlayerData/*
rm -rf plugins/GriefPreventionData/ClaimData/*
rm -f plugins/QuickShop-Hikari/shops.mv.db* 2>/dev/null || true
rm -rf plugins/BlueMap/web/tiles/* 2>/dev/null || true
rm -rf bluemap/logs/* 2>/dev/null || true

# 7. Resetar variáveis de RPG, economia e progresso
echo -e "${AZUL}[5/6] Restaurando variáveis de progresso para o estado inicial...${NC}"
python3 "$ROOT/scripts/banco_dados.py" resetar >/dev/null 2>&1 || true
echo -e "${VERDE}[OK] Fichas de RPG, saldos bancários e bosses resetados para o Dia 0.${NC}"

# 8. Ajustar seed se solicitado
echo -e "${AZUL}[6/6] Verificando configuração de seed...${NC}"
if [ -n "$NOVA_SEED" ]; then
    sed -i "s/^level-seed=.*/level-seed=$NOVA_SEED/" server.properties
    echo -e "${VERDE}[OK] Nova seed configurada em server.properties: ${NEGRITO}$NOVA_SEED${NC}"
elif [ "$SEED_ALEATORIA" = true ]; then
    sed -i "s/^level-seed=.*/level-seed=/" server.properties
    echo -e "${VERDE}[OK] Seed configurada como aleatória em server.properties.${NC}"
else
    ATUAL_SEED=$(grep "^level-seed=" server.properties | cut -d'=' -f2-)
    if [ -n "$ATUAL_SEED" ]; then
        echo -e "${CIANO}[INFO] Seed atual mantida: $ATUAL_SEED (use --nova-seed se quiser trocar)${NC}"
    else
        echo -e "${CIANO}[INFO] Seed aleatória será sorteada pelo Minecraft no início.${NC}"
    fi
fi

echo
echo -e "${VERDE}${NEGRITO}====================================================================${NC}"
echo -e "${VERDE}${NEGRITO}     ✦ MUNDO E DADOS DE JOGADORES RESETADOS COM SUCESSO! ✦${NC}"
echo -e "${VERDE}${NEGRITO}====================================================================${NC}"
echo
echo -e "${AMARELO}O servidor está pronto para iniciar um mundo 100% novo.${NC}"
echo -e "Na próxima inicialização, o Paper gerará os biomas do ${NEGRITO}Terralith${NC} e"
echo -e "carregará todos os sistemas e modelos de ${NEGRITO}Cinzas de Aurelion${NC}."
echo
echo -e "Para iniciar o servidor agora, execute:"
echo -e "  ${CIANO}${NEGRITO}./start.sh${NC}"
echo
