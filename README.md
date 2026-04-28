# 🤖 MonitorIA - Assistente de Dúvidas Acadêmicas

O **MonitorIA** é uma plataforma de Q&A (Perguntas e Respostas) estilo *Stack Overflow*, focada em disciplinas universitárias. O sistema utiliza Inteligência Artificial para fornecer um "primeiro atendimento" imediato, ajudando a organizar o fluxo de dúvidas e evitar perguntas duplicadas.

---

## 🛠️ Tecnologias e Ferramentas

### Backend (O Cérebro)
* **Python + Flask:** Micro-framework para construção da API REST.
* **Flask-SQLAlchemy:** Utilizado como **ORM (Object Relational Mapper)**. 
  * *Vantagem:* Permite gerenciar o banco de dados PostgreSQL usando classes Python em vez de SQL puro, garantindo um código mais limpo, seguro e fácil de manter.
* **PostgreSQL:** Banco de dados robusto para armazenamento de usuários, perguntas e respostas.
* **Groq API (Llama 3):** Processamento de linguagem natural para geração de respostas e detecção de similaridade.

### Frontend (A Interface)
* **Vanilla JS / React:** Interface dinâmica e responsiva.
* **Marked.js:** Para renderizar textos em Markdown.
* **Highlight.js:** Para colorir blocos de código automaticamente.

---

## 🚀 Estrutura de Arquitetura (Clean Code)

O projeto segue uma arquitetura em camadas para separar responsabilidades:

* `models/`: Definição das tabelas do banco de dados como objetos Python.
* `repositories/`: Camada exclusiva para interação com o banco de dados (Queries).
* `services/`: Onde reside a lógica de negócio e a integração com a IA do Groq.
* `routes/`: Definição dos endpoints da API que o frontend consome.

---

## 🧠 Desafios de IA (Groq)

### IA-001: Detecção de Duplicatas (Semântica)
Enquanto o aluno digita o título, o sistema verifica se já existem dúvidas parecidas no banco de dados. Utilizamos **Embeddings** para garantir que o sistema entenda o contexto da pergunta, e não apenas palavras isoladas.

### IA-002: Monitor Virtual
Assim que uma pergunta é enviada, a IA gera uma sugestão de resposta instantânea. 
* **Nota:** Essas respostas são visualmente identificadas como "Sugestão da MonitorIA" para que o aluno saiba que o conteúdo ainda não foi revisado por um humano.

---

## 📋 Plano de Ação

- [ ] **Fase 1:** Setup do Flask, SQLAlchemy e modelagem das tabelas.
- [ ] **Fase 2:** Criação das rotas (CRUD) de perguntas e respostas.
- [ ] **Fase 3:** Desenvolvimento da interface web e consumo da API.
- [ ] **Fase 4:** Integração com Groq para o "Monitor Virtual".
- [ ] **Fase 5:** Implementação da busca semântica de duplicatas.

---

## 🔧 Como Iniciar o Projeto

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/Sp4rkjpedro/MonitorIA.git](https://github.com/Sp4rkjpedro/MonitorIA.git)
