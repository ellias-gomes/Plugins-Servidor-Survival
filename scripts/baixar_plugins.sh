#!/usr/bin/env bash
# Baixa os plugins (compatíveis com Minecraft 26.3) via API do Modrinth / GitHub.
# Uso: ./scripts/baixar_plugins.sh   (rode na raiz do projeto)
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MC="26.3"
mkdir -p "$ROOT/plugins" "$ROOT/world/datapacks"

modrinth() { # slug destino(plugins|datapack)
  local slug="$1" dest="${2:-plugins}" loaders
  if [ "$dest" = "datapack" ]; then loaders='["datapack"]'; else loaders='["paper","bukkit","spigot","purpur"]'; fi
  local json url name
  json=$(curl -s -G "https://api.modrinth.com/v2/project/$slug/version" \
    --data-urlencode "game_versions=[\"$MC\"]" --data-urlencode "loaders=$loaders")
  url=$(echo "$json" | jq -r '.[0].files | (map(select(.primary))[0] // .[0]) | .url // empty')
  name=$(echo "$json" | jq -r '.[0].files | (map(select(.primary))[0] // .[0]) | .filename // empty')
  if [ -z "$url" ]; then echo "[FALHOU] $slug (sem build para $MC)"; return; fi
  local out="$ROOT/plugins"; [ "$dest" = "datapack" ] && out="$ROOT/world/datapacks"
  curl -sL -o "$out/$name" "$url" && echo "[OK] $slug -> $name"
}

# Núcleo
modrinth luckperms
modrinth vaultunlocked
# Proteção / mundo
modrinth griefprevention
modrinth chunky
modrinth bluemap
modrinth placeholderapi
# Economia
modrinth dynamicshop
modrinth quickshop-hikari
# (Lápides, bosses, dungeons, itens, banco, diário e pets são implementados em Skript:
#  plugins/Skript/scripts/*.sk -- nenhum plugin pago/incompatível necessário)
# Scripts (banco, inflação, diário, pets, ofícios)
modrinth skript
# Decoração (Ellias)
modrinth craftengine
mkdir -p "$ROOT/plugins/_opcional" && mv -f "$ROOT"/plugins/craft-engine-*.jar "$ROOT/plugins/_opcional/" 2>/dev/null  # opcional: ver docs/PLUGINS.md
# Mundo (datapack)
modrinth terralith datapack

# EssentialsX (provedor de economia + utilidades) via GitHub
ESS=$(curl -s https://api.github.com/repos/EssentialsX/Essentials/releases/latest | jq -r '.assets[]|select(.name|test("^EssentialsX(-|Spawn-)[0-9]"))|.browser_download_url')
for u in $ESS; do curl -sL -o "$ROOT/plugins/$(basename "$u")" "$u" && echo "[OK] $(basename "$u")"; done
echo "Pronto."
