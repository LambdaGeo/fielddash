"""Ponto de entrada principal para publicação no Streamlit Community Cloud.

Este script suporta:
1. Controle de acesso restrito à equipe de campo via PIN/Token (configurado no Streamlit Secrets).
2. Acesso facilitado por link direto com parâmetro de URL (?token=SEU_PIN).
3. Resolução flexível da configuração do projeto via segredos ou caminhos padrão.
"""
from pathlib import Path
import os
import streamlit as st

import fielddash
from fielddash.core.env import getenv

# 1. Configuração da página (deve ser a primeira chamada Streamlit)
st.set_page_config(page_title="fielddash", page_icon="📊", layout="wide")


def _check_access() -> bool:
    """Valida o acesso da equipe de campo caso um segredo de acesso esteja configurado."""
    required_pin = (
        getenv("FIELD_ACCESS_PIN")
        or getenv("FIELD_ACCESS_TOKEN")
        or getenv("ACCESS_PIN")
    )

    # Se nenhum PIN foi definido nos segredos, o acesso é livre
    if not required_pin:
        return True

    # 1. Checa se já está autenticado nesta sessão do navegador
    if st.session_state.get("authenticated", False):
        return True

    # 2. Checa se o token veio como parâmetro de URL (ex: ?token=xxx ou ?pin=xxx)
    url_token = st.query_params.get("token") or st.query_params.get("pin") or st.query_params.get("key")
    if url_token and str(url_token).strip() == str(required_pin).strip():
        st.session_state["authenticated"] = True
        return True

    # 3. Exibe tela de autenticação da equipe
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 🔐 Área Restrita — Equipe de Campo")
        st.info(
            "Este painel contém dados de trabalho de campo e coleta. "
            "Por favor, insira o código de acesso fornecido pela coordenação da pesquisa."
        )

        with st.form("login_form"):
            entered_pin = st.text_input("Código de Acesso / PIN:", type="password")
            submitted = st.form_submit_button("Entrar no Dashboard")

            if submitted:
                if entered_pin and entered_pin.strip() == str(required_pin).strip():
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Código de acesso incorreto. Verifique com a equipe responsável.")

    st.stop()
    return False


def _resolve_target() -> str:
    """Identifica o projeto .yaml ou pasta a ser carregada."""
    # 1. Segredo ou variável de ambiente explícita
    target = getenv("FIELDDASH_CONFIG") or getenv("GEOCOLETA_CONFIG")
    if target and Path(target).exists():
        return target

    # 2. Pasta local 'projetos' se tiver arquivos .yaml
    projetos_dir = Path("projetos")
    if projetos_dir.is_dir() and (list(projetos_dir.glob("*.yaml")) or list(projetos_dir.glob("*/*.yaml"))):
        return "projetos"

    # 3. Exemplo incluído com dados anonimizados como fallback seguro
    exemplo_yaml = Path("exemplos/residuos/projeto.yaml")
    if exemplo_yaml.exists():
        return str(exemplo_yaml)

    return "."


def main():
    _check_access()

    # Botão de logout na barra lateral se houver proteção ativa
    has_protection = bool(
        getenv("FIELD_ACCESS_PIN")
        or getenv("FIELD_ACCESS_TOKEN")
        or getenv("ACCESS_PIN")
    )
    if has_protection and st.session_state.get("authenticated", False):
        st.sidebar.caption("🟢 Acesso autorizado (Equipe de Campo)")
        if st.sidebar.button("Encerrar sessão", key="logout_btn"):
            st.session_state["authenticated"] = False
            # Remove parâmetro de token da URL se presente para não relogar automaticamente
            if "token" in st.query_params:
                del st.query_params["token"]
            st.rerun()

    target = _resolve_target()
    fielddash.dashboard(target, configure_page=False)


if __name__ == "__main__":
    main()
