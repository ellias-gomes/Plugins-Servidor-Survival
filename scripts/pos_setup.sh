#!/usr/bin/env bash
# ============================================================================
#  PÓS-SETUP: Ajustes finos de economia e mundo nas configs dos plugins.
#  RODE UMA VEZ após a 1ª inicialização (quando as pastas dos plugins forem geradas)
#  e com o servidor PARADO. Depois inicie novamente.
# ============================================================================
cd "$(dirname "$0")/.." || exit 1
P=plugins

patch() { # arquivo regex_sed descricao
  if [ -f "$1" ]; then
    sed -i -E "$2" "$1" && echo "[OK] $3"
  else
    echo "[PULADO] $1 ainda não existe (inicie o servidor uma vez para gerar as pastas)"
  fi
}

# EssentialsX: saldo inicial, símbolo da moeda e sem saldo negativo
patch $P/Essentials/config.yml 's/^starting-balance:.*/starting-balance: 500/' "Essentials: saldo inicial 500"
patch $P/Essentials/config.yml 's/^currency-symbol:.*/currency-symbol: "⛁"/' "Essentials: símbolo da moeda ⛁"
patch $P/Essentials/config.yml 's/^min-money:.*/min-money: 0/' "Essentials: sem saldo negativo"

# DynamicShop: taxa de venda ao servidor ajustada para 15% (padrão 30) e ativação de inflação
patch $P/DynamicShop/config.yml 's/^(\s*)sell_tax_percent:.*/\1sell_tax_percent: 15/' "DynamicShop: margem de venda 15%"
patch $P/DynamicShop/config.yml 's/^(\s*)use-time-inflation:.*/\1use-time-inflation: true/' "DynamicShop: inflação temporal ativada"

# QuickShop-Hikari: taxa básica de 5% sobre transações de jogadores
patch $P/QuickShop-Hikari/config.yml 's/^(\s*)rate: 0\.05/\1rate: 0.05/' "QuickShop: imposto de transação 5%"

# GriefPrevention: blocos iniciais para novos jogadores (2000 blocos)
patch $P/GriefPreventionData/config.yml 's/InitialBlocks: [0-9]+/InitialBlocks: 2000/' "GriefPrevention: 2000 blocos iniciais de claim"

echo ">> Pós-setup concluído com sucesso!"
