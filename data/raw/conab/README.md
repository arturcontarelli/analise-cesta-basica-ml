# Planilhas de custo de produção da CONAB

Nesta pasta ficam as planilhas de custo de produção da CONAB (Companhia Nacional de Abastecimento, órgão federal). Elas informam quanto o agricultor gasta para produzir cada cultura.

**Origem:** https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/custos-de-producao/planilhas-de-custos-de-producao

**Produtos:** só Arroz, Feijão, Café e Leite (decisão 5 em `docs/decisoes.md`; a lista está em `src/config.py` → `PRODUTOS_CONAB`).

## Regras

- Os arquivos são baixados **manualmente** do site acima e salvos aqui **exatamente como vieram**.
- **Não edite os arquivos originais.** Qualquer tratamento (seleção de região, conversão de unidade, alinhamento mensal) é feito pelo código (`src/data_loading.py`, notebook `03_conab.ipynb`), e o resultado vai para `data/processed/`.
- Registre abaixo, para cada arquivo, a data do download e o link exato. Assim qualquer pessoa consegue refazer o trabalho.
- Pela decisão 5, baixe primeiro **só o feijão** e confira frequência (safra ou mês), região e unidade antes de baixar os outros.

## Organização

Uma subpasta por produto (`arroz/`, `feijao/`, depois `cafe/` e `leite/`), com os nomes de arquivo originais.

## Arquivos baixados

| Arquivo | Produto | Link | Data do download |
|---|---|---|---|
| `arroz/Arroz_Irrigado_Serie_Historica_2002-2026.xls` | Arroz (irrigado) | página da CONAB acima (TODO: link exato) | 13/11/2026 |
| `arroz/Arroz_Sequeiro_Serie_Historica_2001-2026.xls` | Arroz (sequeiro) | página da CONAB acima (TODO: link exato) | 13/11/2026 |
| `feijao/Feijao_1_Safra_Serie_Historica-1998-2026.xls` | Feijão (1ª safra) | página da CONAB acima (TODO: link exato) | 13/11/2026 |
| `feijao/Feijao_2_e_3_Safras_Serie_Historica_2013-2026.xls` | Feijão (2ª e 3ª safras) | página da CONAB acima (TODO: link exato) | 13/11/2026 |

**Pendências:**
- Faltam Café e Leite.
- Arroz e feijão têm duas planilhas cada (irrigado/sequeiro; 1ª safra / 2ª e 3ª safras). Decidir no notebook `03_conab.ipynb` qual usar (ou como combinar) e registrar em `docs/decisoes.md`.
- Os arquivos são `.xls` (formato antigo do Excel); o pandas lê com o pacote `xlrd`, que já está no `requirements.txt`.
