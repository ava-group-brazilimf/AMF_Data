# Mixed Pipeline Coupling Patterns
# Padrões de detecção de acoplamento por filesystem em legados de código misto
# Carregado por: discovery-scout (map-dependencies) e logic-extractor
#                quando platform = Generic Spark / Mixed Code

---

## 1. Flag files (sincronização por sentinela)

**Detectar no produtor:** `open(path,"w")` (Python), `PrintWriter` (Scala),
`echo >` (shell) em paths contendo flag|ok|done|ready|.lock|.sentinel
**Detectar no consumidor:** `os.path.exists`, `File(...).exists`, `IF EXIST`,
loops de polling com sleep
**Aresta:** `produtor -> consumidor (FLAG_FILE, path)`
**Databricks:** dependência declarativa de task - o arquivo desaparece.

## 2. Artefatos de dados intermediários

**Detectar:** write path em A (to_csv, PrintWriter, df.write, BCP out) ==
read path em B (open, spark.read, BULK INSERT, OPENROWSET, pd.read_csv)
**Normalização de path (obrigatória antes de comparar):**
case-insensitive (Windows), `\` ≡ `/`, resolver variáveis simples
($PMBadFileDir, %VAR%, ${VAR}), wildcard match (atend_*.csv casa atend_202403.csv)
**Aresta:** `A -> B (DATA_FILE, path, formato)`
**Databricks:** DataFrame passado entre células ou tabela Delta - sem arquivo solto.

## 3. Loads reversos (fecha ciclo cross-tech)

**Detectar:** BULK INSERT/LOAD/COPY em SQL cujo path é write target de
Python/Scala do mesmo inventário. SEMPRE testar - é o acoplamento mais
invisível em análise manual.
**Aresta:** `job -> procedure (DATA_FILE_REVERSE, path)`

## 4. Sincronização temporal implícita

**Detectar:** Thread.sleep / time.sleep fixos entre etapas, agendamentos
sequenciais por horário (job A às 22h, job B às 23h "porque A já terminou").
**Aresta:** `A -> B (TEMPORAL_ASSUMPTION)` + flag FRAGILE
**Databricks:** trigger por conclusão real da task upstream.

## 5. Dependências externas ao repositório

**Detectar:** linked servers (4-part names, especialmente `[IP].db.schema.tab`),
connection strings para hosts que não são objetos do repo, URLs HTTP.
**Aresta:** `EXTERNAL(host) -> objeto (LINKED_SERVER | EXTERNAL_DB | HTTP)`
**Databricks:** Lakehouse Federation, ingestão CDC ou conector gerenciado.

## 6. Sinais de fragilidade a registrar por objeto (alimenta classify)

| Sinal | Onde procurar |
|---|---|
| Credencial hardcoded | connection strings em .py/.scala/.sql - registrar SOMENTE presença e local, NUNCA copiar o valor para o inventário |
| except:pass / catch vazio | blocos de exceção sem ação |
| Exit code 0 em falha | ausência de sys.exit(1)/System.exit(1) após erro |
| NOLOCK em produção | hints WITH (NOLOCK) |
| TRUNCATE fora de transação | TRUNCATE sem BEGIN TRAN no mesmo corpo |
| collect() em driver | .collect() sobre dataset não-limitado |
| Encoding não-UTF8 | encoding="latin-1"/cp1252 explícitos |
| Paths de SO hardcoded | C:\, D:\, /home/ literais |
