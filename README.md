# IntegraMente Backend API

## 📖 Sobre o Projeto

O **IntegraMente Backend** é uma API REST desenvolvida para o aplicativo educacional IntegraMente, focado no ensino de **Cálculo Integral**. Este backend fornece funcionalidades matemáticas avançadas para cálculos simbólicos, numéricos e visualização gráfica de funções matemáticas.

### 🎯 Objetivo Educacional
Apoiar o aprendizado de Cálculo II fornecendo:
- Cálculos precisos de integrais definidas e indefinidas
- Visualização gráfica de funções e áreas sob curvas
- Validação de sintaxe matemática
- Passos detalhados de resolução

---

## 🏗️ Arquitetura do Sistema

### **Tecnologias Utilizadas**
- **FastAPI 0.115+** - Framework web moderno e rápido para Python
- **SymPy 1.14+** - Biblioteca para computação simbólica matemática
- **SciPy 1.15+** - Algoritmos científicos e integração numérica
- **NumPy 2.3+** - Computação numérica eficiente
- **Matplotlib 3.10+** - Geração de gráficos matemáticos
- **Pydantic 2.11+** - Validação e serialização de dados

### **Padrão de Arquitetura**
- **MVC (Model-View-Controller)** adaptado para APIs REST
- **Separação de responsabilidades** em camadas bem definidas
- **Injeção de dependências** via FastAPI
- **Validação automática** de dados de entrada

```
Backend Structure:
├── main.py                 # Configuração principal da API
├── app/
│   ├── core/
│   │   └── config.py      # Configurações centralizadas
│   ├── models/
│   │   ├── requests.py    # Modelos de entrada (DTOs)
│   │   └── responses.py   # Modelos de saída (DTOs)
│   ├── routers/
│   │   ├── area.py        # Endpoint para cálculo de área
│   │   ├── simbolico.py   # Endpoint para integração simbólica
│   │   ├── validar.py     # Endpoint para validação de funções
│   │   ├── exemplos.py    # Endpoint para exemplos educacionais
│   │   └── health.py      # Endpoint para monitoramento
│   └── services/
│       ├── math_service.py    # Lógica matemática principal
│       └── exemplos_service.py # Gerenciamento de exemplos
```

---

## ⚙️ Funcionalidades Técnicas

### **1. Cálculo de Área Sob a Curva (Integração Numérica)**
- **Algoritmo**: Quadratura adaptativa (SciPy)
- **Precisão**: ~10⁻¹⁴ de erro relativo
- **Entrada**: Função matemática + intervalo [a,b]
- **Saída**: Valor numérico + estimativa de erro + gráfico base64

### **2. Integração Simbólica**
- **Engine**: SymPy Computer Algebra System
- **Capacidades**: Antiderivadas analíticas + integrais definidas
- **Formato**: Expressões matemáticas + LaTeX para renderização
- **Educacional**: Passos detalhados de resolução

### **3. Validação Matemática**
- **Parser**: SymPy expression parser
- **Suporte**: Funções elementares, trigonométricas, exponenciais, logarítmicas
- **Sintaxe**: Notação matemática padrão (x^2, sin(x), ln(x), etc.)

### **4. Geração de Gráficos**
- **Biblioteca**: Matplotlib com backend não-interativo
- **Formato**: PNG em base64 para transmissão web
- **Configuração**: Resolução adaptável (50-1000 pontos)
- **Visualização**: Função + área sombreada + grid + labels

---

## 🌐 API Endpoints

### **Base URL**: `https://sua-url.com/`

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|---------|
| GET | `/` | Informações da API | ✅ |
| GET | `/health` | Status do servidor | ✅ |
| POST | `/area` | Cálculo de área (integração numérica) | ✅ |
| POST | `/simbolico` | Integração simbólica | ✅ |
| POST | `/validar` | Validação de funções | ✅ |
| GET | `/exemplos` | Exemplos educacionais organizados | ✅ |
| POST | `/grafico` | Geração isolada de gráficos | ✅ |

### **Documentação Interativa**
- **Swagger UI**: `https://sua-url.com/docs`
- **ReDoc**: `https://sua-url.com/redoc`

---

## 📊 Exemplos de Uso

### **Cálculo de Área**
```bash
POST /area
Content-Type: application/json

{
  "funcao": "x^2",
  "a": -2,
  "b": 2,
  "resolucao": 400
}

# Resposta:
{
  "sucesso": true,
  "valor_integral": 5.333333333333333,
  "area_total": 5.333333333333333,
  "erro_estimado": 5.921189464667501e-14,
  "grafico_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "pontos_grafico": [{"x": -2.0, "y": 4.0}, ...],
  "funcao_formatada": "x**2",
  "intervalo": {"a": -2.0, "b": 2.0},
  "calculado_em": "2024-06-25T14:27:02.169184"
}
```

### **Integração Simbólica**
```bash
POST /simbolico
Content-Type: application/json

{
  "funcao": "x^2",
  "mostrar_passos": true,
  "formato_latex": true
}

# Resposta:
{
  "sucesso": true,
  "antiderivada": "x**3/3",
  "antiderivada_latex": "\\frac{x^3}{3}",
  "passos_resolucao": [
    "Função original: x^2",
    "Aplicando integração: ∫(x^2)dx",
    "Antiderivada: x**3/3",
    "Resultado: x**3/3 + C"
  ],
  "funcao_original": "x^2",
  "calculado_em": "2024-06-25T14:27:02.169184"
}
```

---

## 🚀 Deploy e Hospedagem

### **Plataformas Suportadas**
- **Render** (Recomendado) - Deploy automático via GitHub
- **Railway** - Detecção automática de FastAPI
- **Fly.io** - Deploy via CLI
- **PythonAnywhere** - Hospedagem tradicional

### **Configuração de Produção**
- **CORS** habilitado para domínios específicos
- **Logs** estruturados para monitoramento
- **Health checks** para alta disponibilidade
- **Variáveis de ambiente** para configurações sensíveis

---

## 🧪 Testes e Qualidade

### **Scripts de Teste**
```bash
# Testar todas as funcionalidades
python test_api.py

# Verificar prontidão para deploy
python test_deploy.py

# Iniciar servidor de desenvolvimento
python start_server.py
```

### **Cobertura de Testes**
- ✅ Validação de entrada
- ✅ Cálculos matemáticos
- ✅ Geração de gráficos
- ✅ Tratamento de erros
- ✅ Performance de endpoints

---

## 📈 Performance e Limitações

### **Capacidades**
- **Concorrência**: Suporte a múltiplas requisições simultâneas
- **Precisão**: Erro numérico < 10⁻¹⁴ para funções bem comportadas
- **Resolução**: Até 1000 pontos para gráficos
- **Timeout**: 30 segundos por cálculo (configurável)

### **Limitações Conhecidas**
- Funções com descontinuidades podem gerar erros
- Integrais impróprias requerem tratamento especial
- Gráficos limitados a funções de uma variável

---

## 🔧 Desenvolvimento e Manutenção

### **Instalação Local**
```bash
# 1. Clonar repositório
git clone <repo-url>
cd integramente_back

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Executar testes
python test_deploy.py

# 4. Iniciar servidor
python main.py
```

### **Estrutura de Dados**
- **Entrada**: JSON com validação Pydantic
- **Processamento**: SymPy + SciPy + NumPy
- **Saída**: JSON padronizado com campos obrigatórios

---

## 👥 Integração com Flutter

### **Comunicação**
- **Protocolo**: HTTP/HTTPS REST
- **Formato**: JSON
- **Autenticação**: Não requerida (API educacional)
- **CORS**: Configurado para desenvolvimento cross-origin

### **Campos de Resposta Padronizados**
Todas as respostas incluem:
- `sucesso: boolean` - Status da operação
- `erro: string | null` - Mensagem de erro (se houver)
- `calculado_em: string` - Timestamp ISO 8601

---

## 📋 Conclusão Técnica

O **IntegraMente Backend** representa uma solução robusta e escalável para computação matemática educacional, combinando:

- **Precisão matemática** via bibliotecas científicas consolidadas
- **Performance web** através do FastAPI assíncrono
- **Facilidade de uso** com documentação automática
- **Manutenibilidade** via arquitetura em camadas
- **Extensibilidade** para futuras funcionalidades matemáticas

A arquitetura modular permite fácil adição de novos tipos de cálculos, mantendo a estabilidade e performance do sistema existente.

---

**Desenvolvido para o projeto IntegraMente - Cálculo Integral Educacional** 📚🧮 