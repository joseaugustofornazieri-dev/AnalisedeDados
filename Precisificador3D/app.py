import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Precificador 3D",
    page_icon="🖨️",
    layout="wide",
)

# ----------------------------
# Funções de cálculo
# ----------------------------
def dinheiro(valor: float) -> str:
    """Formata valores no padrão brasileiro."""
    texto = f"R$ {valor:,.2f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def calcular_precificacao(
    peso_g,
    preco_kg,
    desperdicio_pct,
    horas_impressao,
    consumo_w,
    tarifa_kwh,
    custo_maquina_hora,
    minutos_preparacao,
    minutos_acabamento,
    valor_hora_mao_obra,
    outros_custos,
    margem_pct,
    impostos_pct,
    taxas_venda_pct,
):
    # Filamento com acréscimo para suportes, purga e possíveis perdas.
    peso_com_perda = peso_g * (1 + desperdicio_pct / 100)
    custo_filamento = (peso_com_perda / 1000) * preco_kg

    # Energia: potência em watts convertida para kW.
    custo_energia = (consumo_w / 1000) * horas_impressao * tarifa_kwh

    # Reserva para manutenção, desgaste e depreciação da impressora.
    custo_uso_maquina = horas_impressao * custo_maquina_hora

    # Mão de obra: preparação e acabamento são informados em minutos.
    horas_mao_obra = (minutos_preparacao + minutos_acabamento) / 60
    custo_mao_obra = horas_mao_obra * valor_hora_mao_obra

    custo_total = (
        custo_filamento
        + custo_energia
        + custo_uso_maquina
        + custo_mao_obra
        + outros_custos
    )

    # Impostos e taxas são considerados percentuais do preço de venda.
    percentual_disponivel = 1 - (margem_pct + impostos_pct + taxas_venda_pct) / 100

    if percentual_disponivel <= 0:
        return {
            "erro": (
                "A soma da margem desejada, dos impostos e das taxas precisa ser "
                "menor que 100%. Reduza um ou mais percentuais."
            )
        }

    preco_sugerido = custo_total / percentual_disponivel
    valor_impostos = preco_sugerido * impostos_pct / 100
    valor_taxas = preco_sugerido * taxas_venda_pct / 100
    lucro_estimado = preco_sugerido - custo_total - valor_impostos - valor_taxas
    margem_real = (lucro_estimado / preco_sugerido * 100) if preco_sugerido else 0

    return {
        "peso_com_perda": peso_com_perda,
        "custo_filamento": custo_filamento,
        "custo_energia": custo_energia,
        "custo_uso_maquina": custo_uso_maquina,
        "horas_mao_obra": horas_mao_obra,
        "custo_mao_obra": custo_mao_obra,
        "outros_custos": outros_custos,
        "custo_total": custo_total,
        "preco_sugerido": preco_sugerido,
        "valor_impostos": valor_impostos,
        "valor_taxas": valor_taxas,
        "lucro_estimado": lucro_estimado,
        "margem_real": margem_real,
    }


# ----------------------------
# Interface
# ----------------------------
st.title("🖨️ Precificador de Impressão 3D")
st.caption(
    "Calcule o custo de produção e encontre um preço de venda que cubra "
    "filamento, energia, máquina, mão de obra e demais despesas."
)

with st.sidebar:
    st.header("⚙️ Configurações")
    st.write("Informe os custos que você costuma utilizar.")
    st.info(
        "Os valores iniciais são exemplos. Troque-os pelos valores reais da "
        "sua impressora, da sua região e do seu negócio."
    )

    preco_kg = st.number_input(
        "Preço do filamento (R$/kg)", min_value=0.0, value=90.0, step=5.0
    )
    desperdicio_pct = st.number_input(
        "Perda/desperdício do filamento (%)",
        min_value=0.0,
        max_value=300.0,
        value=10.0,
        step=1.0,
    )
    consumo_w = st.number_input(
        "Consumo médio da impressora (W)",
        min_value=0.0,
        value=150.0,
        step=10.0,
    )
    tarifa_kwh = st.number_input(
        "Energia elétrica (R$/kWh)", min_value=0.0, value=0.95, step=0.05
    )
    custo_maquina_hora = st.number_input(
        "Manutenção e desgaste (R$/hora de impressão)",
        min_value=0.0,
        value=1.50,
        step=0.25,
        help="Reserva por hora para manutenção, peças e depreciação da impressora.",
    )
    valor_hora_mao_obra = st.number_input(
        "Valor da sua mão de obra (R$/hora)",
        min_value=0.0,
        value=25.0,
        step=5.0,
    )
    impostos_pct = st.number_input(
        "Impostos estimados sobre a venda (%)",
        min_value=0.0,
        max_value=99.0,
        value=0.0,
        step=0.5,
        help="Use o percentual efetivo aplicável ao seu negócio. Se não souber, deixe 0 e confirme com seu contador.",
    )
    taxas_venda_pct = st.number_input(
        "Taxas de pagamento/plataforma (%)",
        min_value=0.0,
        max_value=99.0,
        value=0.0,
        step=0.5,
        help="Ex.: taxa de cartão ou marketplace, calculada sobre o preço de venda.",
    )

tab_calculo, tab_simulacao, tab_ajuda = st.tabs(
    ["🧮 Calcular preço", "📊 Simular margens", "ℹ️ Como usar"]
)

with tab_calculo:
    st.subheader("1. Dados da peça")
    col1, col2, col3 = st.columns(3)

    with col1:
        nome_peca = st.text_input("Nome da peça", value="Minha peça 3D")
        peso_g = st.number_input(
            "Filamento usado (gramas)",
            min_value=0.0,
            value=100.0,
            step=5.0,
        )
    with col2:
        horas_impressao = st.number_input(
            "Tempo de impressão (horas)",
            min_value=0.0,
            value=5.0,
            step=0.5,
            help="Informe o tempo total de máquina, incluindo impressões que façam parte da mesma peça.",
        )
        margem_pct = st.number_input(
            "Margem de lucro desejada (%)",
            min_value=0.0,
            max_value=99.0,
            value=30.0,
            step=1.0,
            help="É a porcentagem do preço de venda que você deseja manter como lucro após os custos, impostos e taxas informados.",
        )
    with col3:
        outros_custos = st.number_input(
            "Outros custos por peça (R$)",
            min_value=0.0,
            value=3.0,
            step=1.0,
            help="Inclua embalagem, cola, pintura, insertos, ímãs e outros materiais.",
        )
        quantidade = st.number_input(
            "Quantidade de peças iguais",
            min_value=1,
            value=1,
            step=1,
            help="Os resultados unitários são calculados para cada peça. Use para estimar o total do pedido.",
        )

    st.subheader("2. Mão de obra")
    col4, col5 = st.columns(2)
    with col4:
        minutos_preparacao = st.number_input(
            "Preparação e configuração (minutos)",
            min_value=0,
            value=10,
            step=5,
            help="Ex.: fatiar o arquivo, preparar a mesa e iniciar a impressão.",
        )
    with col5:
        minutos_acabamento = st.number_input(
            "Acabamento por peça (minutos)",
            min_value=0,
            value=15,
            step=5,
            help="Ex.: retirar suportes, lixar, limpar e embalar.",
        )

    resultado = calcular_precificacao(
        peso_g=peso_g,
        preco_kg=preco_kg,
        desperdicio_pct=desperdicio_pct,
        horas_impressao=horas_impressao,
        consumo_w=consumo_w,
        tarifa_kwh=tarifa_kwh,
        custo_maquina_hora=custo_maquina_hora,
        minutos_preparacao=minutos_preparacao,
        minutos_acabamento=minutos_acabamento,
        valor_hora_mao_obra=valor_hora_mao_obra,
        outros_custos=outros_custos,
        margem_pct=margem_pct,
        impostos_pct=impostos_pct,
        taxas_venda_pct=taxas_venda_pct,
    )

    st.divider()

    if "erro" in resultado:
        st.error(resultado["erro"])
    else:
        st.subheader(f"3. Resultado — {nome_peca or 'Peça sem nome'}")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Custo total unitário", dinheiro(resultado["custo_total"]))
        m2.metric("Preço de venda sugerido", dinheiro(resultado["preco_sugerido"]))
        m3.metric("Lucro estimado por peça", dinheiro(resultado["lucro_estimado"]))
        m4.metric("Margem real estimada", f'{resultado["margem_real"]:.1f}%')

        st.subheader("Detalhamento dos custos por peça")
        detalhamento = pd.DataFrame(
            [
                ["Filamento (com desperdício)", resultado["custo_filamento"]],
                ["Energia elétrica", resultado["custo_energia"]],
                ["Uso, manutenção e desgaste da máquina", resultado["custo_uso_maquina"]],
                ["Mão de obra", resultado["custo_mao_obra"]],
                ["Outros custos", resultado["outros_custos"]],
                ["CUSTO TOTAL", resultado["custo_total"]],
                ["Impostos estimados sobre a venda", resultado["valor_impostos"]],
                ["Taxas de pagamento/plataforma", resultado["valor_taxas"]],
                ["Lucro estimado", resultado["lucro_estimado"]],
            ],
            columns=["Item", "Valor (R$)"],
        )
        st.dataframe(
            detalhamento.style.format({"Valor (R$)": "R$ {:.2f}"}),
            use_container_width=True,
            hide_index=True,
        )

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Filamento com perda", f'{resultado["peso_com_perda"]:.1f} g')
        col_b.metric("Mão de obra total", f'{resultado["horas_mao_obra"]:.2f} h')
        col_c.metric(
            "Custo por hora de impressão",
            dinheiro(
                (resultado["custo_total"] / horas_impressao)
                if horas_impressao > 0
                else 0
            ),
        )

        st.subheader("Resumo do pedido")
        resumo = pd.DataFrame(
            [
                ["Peça", nome_peca or "Peça sem nome"],
                ["Quantidade", quantidade],
                ["Custo total do pedido", dinheiro(resultado["custo_total"] * quantidade)],
                ["Valor sugerido do pedido", dinheiro(resultado["preco_sugerido"] * quantidade)],
                ["Lucro estimado do pedido", dinheiro(resultado["lucro_estimado"] * quantidade)],
            ],
            columns=["Descrição", "Resultado"],
        )
        st.dataframe(resumo, use_container_width=True, hide_index=True)

        csv = detalhamento.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Baixar detalhamento dos custos (CSV)",
            data=csv,
            file_name="precificacao_impressao_3d.csv",
            mime="text/csv",
        )

        st.caption(
            "Estimativa gerencial, não uma garantia de lucro. Confira os custos reais, "
            "o regime tributário, as taxas de venda e o preço praticado no mercado."
        )

with tab_simulacao:
    st.subheader("Compare preços com diferentes margens")
    st.write(
        "A simulação usa os dados e os custos preenchidos na aba **Calcular preço**."
    )

    if "erro" in resultado:
        st.error(resultado["erro"])
    else:
        margens = [10, 15, 20, 25, 30, 35, 40, 50]
        linhas = []
        for margem in margens:
            sim = calcular_precificacao(
                peso_g=peso_g,
                preco_kg=preco_kg,
                desperdicio_pct=desperdicio_pct,
                horas_impressao=horas_impressao,
                consumo_w=consumo_w,
                tarifa_kwh=tarifa_kwh,
                custo_maquina_hora=custo_maquina_hora,
                minutos_preparacao=minutos_preparacao,
                minutos_acabamento=minutos_acabamento,
                valor_hora_mao_obra=valor_hora_mao_obra,
                outros_custos=outros_custos,
                margem_pct=margem,
                impostos_pct=impostos_pct,
                taxas_venda_pct=taxas_venda_pct,
            )
            if "erro" not in sim:
                linhas.append(
                    {
                        "Margem desejada (%)": margem,
                        "Preço sugerido (R$)": sim["preco_sugerido"],
                        "Lucro estimado (R$)": sim["lucro_estimado"],
                    }
                )

        if linhas:
            simulacao_df = pd.DataFrame(linhas)
            st.dataframe(
                simulacao_df.style.format(
                    {
                        "Preço sugerido (R$)": "R$ {:.2f}",
                        "Lucro estimado (R$)": "R$ {:.2f}",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )
            st.bar_chart(
                simulacao_df.set_index("Margem desejada (%)")[["Preço sugerido (R$)"]]
            )

with tab_ajuda:
    st.subheader("Como preencher corretamente")
    st.markdown(
        """
        1. **Filamento:** informe o peso usado na peça e o preço pago por quilo.
        2. **Desperdício:** considere suportes, brim, purga e falhas. O percentual é aplicado ao peso informado.
        3. **Energia:** use o consumo médio real da impressora em watts e a tarifa da conta de luz em R$/kWh.
        4. **Manutenção e desgaste:** reserve um valor por hora para bicos, mesa, correias, manutenção e depreciação.
        5. **Mão de obra:** inclua preparação, retirada de suportes, acabamento e embalagem. O valor da hora é aplicado ao tempo informado.
        6. **Outros custos:** inclua itens consumíveis que não estejam no custo do filamento.
        7. **Impostos e taxas:** informe os percentuais efetivos que incidem sobre a venda, se aplicáveis.
        8. **Margem de lucro:** é calculada sobre o preço de venda, depois dos custos, impostos e taxas informados.

        **Fórmula do preço sugerido**

        `Preço = Custo total ÷ (1 − margem − impostos − taxas)`

        Os percentuais da fórmula devem ser convertidos para decimal. Por exemplo, 30% = 0,30.
        """
    )
    st.warning(
        "Não confunda margem com acréscimo sobre o custo. Para ter 30% de margem, "
        "divida o custo pela parcela restante do preço (0,70), antes de considerar "
        "impostos e taxas. Isso é diferente de simplesmente acrescentar 30% ao custo."
    )

st.sidebar.divider()
st.sidebar.caption("Precificador 3D • Python + Streamlit")
