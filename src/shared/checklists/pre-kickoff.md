# Pre-Kickoff Checklist — Data Migration Factory

> Executar **antes** de iniciar qualquer wave de migração. Responsável: PM + Tech Lead.
> Baseado no delivery-lead-checklist do .avanade-core e nas práticas do método Avanade.

---

## 1. Contexto do Projeto
- [ ] `projects/{nome}/context/project-config.yaml` preenchido e validado
- [ ] `projects/{nome}/context/agent-task-config.yaml` criado com `trace_id` gerado
- [ ] Plataformas de origem e destino confirmadas com o cliente
- [ ] Tech lead e PM designados
- [ ] Repositório legado com acesso de leitura configurado

## 2. Escopo e Contratos
- [ ] Escopo da wave delimitado (lista de objetos a migrar)
- [ ] SLAs de qualidade acordados com o cliente (paridade mínima, latência)
- [ ] Contrato de confidencialidade / LGPD revisado para dados PII
- [ ] Ambientes target provisionados (DEV/HML/PRD)

## 3. Ferramentas e Acessos
- [ ] Acesso ao repositório legado (leitura) configurado
- [ ] Credenciais do ambiente target armazenadas em Key Vault / secret store
- [ ] Python ≥ 3.11 + `pytest pyyaml` instalados (`.venv` ativo)
- [ ] VS Code + extensão GitHub Copilot instalada e ativa
- [ ] Scripts de governança validados: `python -m pytest tests/ -q` (todos verde)

## 4. Agentes e Skills
- [ ] `master-agent` testado: `*route` responde corretamente
- [ ] `migration-coordinator` testado: `*project-status` responde
- [ ] Módulos src/modules/ corretos para o escopo da wave identificados
- [ ] `agent-task-config.yaml` com `agent_sequence` correto para a wave

## 5. Governança
- [ ] `wave-config-sample.yaml` preenchido e validado por `validate_wave_config.py`
- [ ] Gate thresholds revisados: Gate 1 ≥ 70, Gate 2 ≥ 85, Gate 3 paridade ≥ 99.9%
- [ ] Aprovadores de gate definidos (mínimo 2 por gate)
- [ ] Canal de comunicação de escalação definido (Teams / email)

## 6. Kickoff Meeting
- [ ] Stakeholders informados sobre duração estimada
- [ ] Workflow de cada módulo revisado com o time técnico
- [ ] Riscos críticos do `problem-statement.md` comunicados
- [ ] Go/No-Go formal registrado antes de iniciar

---

**Assinatura do Go/No-Go:**  
PM: _________________ | Tech Lead: _________________ | Data: _________
