# Stack de plugins (todos verificados com build para 26.3 em 17/10/2026)

| Peça | Versão | Papel |
|---|---|---|
| Paper | 26.3 #202 | Servidor |
| LuckPerms | 5.5.71 | Permissões (grupos `jogador` e `admin`) |
| VaultUnlocked | 2.20.3 | API de economia entre plugins |
| EssentialsX (+Spawn) | 2.22.0 | Carteira ("Ouro de Aurelion"), homes, tpa, /pay |
| GriefPrevention | 16.18.7 | Terrenos (proteja a construção do Pedro) |
| DynamicShop | 3.0.7 | `/shop` com oferta/demanda e inflação por escassez |
| QuickShop-Hikari | 6.3.0.3 | Lojas de jogadores (`/qs`), imposto 5% |
| Skript | 2.17.0 | Toda a lógica customizada (veja abaixo) |
| Chunky, BlueMap, PlaceholderAPI | - | Pré-geração, mapa web, placeholders |
| Terralith | 2.6.5+26.3 | Datapack de biomas (novo mundo) |
| CraftEngine (opcional) | 26.9.2 | Móveis/decoração para o Ellias - em `plugins/_opcional/` |

## Por que Skript em vez de MythicMobs/MMOItems/AngelChest/EcoPets...
Na data da pesquisa esses plugins **não tinham build para 26.3** no Modrinth (alguns são pagos no Spigot). Para não depender de jars incompatíveis, as funções foram implementadas em Skript, o que também permite integração total com a economia:

| Script | Função |
|---|---|
| `economia.sk` | Inflação, juros dinâmicos, impostos, eventos, painel `/economia` |
| `banco.sk` | Banco com níveis e rendimento diário |
| `lapide.sk` | Lápide sem perda de itens + taxa de resgate (Pedro) |
| `itens.sk` | 10 Relíquias de Aurelion + conjunto "Fio de Ouro" com bônus |
| `bosses.sk` | 5 Guardiões, arenas, ondas, fases, drops |
| `progressao.sk` | Runas, pets colecionáveis, ofícios (salários), cartografia |
| `diario.sk` | Diário de Bordo (10 objetivos, GUI) |
| `lore.sk` | Prólogo em livro escrito (`written_book`), `/lore`, `/memorias`, `/mentor`, `/final` |
| `skyrim.sk` | 5 Feitiços/Shouts ativáveis, 4 Armas Únicas e 4 Semi-Bosses de Caçada (`/cacadas`) |
| `modelos.sk` + `aurelion_modelos` | 12 Modelos 3D articulados (`block_display`) com 7 poses animadas para Bosses, Semi-Bosses e Pilares |

Se um dia MythicMobs/MMOItems/EcoPets/ModelEngine lançarem build 26.3 você pode migrar mantendo `economia.sk` e `diario.sk`.

## Sinergias
- **Bosses -> Economia:** salário + runas + relíquias; taxa de expedição indexada à inflação vai ao tesouro.
- **Bosses -> Banco:** Thalassa libera nível 2, Seraphel libera nível 3.
- **Bosses -> Lápide:** cada boss derrotado reduz 0,5 pct da taxa (4% -> mínimo 2%).
- **Bosses -> Lore:** primeira vitória desbloqueia uma lembrança (`/memorias`) e um Ovo de Pet.
- **Diário:** lê o progresso de todos os sistemas e paga recompensas.
- **DynamicShop + QuickShop:** mercado do reino e mercado entre jogadores com impostos distintos.

## Perfis atendidos
**Pedro:** lápide (nunca perde itens; só taxa), cartografia (ganha ouro e Ovos de Pet por biomas novos), pets (11 pets, 4 raridades, níveis), armaduras do conjunto Fio de Ouro, dungeons, GriefPrevention, Terralith.
**Ellias:** banco/juros/impostos, `/economia`, lojas, ofícios, armas e ferramentas das relíquias, runas (`/runas`), bosses com mecânicas, decoração (CraftEngine opcional).

## Decoração (CraftEngine, opcional)
1. Mova `plugins/_opcional/craft-engine-*.jar` para `plugins/`.
2. Inicie, leia `plugins/CraftEngine/config.yml` e configure o resource pack (hospedagem própria exige abrir outra porta no túnel; ou use um host externo).
3. Para consumir moeda, venda os itens decorativos em uma loja do DynamicShop (sumidouro de dinheiro).
