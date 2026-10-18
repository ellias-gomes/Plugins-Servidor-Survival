# Sistema Econômico Dinâmico & Comércio

## Moedas
- **Ouro de Aurelion** (virtual, EssentialsX/Vault): saldo padrão inicial de 500.
- **Moedas Físicas de Aurelion**:
  - `Moeda de Aurelion` (1 Ouro): pepita de ouro cunhada.
  - `Lingote Real de Aurelion` (100 Ouros): lingote com selo imperial.
  - Comandos: `/moeda sacar <qtd>` e `/moeda depositar`. Clicar com o botão direito com a moeda na mão deposita instantaneamente na conta virtual!
- **Câmbio com Villagers (Aldeões)**:
  - Aldeões mantêm o comércio tradicional em Esmeraldas, mas a economia está 100% conectada através do **Câmbio Real Imperial**:
    - `/cambio comprar <qtd>`: compra Esmeraldas usando seu Ouro de Aurelion.
    - `/cambio vender <qtd>`: vende Esmeraldas agrícolas/mineradas e recebe Ouro de Aurelion.
    - Segurar **Shift + Botão Direito** em qualquer aldeão abre o menu de câmbio rápido no local!
- **Fragmentos Rúnicos** (dropados exclusivamente de Guardiões e Caçadas): `/runas`. Usados para itens místicos, livros raros e ovos de pet.

## Explicação das Lojas no Jogo (`/lojas`)
1. **Mercado Central Dinâmico (`/shop` e `/sell`)**:
   - Administrado pelo reino com oferta e demanda em tempo real (DynamicShop).
   - Comprar itens repetidamente faz o preço subir; vender itens em massa faz o preço cair.
   - Use `/sell` para vender o item da mão ou `/sell gui` para abrir um baú de venda rápida.
2. **Lojas Privadas de Jogador (`/qs` - QuickShop-Hikari)**:
   - Permite que o Pedro e o Ellias comercializem materiais entre si na vila.
   - **Como criar:**
     1. Coloque um Baú no chão.
     2. Segure o item que deseja vender e bata no baú com ele na mão.
     3. Digite o preço unitário no chat.
     4. Abasteça o baú com os itens.
   - Cada transação recolhe **5% de imposto** para o Tesouro do Reino.

## Fontes de Renda (Faucets)
- **Ofícios e Profissões**: Mineração de minérios, corte de madeira e caça de monstros pagam ouro a cada ação. Salários **não** sobem com a inflação (o poder de compra cai se a inflação disparar).
- **Cartografia**: +150 Ouros a cada bioma inédito descoberto no Terralith.
- **Caçadas e Semi-Bosses**: 1.500 Ouros por foragido derrotado (`/cacadas`).
- **Guardiões e Diário de Bordo**: Grandes somas de ouro e runas por objetivo concluído.
- **Banco de Aurelion**: Juros compostos diários.

## Sumidouros (Sinks) e Tributação
| Tributo / Serviço | Alíquota / Custo |
|---|---|
| Imposto sobre lojas de jogadores (QuickShop) | 5% |
| Margem de câmbio com Villagers | 15% |
| Margem de venda ao servidor (DynamicShop) | 15% |
| Imposto de Renda sobre rendimentos do Banco | 10% |
| Taxa de custódia diária do Banco | 0,1% sobre o depósito |
| Imposto sobre Grandes Fortunas | 0,5%/dia sobre o que ultrapassa 100.000 Ouros na carteira |
| Taxa de Resgate da Lápide | 4% do saldo (reduz até 2% com bosses derrotados) |
| Upgrade do Banco (Nível 2 e 3) | 5.000 Ouros (nv. 2) / 25.000 Ouros (nv. 3) |

## Inflação Automática Diária (`economia.sk`)
A cada 24 horas reais:
1. `massa_total` = carteiras + depósitos no banco.
2. `meta` = 5.000 + 20.000 x bosses derrotados + 3.000 x dias de servidor.
3. Se `massa / meta > 1.1` ➔ Preços sobem +2% e juros do Banco sobem +0,05 (política monetária restritiva).
4. Se `massa / meta < 0.9` ➔ Preços caem -1% e juros do Banco caem -0,03.
5. A cada 7 dias, sorteia um evento econômico com duração de 3 dias (Colheita Farta, Guerra, Corrida do Ouro, etc.).
