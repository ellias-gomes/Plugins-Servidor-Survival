#!/usr/bin/env bash
# Inicia o servidor "Cinzas de Aurelion" (Paper 26.3, Java 25).
cd "$(dirname "$0")" || exit 1
RAM="${RAM:-5G}"   # máquina com 12 GB: 5G é seguro. Aumente para 6G/8G se tiver folga.
while true; do
  python3 scripts/banco_dados.py salvar "Inicializacao do Servidor" 2>/dev/null || true
  java -Xms$RAM -Xmx$RAM -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 \
    -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch \
    -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M \
    -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 \
    -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 \
    -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem \
    -XX:MaxTenuringThreshold=1 -Dusing.aikars.flags=https://mcflags.emc.gs -Daikars.new.flags=true \
    -jar paper.jar --nogui
  python3 scripts/banco_dados.py salvar "Parada do Servidor" 2>/dev/null || true
  echo ">> Servidor parou e dados sincronizados em dados/aurelion.db. Reiniciando em 10s (Ctrl+C para cancelar)..."
  sleep 10
done
