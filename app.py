import streamlit as st
import pandas as pd
import itertools
import io

st.set_page_config(page_title="Comparador de Preços", layout="wide")

st.title("🏗️ Comparador Inteligente de Materiais")

# Upload
st.sidebar.header("📁 Upload de Arquivos")
lista_file = st.sidebar.file_uploader("Lista de compra (CSV)", type="csv")
precos_file = st.sidebar.file_uploader("Banco de preços (CSV)", type="csv")
frete_file = st.sidebar.file_uploader("Fretes (CSV)", type="csv")

# Estado
if "resultado" not in st.session_state:
    st.session_state["resultado"] = None

# Função
def melhor_combinacao(lista, precos, fretes):
    lojas = precos["loja"].unique()
    melhor_total = float("inf")
    melhor_resultado = None
    melhor_detalhe = []

    for r in range(1, len(lojas) + 1):
        for combinacao in itertools.combinations(lojas, r):

            total = 0
            detalhe = []
            lojas_usadas = set()

            for _, row in lista.iterrows():
                item = row["nome do item"]
                qtd = row["quantitativo"]

                dados_item = precos[
                    (precos["item"] == item) &
                    (precos["loja"].isin(combinacao))
                ]

                if dados_item.empty:
                    total = float("inf")
                    break

                melhor = dados_item.loc[dados_item["preco"].idxmin()]
                subtotal = melhor["preco"] * qtd

                total += subtotal
                lojas_usadas.add(melhor["loja"])

                detalhe.append({
                    "Item": item,
                    "Quantidade": qtd,
                    "Loja": melhor["loja"],
                    "Preço": melhor["preco"],
                    "Subtotal": subtotal
                })

            for loja in lojas_usadas:
                total += fretes.get(loja, 0)

            if total < melhor_total:
                melhor_total = total
                melhor_resultado = combinacao
                melhor_detalhe = detalhe

    return melhor_resultado, melhor_total, pd.DataFrame(melhor_detalhe)


# Execução
if lista_file and precos_file and frete_file:
    lista = pd.read_csv(lista_file)
    precos = pd.read_csv(precos_file)
    fretes_df = pd.read_csv(frete_file)

    fretes = dict(zip(fretes_df["loja"], fretes_df["frete"]))

    st.subheader("📋 Lista de Compra")
    st.dataframe(lista)

    st.subheader("💰 Banco de Preços")
    st.dataframe(precos)

    st.subheader("🚚 Fretes")
    st.dataframe(fretes_df)

    if st.button("🧠 Calcular melhor combinação"):
        st.session_state["resultado"] = melhor_combinacao(lista, precos, fretes)

        if st.session_state["resultado"] is not None:
            lojas, total, detalhe_df = st.session_state["resultado"]

            st.subheader("🏆 Melhor combinação de lojas")
            st.write(lojas)

            st.subheader("📊 Detalhamento da compra")
            st.dataframe(detalhe_df)

            st.success(f"💰 Custo total otimizado: R$ {total:,.2f}")

            output = io.StringIO()

        for loja in detalhe_df["Loja"].unique():
            df_loja = detalhe_df[detalhe_df["Loja"] == loja].copy()
            total_loja = df_loja["Subtotal"].sum()

            output.write(f"=== {loja} ===\n")
            df_loja.to_csv(output, index=False, sep=";")

            output.write(f"TOTAL;;;;{total_loja}\n\n")

        csv_data = output.getvalue().encode("utf-8-sig")

        st.download_button(
            "📥 Baixar resultado por loja (CSV)",
            data=csv_data,
            file_name="resultado_por_loja.csv",
            mime="text/csv"
        )

else:
    st.info("⬅️ Faça upload dos três arquivos CSV para começar")

st.markdown("---")
st.caption("Sistema inteligente de comparação de preços para obras")