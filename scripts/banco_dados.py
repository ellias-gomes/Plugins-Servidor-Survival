#!/usr/bin/env python3
"""
Gerenciador do Banco de Dados SQLite (dados/aurelion.db) e Reset de Avanço
Servidor: Cinzas de Aurelion (Minecraft 26.3)

Comandos:
  python3 scripts/banco_dados.py salvar [motivo]     - Sincroniza tudo para dados/aurelion.db e cria snapshot
  python3 scripts/banco_dados.py status              - Exibe relatório completo do banco de dados SQLite
  python3 scripts/banco_dados.py resetar             - Faz backup no SQLite e reseta todo o avanço do mapa
  python3 scripts/banco_dados.py restaurar [id]      - Restaura o avanço a partir de um snapshot do SQLite
"""

import datetime
import glob
import json
import os
import re
import sqlite3
import struct
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_DIR = os.path.join(ROOT, "dados")
DB_PATH = os.path.join(DB_DIR, "aurelion.db")
VARS_CSV = os.path.join(ROOT, "plugins", "Skript", "variables.csv")
USERCACHE = os.path.join(ROOT, "usercache.json")
ESS_USERDATA = os.path.join(ROOT, "plugins", "Essentials", "userdata")

BOSS_NAMES = {
    1: "Verdelith, o Guardião do Musgo",
    2: "Thalassa, Rainha das Marés",
    3: "Korvan, o Ferreiro Caído",
    4: "Seraphel, o Oráculo Quebrado",
    5: "O Eclipse",
}


def decode_skript_value(vtype: str, hexval: str):
    vtype = vtype.strip()
    hexval = hexval.strip()
    try:
        if vtype == "boolean":
            return hexval == "01"
        if vtype == "long":
            return struct.unpack(">q", bytes.fromhex(hexval))[0]
        if vtype == "double":
            return round(struct.unpack(">d", bytes.fromhex(hexval))[0], 2)
        if vtype == "string":
            raw = bytes.fromhex(hexval)
            # Skript prefixa strings com tamanho varint/short (geralmente 2 bytes: 80 <len>)
            if len(raw) >= 2 and raw[0] >= 0x80:
                return raw[2:].decode("utf-8", errors="replace")
            return raw.decode("utf-8", errors="replace")
    except Exception:
        pass
    return hexval


def parse_variables_csv():
    data = {}
    raw_content = ""
    if not os.path.isfile(VARS_CSV):
        return data, raw_content
    with open(VARS_CSV, "r", encoding="utf-8", errors="replace") as f:
        raw_content = f.read()
    for line in raw_content.splitlines():
        line_s = line.strip()
        if not line_s or line_s.startswith("#"):
            continue
        parts = line_s.split(",", 2)
        if len(parts) != 3:
            continue
        var_name, var_type, var_hex = parts[0].strip(), parts[1].strip(), parts[2].strip()
        data[var_name] = decode_skript_value(var_type, var_hex)
    return data, raw_content


def load_player_names_and_wallets():
    names = {}
    wallets = {}
    if os.path.isfile(USERCACHE):
        try:
            with open(USERCACHE, "r", encoding="utf-8") as f:
                for entry in json.load(f):
                    if "uuid" in entry and "name" in entry:
                        names[entry["uuid"]] = entry["name"]
        except Exception:
            pass
    if os.path.isdir(ESS_USERDATA):
        for yml in glob.glob(os.path.join(ESS_USERDATA, "*.yml")):
            uid = os.path.splitext(os.path.basename(yml))[0]
            try:
                with open(yml, "r", encoding="utf-8", errors="replace") as f:
                    txt = f.read()
                m_name = re.search(r"last-account-name:\s*([^\r\n]+)", txt)
                if m_name:
                    n = m_name.group(1).strip().strip("'\"")
                    if n != "Tax":
                        names[uid] = n
                m_money = re.search(r"money:\s*['\"]?([0-9.\-]+)['\"]?", txt)
                if m_money:
                    wallets[uid] = round(float(m_money.group(1)), 2)
            except Exception:
                pass
    return names, wallets


def init_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS jogadores (
            uuid TEXT PRIMARY KEY,
            nome TEXT,
            carteira REAL DEFAULT 0,
            banco_saldo REAL DEFAULT 0,
            banco_nivel INTEGER DEFAULT 1,
            runas INTEGER DEFAULT 0,
            pets_colecionados INTEGER DEFAULT 0,
            biomas_descobertos INTEGER DEFAULT 0,
            objetivos_feitos INTEGER DEFAULT 0,
            cacadas_feitas INTEGER DEFAULT 0,
            memorias_feitas INTEGER DEFAULT 0,
            voto_final TEXT DEFAULT '',
            atualizado_em TEXT
        );

        CREATE TABLE IF NOT EXISTS economia_estado (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            dia INTEGER DEFAULT 0,
            multiplicador REAL DEFAULT 1.0,
            juro REAL DEFAULT 0.5,
            tesouro REAL DEFAULT 0.0,
            evento_nome TEXT DEFAULT 'Nenhum',
            evento_preco REAL DEFAULT 1.0,
            evento_salario REAL DEFAULT 1.0,
            evento_juro REAL DEFAULT 1.0,
            atualizado_em TEXT
        );

        CREATE TABLE IF NOT EXISTS progresso_bosses (
            boss_id INTEGER PRIMARY KEY,
            nome TEXT,
            derrotado INTEGER DEFAULT 0,
            atualizado_em TEXT
        );

        CREATE TABLE IF NOT EXISTS diario_progresso (
            uuid TEXT,
            objetivo_id INTEGER,
            concluido INTEGER DEFAULT 0,
            PRIMARY KEY (uuid, objetivo_id)
        );

        CREATE TABLE IF NOT EXISTS cacadas_progresso (
            uuid TEXT,
            cacada_id INTEGER,
            concluido INTEGER DEFAULT 0,
            PRIMARY KEY (uuid, cacada_id)
        );

        CREATE TABLE IF NOT EXISTS historico_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            criado_em TEXT,
            motivo TEXT,
            bosses_derrotados INTEGER,
            dia_economico INTEGER,
            tesouro REAL,
            resumo_json TEXT,
            variables_csv_raw TEXT
        );
        """
    )
    conn.commit()
    return conn


def salvar_no_banco(motivo="Salvamento Manual"):
    conn = init_db()
    cur = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sk_vars, raw_csv = parse_variables_csv()
    names, wallets = load_player_names_and_wallets()

    # 1. Economia
    dia = int(sk_vars.get("eco::dia", 0))
    multi = float(sk_vars.get("eco::multi", 1.0))
    juro = float(sk_vars.get("eco::juro", 0.5))
    tesouro = float(sk_vars.get("eco::tesouro", 0.0))
    ev_nome = str(sk_vars.get("eco::evento::nome", "Nenhum"))
    ev_preco = float(sk_vars.get("eco::evento::preco", 1.0))
    ev_sal = float(sk_vars.get("eco::evento::salario", 1.0))
    ev_juro = float(sk_vars.get("eco::evento::juro", 1.0))

    cur.execute(
        """
        INSERT INTO economia_estado (id, dia, multiplicador, juro, tesouro, evento_nome, evento_preco, evento_salario, evento_juro, atualizado_em)
        VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            dia=excluded.dia,
            multiplicador=excluded.multiplicador,
            juro=excluded.juro,
            tesouro=excluded.tesouro,
            evento_nome=excluded.evento_nome,
            evento_preco=excluded.evento_preco,
            evento_salario=excluded.evento_salario,
            evento_juro=excluded.evento_juro,
            atualizado_em=excluded.atualizado_em
        """,
        (dia, multi, juro, tesouro, ev_nome, ev_preco, ev_sal, ev_juro, now_str),
    )

    # 2. Bosses
    bosses_count = 0
    for bid in range(1, 6):
        derrotado = 1 if sk_vars.get(f"prog::boss::{bid}", False) else 0
        bosses_count += derrotado
        cur.execute(
            """
            INSERT INTO progresso_bosses (boss_id, nome, derrotado, atualizado_em)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(boss_id) DO UPDATE SET
                nome=excluded.nome,
                derrotado=excluded.derrotado,
                atualizado_em=excluded.atualizado_em
            """,
            (bid, BOSS_NAMES[bid], derrotado, now_str),
        )

    # 3. Descobrir todos os UUIDs de jogadores reais
    uuids = set(names.keys())
    uuid_pattern = re.compile(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})")
    for k in sk_vars.keys():
        m = uuid_pattern.search(k)
        if m:
            uuids.add(m.group(1))
    # Remove conta de imposto do QuickShop se existir
    uuids = {u for u in uuids if names.get(u, "") != "Tax" and u != "2c5f00ba-902c-411b-b9b9-9261cf43aee1"}

    cur.execute("DELETE FROM diario_progresso")
    cur.execute("DELETE FROM cacadas_progresso")

    jogadores_resumo = []
    for uid in sorted(uuids):
        nome = str(sk_vars.get(f"db::jogador::{uid}::nome", names.get(uid, "Desconhecido")))
        carteira = float(sk_vars.get(f"saldo::{uid}", wallets.get(uid, 0.0)))
        banco_saldo = float(sk_vars.get(f"banco::{uid}", 0.0))
        banco_nivel = int(sk_vars.get(f"banconivel::{uid}", 1))
        runas = int(sk_vars.get(f"runas::{uid}", 0))
        voto_final = str(sk_vars.get(f"final::{uid}", ""))

        pets_cnt = sum(1 for k in sk_vars if k.startswith(f"pets::{uid}::owned::"))
        biomas_cnt = sum(1 for k in sk_vars if k.startswith(f"explo::{uid}::"))
        mem_cnt = sum(1 for i in range(1, 6) if sk_vars.get(f"memoria::{uid}::{i}", False))

        obj_cnt = 0
        for oid in range(1, 11):
            done = 1 if sk_vars.get(f"diario::{uid}::done::{oid}", False) else 0
            obj_cnt += done
            cur.execute("INSERT INTO diario_progresso (uuid, objetivo_id, concluido) VALUES (?, ?, ?)", (uid, oid, done))

        cac_cnt = 0
        for cid in range(1, 5):
            done = 1 if sk_vars.get(f"cacada::done::{uid}::{cid}", False) else 0
            cac_cnt += done
            cur.execute("INSERT INTO cacadas_progresso (uuid, cacada_id, concluido) VALUES (?, ?, ?)", (uid, cid, done))

        cur.execute(
            """
            INSERT INTO jogadores (uuid, nome, carteira, banco_saldo, banco_nivel, runas, pets_colecionados,
                                   biomas_descobertos, objetivos_feitos, cacadas_feitas, memorias_feitas, voto_final, atualizado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(uuid) DO UPDATE SET
                nome=excluded.nome,
                carteira=excluded.carteira,
                banco_saldo=excluded.banco_saldo,
                banco_nivel=excluded.banco_nivel,
                runas=excluded.runas,
                pets_colecionados=excluded.pets_colecionados,
                biomas_descobertos=excluded.biomas_descobertos,
                objetivos_feitos=excluded.objetivos_feitos,
                cacadas_feitas=excluded.cacadas_feitas,
                memorias_feitas=excluded.memorias_feitas,
                voto_final=excluded.voto_final,
                atualizado_em=excluded.atualizado_em
            """,
            (uid, nome, carteira, banco_saldo, banco_nivel, runas, pets_cnt, biomas_cnt, obj_cnt, cac_cnt, mem_cnt, voto_final, now_str),
        )
        jogadores_resumo.append(
            {
                "uuid": uid,
                "nome": nome,
                "carteira": carteira,
                "banco": banco_saldo,
                "runas": runas,
                "objetivos": obj_cnt,
                "cacadas": cac_cnt,
                "pets": pets_cnt,
                "biomas": biomas_cnt,
            }
        )

    resumo = {
        "timestamp": now_str,
        "motivo": motivo,
        "economia": {"dia": dia, "multi": multi, "juro": juro, "tesouro": tesouro, "evento": ev_nome},
        "bosses_derrotados": bosses_count,
        "jogadores": jogadores_resumo,
    }
    cur.execute(
        """
        INSERT INTO historico_snapshots (criado_em, motivo, bosses_derrotados, dia_economico, tesouro, resumo_json, variables_csv_raw)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (now_str, motivo, bosses_count, dia, tesouro, json.dumps(resumo, ensure_ascii=False), raw_csv),
    )
    snap_id = cur.lastrowid
    conn.commit()
    conn.close()
    print(f"[OK] Banco de dados SQLite atualizado em: {DB_PATH}")
    print(f"     Snapshot #{snap_id} gravado ({motivo}) em {now_str}")
    print(f"     Jogadores sincronizados: {len(jogadores_resumo)} | Bosses derrotados: {bosses_count}/5 | Dia Econômico: {dia}")


def mostrar_status():
    conn = init_db()
    cur = conn.cursor()
    print("=== STATUS DO BANCO DE DADOS SQLITE (dados/aurelion.db) ===")
    cur.execute("SELECT dia, multiplicador, juro, tesouro, evento_nome, atualizado_em FROM economia_estado WHERE id=1")
    eco = cur.fetchone()
    if eco:
        print(f"\n[Economia] Dia {eco[0]} | Multiplicador: {eco[1]}x | Juros: {eco[2]}%/dia | Tesouro: {eco[3]} | Evento: {eco[4]} (Atualizado: {eco[5]})")
    else:
        print("\n[Economia] Nenhum registro salvo ainda. Execute: python3 scripts/banco_dados.py salvar")

    print("\n[Guardiões de Aurelion]")
    cur.execute("SELECT boss_id, nome, derrotado FROM progresso_bosses ORDER BY boss_id")
    for row in cur.fetchall():
        st = "DERROTADO" if row[2] else "VIVO (Pendente)"
        print(f"  #{row[0]} {row[1]}: {st}")

    print("\n[Jogadores Registrados]")
    cur.execute(
        "SELECT nome, uuid, carteira, banco_saldo, banco_nivel, runas, objetivos_feitos, cacadas_feitas, pets_colecionados, biomas_descobertos FROM jogadores"
    )
    rows = cur.fetchall()
    if not rows:
        print("  (Nenhum jogador registrado)")
    for r in rows:
        print(f"  • {r[0]} ({r[1]})")
        print(f"    Carteira: {r[2]} | Banco (Nv.{r[4]}): {r[3]} | Runas: {r[5]}")
        print(f"    Diário: {r[6]}/10 | Caçadas Skyrim: {r[7]}/4 | Pets: {r[8]}/11 | Biomas: {r[9]}")

    print("\n[Últimos 5 Snapshots de Restauração]")
    cur.execute("SELECT id, criado_em, motivo, bosses_derrotados, dia_economico, tesouro FROM historico_snapshots ORDER BY id DESC LIMIT 5")
    for s in cur.fetchall():
        print(f"  Snapshot #{s[0]} [{s[1]}] - {s[2]} (Bosses: {s[3]}/5, Dia: {s[4]}, Tesouro: {s[5]})")
    conn.close()


def resetar_avanco():
    # 1. Faz backup do estado atual no SQLite antes de resetar
    salvar_no_banco("Backup Automático Pré-Reset")

    # 2. Reescreve plugins/Skript/variables.csv mantendo apenas o catálogo de pets e economia zerada no Dia 0
    clean_csv = """# === Skript's variable storage ===
# Please do not modify this file manually!
#
# version: 2.17.0

eco::dia, long, 0000000000000000
eco::evento::juro, long, 0000000000000001
eco::evento::nome, string, 80064E656E68756D
eco::evento::preco, long, 0000000000000001
eco::evento::salario, long, 0000000000000001
eco::juro, double, 3FE0000000000000
eco::multi, long, 0000000000000001
eco::tesouro, double, 0000000000000000
petcat::ids::1, string, 800A6C6F626F5F63696E7A61
petcat::ids::2, string, 800A6761746F5F6D7573676F
petcat::ids::3, string, 800D706170616761696F5F72756269
petcat::ids::4, string, 800E6C6F626F5F65737065637472616C
petcat::ids::5, string, 800C6761746F5F6E6F7475726E6F
petcat::ids::6, string, 800C706170616761696F5F736F6C
petcat::ids::7, string, 800D6C6F626F5F666572727567656D
petcat::ids::8, string, 800F6761746F5F74656D70657374616465
petcat::ids::9, string, 800E706170616761696F5F6D61726573
petcat::ids::10, string, 800D6C6F626F5F617572656C696F6E
petcat::ids::11, string, 800C6761746F5F65636C69707365
prog::bosses, long, 0000000000000000
"""
    os.makedirs(os.path.dirname(VARS_CSV), exist_ok=True)
    with open(VARS_CSV, "w", encoding="utf-8") as f:
        f.write(clean_csv)

    # 3. Zera saldo (money) nos arquivos userdata do Essentials
    if os.path.isdir(ESS_USERDATA):
        for yml in glob.glob(os.path.join(ESS_USERDATA, "*.yml")):
            try:
                with open(yml, "r", encoding="utf-8") as f:
                    txt = f.read()
                txt_new = re.sub(r"money:\s*['\"]?[0-9.\-]+['\"]?", "money: '0'", txt)
                with open(yml, "w", encoding="utf-8") as f:
                    f.write(txt_new)
            except Exception:
                pass

    # 4. Atualiza tabelas do SQLite para refletir o estado zerado
    conn = init_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM jogadores")
    cur.execute("DELETE FROM diario_progresso")
    cur.execute("DELETE FROM cacadas_progresso")
    conn.commit()
    conn.close()
    salvar_no_banco("Reset Completo de Avanço")
    print("[OK] Todo o avanço da campanha, bosses, diário, caçadas, memórias, banco e saldos foram zerados!")


def restaurar_snapshot(snap_id: int):
    conn = init_db()
    cur = conn.cursor()
    cur.execute("SELECT criado_em, motivo, variables_csv_raw FROM historico_snapshots WHERE id=?", (snap_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        print(f"[ERRO] Snapshot #{snap_id} não encontrado no banco de dados!")
        sys.exit(1)
    if not row[2]:
        print(f"[ERRO] Snapshot #{snap_id} não possui conteúdo de variables.csv.")
        sys.exit(1)
    with open(VARS_CSV, "w", encoding="utf-8") as f:
        f.write(row[2])
    salvar_no_banco(f"Restaurado do Snapshot #{snap_id}")
    print(f"[OK] Avanço restaurado com sucesso para o Snapshot #{snap_id} ({row[1]} de {row[0]})!")


def main():
    cmd = sys.argv[1].lower() if len(sys.argv) > 1 else "status"
    if cmd in ("salvar", "save", "sync"):
        motivo = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Sincronização Manual CLI"
        salvar_no_banco(motivo)
    elif cmd in ("status", "info", "relatorio"):
        mostrar_status()
    elif cmd in ("resetar", "reset", "zerar"):
        resetar_avanco()
    elif cmd in ("restaurar", "restore"):
        if len(sys.argv) < 3:
            print("Uso: python3 scripts/banco_dados.py restaurar <id_do_snapshot>")
            sys.exit(1)
        restaurar_snapshot(int(sys.argv[2]))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
