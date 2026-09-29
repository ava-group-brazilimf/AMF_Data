---
name: avanade-brand-guidelines
description: Aplica as diretrizes oficiais de marca da Avanade (cores, tipografia e estilo visual) a artefatos digitais e documentos, garantindo consistência visual, aderência a padrões corporativos e alinhamento com a identidade global da Avanade.
---

Use esta skill sempre que **brand, identidade visual, layout ou padrões de design corporativo** forem relevantes.

## License
Uso interno Avanade. Consulte as políticas internas de Brand & Marketing para termos completos.

## Avanade Brand Styling Overview
Esta skill automatiza a aplicação da identidade visual Avanade em artefatos como:
- Apresentações (PPT/PPTX)
- Documentos (Markdown, Word, PDF)
- Diagramas e relatórios técnicos
- Outputs gerados por agentes (decks, specs, proposals)

## Keywords
branding, corporate identity, visual identity, avanade brand, design system, typography, brand colors, visual formatting, post-processing

---

## Brand Guidelines

### Colors

#### Primary Colors
- **Avanade Orange**: `#FF5800` — Cor principal de destaque e identidade
- **Dark Gray**: `#1F1F1F` — Texto principal e fundos escuros
- **White**: `#FFFFFF` — Fundos claros e contraste

#### Secondary / Neutral Colors
- **Mid Gray**: `#6E6E6E` — Elementos secundários
- **Light Gray**: `#E6E6E6` — Fundos sutis e separadores

> Regras:
> - Orange apenas para destaques, títulos-chave e elementos de ênfase  
> - Nunca usar Orange para grandes blocos de texto  

---

### Typography

#### Headings
- **Primary**: Segoe UI Semibold  
- **Fallback**: Arial

#### Body Text
- **Primary**: Segoe UI  
- **Fallback**: Arial

> Regras:
> - Títulos ≥ 24pt  
> - Corpo entre 11–14pt  
> - Hierarquia visual sempre preservada  

---

## Features

### Smart Font Application
- Aplica Segoe UI em títulos e corpo do texto
- Fallback automático para Arial quando necessário
- Mantém legibilidade em qualquer ambiente

### Text Styling
- Títulos com maior peso visual
- Corpo com espaçamento otimizado
- Contraste automático baseado no fundo

### Shapes & Accents
- Elementos não textuais usam **Avanade Orange** com moderação
- Tons de cinza para suporte visual
- Evita poluição visual e mantém padrão executivo

---

## Technical Details

### Font Management
- Utiliza fontes nativas do sistema (Segoe UI)
- Não requer instalação adicional
- Compatível com ambientes Windows corporativos

### Color Application
- Cores aplicadas via valores RGB/HEX
- Fidelidade mantida em PPTX, PDF e imagens
- Compatível com bibliotecas como `python-pptx`

---

## When to Use
- Geração automática de decks executivos
- Pós-processamento de outputs de agentes (Markdown → PPT)
- Padronização visual de propostas, EF, ET, relatórios
- Qualquer artefato voltado a cliente ou liderança

## When NOT to Use
- Rascunhos técnicos internos sem exposição
- Prototipação exploratória sem necessidade de branding

---

## Notes
- Esta skill **não altera conteúdo**, apenas **forma e estilo**
- Sempre prioriza clareza, sobriedade e padrão executivo Avanade