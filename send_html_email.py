#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Envio de e-mails em HTML para destinos definidos em JSON.
- Configurações SMTP em config.json
- Destinos em recipients.json (com grupos)
- Corpo do e-mail em email_template.html (suporta {{name}} opcional)
Uso:
  - Duplo clique (Windows/macOS) ou:  python send_html_email.py
  - Escolha o grupo pelo menu (ex.: clientes, interno, todos)
"""

import json
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent

CONFIG_PATH = HERE / "config.json"
RECIPIENTS_PATH = HERE / "recipients.json"
HTML_TEMPLATE_PATH = HERE / "email_template.html"

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_template(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def normalize_recipients(group_items):
    """
    Aceita itens como strings (emails) ou objetos { "email": "...", "name": "..." }.
    Retorna lista de dicts padronizados: [{email, name?}, ...]
    """
    norm = []
    for item in group_items:
        if isinstance(item, str):
            norm.append({"email": item, "name": None})
        elif isinstance(item, dict):
            email = item.get("email")
            name = item.get("name")
            norm.append({"email": email, "name": name})
        else:
            # ignora formatos desconhecidos
            continue
    # filtra emails válidos
    valids = [r for r in norm if r.get("email") and EMAIL_RE.match(r["email"])]
    return valids

def pick_group(groups):
    print("\n=== Selecione o grupo de destino ===")
    keys = list(groups.keys())
    for i, k in enumerate(keys, start=1):
        print(f"{i}. {k}  ({len(groups[k])} destinatário(s))")
    extra_i = len(keys) + 1
    print(f"{extra_i}. todos  (todos os grupos)")

    while True:
        try:
            choice = input("Digite o número da opção: ").strip()
        except EOFError:
            choice = ""
        if not choice.isdigit():
            print("Opção inválida. Tente novamente.")
            continue
        idx = int(choice)
        if 1 <= idx <= len(keys):
            return keys[idx - 1]
        elif idx == extra_i:
            return "todos"
        else:
            print("Opção inválida. Tente novamente.")

def render_html(html, name):
    if name:
        return html.replace("{{name}}", name)
    else:
        return html.replace("{{name}}", "Gabi")  # padrão, se nome não informado

def main():
    # Carrega config, recipients e template
    if not CONFIG_PATH.exists() or not RECIPIENTS_PATH.exists() or not HTML_TEMPLATE_PATH.exists():
        print("Arquivos necessários não encontrados. Verifique config.json, recipients.json e email_template.html.")
        sys.exit(1)

    config = load_json(CONFIG_PATH)
    recipients_raw = load_json(RECIPIENTS_PATH)
    html_template = load_template(HTML_TEMPLATE_PATH)

    smtp_server = config.get("smtp_server", "smtp.gmail.com")
    smtp_port = int(config.get("smtp_port", 587))
    username = config["username"]
    password = config["password"]
    from_name = config.get("from_name", username)
    subject = config.get("subject", "Aviso automático")

    if not isinstance(recipients_raw, dict):
        print("O arquivo recipients.json deve conter um objeto com grupos.")
        sys.exit(1)

    # Menu de grupo
    selected_group = pick_group(recipients_raw)

    # Monta lista final de destinatários
    if selected_group == "todos":
        all_items = []
        for g, items in recipients_raw.items():
            all_items.extend(items)
        recipients = normalize_recipients(all_items)
    else:
        recipients = normalize_recipients(recipients_raw.get(selected_group, []))

    if not recipients:
        print("Nenhum destinatário válido encontrado para o grupo selecionado.")
        sys.exit(0)

    print(f"\nEnviando para {len(recipients)} destinatário(s)...\n")

    sent_ok = 0
    failed = []

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)

            for r in recipients:
                to_email = r["email"]
                name = r.get("name")

                html_body = render_html(html_template, name)

                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = f"{from_name} <{username}>"
                msg["To"] = to_email

                # Parte texto simples (fallback)
                text_body = "Seu cliente de e-mail não suporta HTML. Mensagem automática."
                part1 = MIMEText(text_body, "plain", "utf-8")
                part2 = MIMEText(html_body, "html", "utf-8")
                msg.attach(part1)
                msg.attach(part2)

                try:
                    server.sendmail(username, [to_email], msg.as_string())
                    print(f"OK  -> {to_email}")
                    sent_ok += 1
                except Exception as e:
                    print(f"ERRO -> {to_email}: {e}")
                    failed.append({"email": to_email, "error": str(e)})
    except Exception as e:
        print(f"Falha ao conectar/enviar via SMTP: {e}")
        sys.exit(2)

    print("\n=== Resumo ===")
    print(f"Enviados com sucesso: {sent_ok}")
    if failed:
        print(f"Falharam ({len(failed)}):")
        for f in failed:
            print(f" - {f['email']}: {f['error']}")

if __name__ == "__main__":
    main()
