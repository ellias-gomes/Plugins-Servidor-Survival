#!/usr/bin/env bash
# Aceita o EULA da Mojang (https://aka.ms/MinecraftEULA). Rode SOMENTE se você leu e concorda.
cd "$(dirname "$0")/.." || exit 1
echo "eula=true" > eula.txt && echo "EULA aceito."
