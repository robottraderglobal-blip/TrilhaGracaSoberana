'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import styles from './minha-devocional.module.css';

/* ── Tipos ───────────────────────────────────────────────── */
type Etapa = 'input' | 'passagem' | 'analise' | 'devocional';

interface PassagemSugerida {
  passagemId: string;
  ref: string;
  texto: string;
  justificativa: string;
}

interface PassagensResponse {
  passagens: PassagemSugerida[];
}

interface AnaliseGerada {
  analiseId: string;
  conteudoMd: string;
  palavras: number;
  passos: Record<string, string>;
}

interface DevocionalGerada {
  devocionalId: string;
  titulo: string;
  conteudoMd: string;
  palavras: number;
}

interface HistoricoItem {
  id: string;
  input_usuario: string;
  passagem_ref: string;
  passagem_texto: string;
  created_at: string;
  usuario_analises: Array<{ id: string; conteudo_md: string }>;
  usuario_devocionais: Array<{ id: string; titulo: string; conteudo_md: string; palavras: number }>;
}

/* ── Session key (anônima, persistida no sessionStorage) ── */
function getOrCreateSessionKey(): string {
  const stored = sessionStorage.getItem('minha_devocional_session');
  if (stored) return stored;
  const newKey = `anon_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
  sessionStorage.setItem('minha_devocional_session', newKey);
  return newKey;
}

/* ── Step Indicator ─────────────────────────────────────── */
function StepIndicator({ etapa }: { etapa: Etapa }) {
  const steps: Array<{ id: Etapa; label: string }> = [
    { id: 'passagem',   label: 'Passagem' },
    { id: 'analise',    label: 'Análise' },
    { id: 'devocional', label: 'Devocional' },
  ];
  const order: Etapa[] = ['input', 'passagem', 'analise', 'devocional'];
  const currentIdx = order.indexOf(etapa);

  return (
    <div className={styles.stepIndicator}>
      {steps.map((step, i) => {
        const stepIdx = order.indexOf(step.id);
        const isDone = currentIdx > stepIdx;
        const isActive = etapa === step.id || (etapa === 'input' && i === 0);
        return (
          <div key={step.id} style={{ display: 'flex', alignItems: 'center' }}>
            <div className={styles.stepDot}>
              <div className={`${styles.stepCircle} ${isDone ? styles.done : ''} ${isActive ? styles.active : ''}`}>
                {isDone ? '✓' : i + 1}
              </div>
              <span className={`${styles.stepLabel} ${isActive ? styles.active : ''}`}>{step.label}</span>
            </div>
            {i < steps.length - 1 && (
              <div className={`${styles.stepLine} ${isDone ? styles.done : ''}`} />
            )}
          </div>
        );
      })}
    </div>
  );
}

/* ── Componente principal ───────────────────────────────── */
export default function MinhaDevocionalClient() {
  const [etapa, setEtapa] = useState<Etapa>('input');
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState('');
  const [erro, setErro] = useState('');
  const [showToast, setShowToast] = useState(false);

  const [passagem, setPassagem] = useState<PassagemSugerida | null>(null);
  const [passagens, setPassagens] = useState<PassagemSugerida[]>([]);
  const [analise, setAnalise] = useState<AnaliseGerada | null>(null);
  const [devocional, setDevocional] = useState<DevocionalGerada | null>(null);
  const [historico, setHistorico] = useState<HistoricoItem[]>([]);

  const sessionKey = useRef('');
  useEffect(() => { sessionKey.current = getOrCreateSessionKey(); }, []);

  /* Carrega histórico da sessão */
  const carregarHistorico = useCallback(async () => {
    if (!sessionKey.current) return;
    const res = await fetch(`/api/minha-devocional/historico?sessionKey=${sessionKey.current}`);
    if (res.ok) {
      const data = await res.json();
      setHistorico(data.historico || []);
    }
  }, []);

  useEffect(() => { carregarHistorico(); }, [carregarHistorico]);

  /* ── Etapa 1: Sugerir passagem ── */
  const sugerirPassagem = async () => {
    if (!input.trim()) return;
    setErro('');
    setLoading(true);
    setLoadingMsg('Buscando passagens para o seu tema…');
    try {
      const res = await fetch('/api/minha-devocional/sugerir-passagem', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input, sessionKey: sessionKey.current }),
      });
      const data: PassagensResponse = await res.json();
      if (!res.ok) throw new Error((data as any).error || 'Erro ao sugerir passagem');
      setPassagens(data.passagens || []);
      setPassagem(null); // limpa seleção anterior
      setEtapa('passagem');
    } catch (e) {
      setErro((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  /* ── Confirmar + iniciar análise (tudo num passo só) ── */
  const analisarPassagem = async (p: PassagemSugerida) => {
    setPassagem(p);
    setErro('');
    setLoading(true);
    setLoadingMsg('Confirmando passagem e preparando análise…');
    try {
      // 1. Confirma no banco
      await fetch('/api/minha-devocional/confirmar-passagem', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ passagemId: p.passagemId }),
      });

      // 2. Muda etapa imediatamente
      setEtapa('analise');

      // 3. Inicia a análise automática
      setLoadingMsg('Gerando análise exegética… isso pode levar um minuto.');
      const res = await fetch('/api/minha-devocional/gerar-analise', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ passagemId: p.passagemId }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Erro ao gerar análise');
      setAnalise(data);
    } catch (e) {
      setErro((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  /* ── Regenerar análise (já com passagem confirmada) ── */
  const gerarAnalise = async () => {
    if (!passagem) return;
    setErro('');
    setLoading(true);
    setLoadingMsg('Regenerándo análise exegética…');
    try {
      const res = await fetch('/api/minha-devocional/gerar-analise', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ passagemId: passagem.passagemId }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Erro ao gerar análise');
      setAnalise(data);
    } catch (e) {
      setErro((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  /* ── Etapa 3: Gerar devocional ── */
  const gerarDevocional = async () => {
    if (!passagem || !analise) return;
    setErro('');
    setLoading(true);
    setLoadingMsg('Escrevendo a devocional no estilo J.C. Ryle… aguarde.');
    try {
      const res = await fetch('/api/minha-devocional/gerar-devocional', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ passagemId: passagem.passagemId, analiseId: analise.analiseId }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Erro ao gerar devocional');
      setDevocional(data);
      setEtapa('devocional');
      carregarHistorico();
    } catch (e) {
      setErro((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  /* ── Copiar devocional ── */
  const copiarDevocional = async () => {
    if (!devocional) return;
    await navigator.clipboard.writeText(devocional.conteudoMd);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 2500);
  };

  /* ── Reiniciar tudo ── */
  const novaDevocional = () => {
    setEtapa('input');
    setInput('');
    setPassagem(null);
    setPassagens([]);
    setAnalise(null);
    setDevocional(null);
    setErro('');
  };

  /* ── Carregar item do histórico ── */
  const carregarDoHistorico = (item: HistoricoItem) => {
    setPassagem({
      passagemId: item.id,
      ref: item.passagem_ref,
      texto: item.passagem_texto,
      justificativa: '',
    });
    if (item.usuario_analises?.length > 0) {
      const a = item.usuario_analises[0];
      setAnalise({ analiseId: a.id, conteudoMd: a.conteudo_md, palavras: 0, passos: {} });
    }
    if (item.usuario_devocionais?.length > 0) {
      const d = item.usuario_devocionais[0];
      setDevocional({ devocionalId: d.id, titulo: d.titulo, conteudoMd: d.conteudo_md, palavras: d.palavras });
      setEtapa('devocional');
    } else if (item.usuario_analises?.length > 0) {
      setEtapa('analise');
    } else {
      setEtapa('passagem');
    }
  };

  /* ── Render ── */
  return (
    <div className={styles.pageWrapper}>
      {/* Header */}
      <div className={styles.pageHeader}>
        <h1 className={styles.pageTitle}>✍️ Minha Devocional</h1>
        <p className={styles.pageSubtitle}>
          Diga um tema, situação ou versículo que queira meditar.
          A IA sugerirá uma passagem e gerará uma análise e devocional no estilo J.C. Ryle.
        </p>
      </div>

      {/* Step Indicator */}
      <StepIndicator etapa={etapa} />

      {/* Erro global */}
      {erro && (
        <div style={{ background: 'rgba(239,68,68,0.12)', border: '1px solid rgba(239,68,68,0.3)',
          borderRadius: '0.6rem', padding: '0.85rem 1rem', marginBottom: '1.25rem',
          color: '#f87171', fontFamily: 'var(--font-outfit)', fontSize: '0.875rem' }}>
          ⚠️ {erro}
        </div>
      )}

      {/* ── ETAPA 1 & 2: Input + Passagem sugerida ── */}
      {(etapa === 'input' || etapa === 'passagem') && (
        <>
          <div className={styles.card}>
            <label htmlFor="temaInput" className={styles.inputLabel}>
              Tema, situação ou versículo
            </label>
            <textarea
              id="temaInput"
              className={styles.textarea}
              placeholder="Ex: &quot;Estou com medo do futuro&quot; ou &quot;Quero meditar sobre a graça de Deus&quot; ou &quot;Romanos 8&quot;"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter' && e.ctrlKey) sugerirPassagem(); }}
              rows={4}
            />
            <div className={styles.btnRow}>
              <button
                className={`${styles.btn} ${styles.btnPrimary}`}
                onClick={sugerirPassagem}
                disabled={loading || !input.trim()}
              >
                🔍 {etapa === 'passagem' ? 'Buscar Outra Passagem' : 'Encontrar Passagem'}
              </button>
              {etapa === 'passagem' && (
                <button
                  className={`${styles.btn} ${styles.btnSecondary}`}
                  onClick={novaDevocional}
                >
                  ↩ Recomeçar
                </button>
              )}
            </div>
          </div>

          {/* Passagens sugeridas — cada card tem botão próprio */}
          {passagens.length > 0 && !loading && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '0.5rem' }}>
              {passagens.length > 1 && (
                <p style={{ fontFamily: 'var(--font-outfit)', fontSize: '0.82rem',
                  color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                  Encontrei {passagens.length} passagens relacionadas. Escolha uma:
                </p>
              )}
              {passagens.map((p) => (
                <div
                  key={p.passagemId}
                  className={styles.passagemCard}
                >
                  <div className={styles.passagemRef}>{p.ref}</div>
                  <div className={styles.passagemTexto}>{p.texto}</div>
                  <div className={styles.btnRow} style={{ marginTop: '1rem' }}>
                    <button
                      className={`${styles.btn} ${styles.btnSuccess}`}
                      onClick={() => analisarPassagem(p)}
                      disabled={loading}
                    >
                      📖 Analisar esta Passagem
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ── ETAPA 3: Análise ── */}
      {etapa === 'analise' && passagem && (
        <>
          {/* Sticky com referência + botão voltar */}
          <div className={styles.stickyPassagem}>
            <button
              className={styles.stickyBackBtn}
              onClick={() => { setEtapa('passagem'); setAnalise(null); }}
              disabled={loading}
            >
              ← Trocar passagem
            </button>
            <span className={styles.stickyPassagemRef}>📖 {passagem.ref}</span>
          </div>

          {/* Texto completo da passagem sempre visível */}
          <blockquote className={styles.passagemBlockquote}>
            <span className={styles.passagemBlockquoteRef}>{passagem.ref}</span>
            {passagem.texto}
          </blockquote>

          {/* Gerar análise */}
          {!analise && !loading && (
            <div className={styles.card}>
              <h2 className={styles.sectionTitle}>Análise Exegética</h2>
              <p style={{ fontFamily: 'var(--font-outfit)', fontSize: '0.9rem',
                color: 'var(--text-muted)', marginBottom: '1.25rem', lineHeight: 1.6 }}>
                Análise reformada pelo método histórico-gramatical — observação, contexto,
                gramática, interpretação, aplicação cristocêntrica e indicação de material extra.
              </p>
              <button
                className={`${styles.btn} ${styles.btnPrimary}`}
                onClick={gerarAnalise}
              >
                📖 Gerar Análise Exegética
              </button>
            </div>
          )}

          {/* Resultado da análise — markdown direto */}
          {analise && (
            <div className={styles.card}>
              <h2 className={styles.sectionTitle}>Análise Exegética — {passagem.ref}</h2>
              <div className={styles.analiseTexto}>
                <ReactMarkdown>{analise.conteudoMd}</ReactMarkdown>
              </div>
              <div className={styles.btnRow}>
                <button
                  className={`${styles.btn} ${styles.btnPrimary}`}
                  onClick={gerarDevocional}
                  disabled={loading}
                >
                  ✍️ Gerar Devocional no Estilo Ryle
                </button>
                <button
                  className={`${styles.btn} ${styles.btnSecondary}`}
                  onClick={gerarAnalise}
                  disabled={loading}
                >
                  🔄 Regenerar Análise
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {/* ── ETAPA 4: Devocional ── */}
      {etapa === 'devocional' && passagem && devocional && (
        <>
          {/* Sticky da passagem */}
          <div className={styles.stickyPassagem}>
            <span className={styles.stickyPassagemRef}>📖 {passagem.ref}</span>
            <span className={styles.stickyPassagemTexto}>{passagem.texto}</span>
          </div>

          <div className={styles.devocionalCard}>
            <div className={styles.devocionalHeader}>
              <h2 className={styles.devocionalTitulo}>{devocional.titulo}</h2>
              <div className={styles.devocionalPassagemRef}>{passagem.ref} (ARA)</div>
            </div>

            {/* Versículo completo */}
            <blockquote style={{
              borderLeft: '3px solid var(--accent-gold, #c9a84c)',
              paddingLeft: '1.2rem',
              margin: '0 0 2rem 0',
              fontFamily: 'var(--font-playfair)',
              fontStyle: 'italic',
              fontSize: '1rem',
              color: 'var(--text-secondary)',
              lineHeight: 1.75,
            }}>
              {passagem.texto}
            </blockquote>

            <div className={styles.devocionalTexto}>
              <ReactMarkdown>{devocional.conteudoMd}</ReactMarkdown>
            </div>

            <div className={styles.wordCount}>
              {devocional.palavras} palavras
            </div>
          </div>

          {/* Botões de ação */}
          <div className={styles.btnRow}>
            <button className={`${styles.btn} ${styles.btnPrimary}`} onClick={copiarDevocional}>
              📋 Copiar Devocional
            </button>
            <button
              className={`${styles.btn} ${styles.btnSecondary}`}
              onClick={async () => {
                setEtapa('analise');
                setDevocional(null);
                await gerarDevocional();
              }}
              disabled={loading}
            >
              🔄 Regenerar Devocional
            </button>
            {analise && (
              <button
                className={`${styles.btn} ${styles.btnSecondary}`}
                onClick={() => { setEtapa('analise'); setDevocional(null); }}
              >
                📖 Ver Análise
              </button>
            )}
            <button
              className={`${styles.btn} ${styles.btnDanger}`}
              onClick={novaDevocional}
            >
              ➕ Nova Devocional
            </button>
          </div>
        </>
      )}

      {/* Loading state global */}
      {loading && (
        <div className={styles.loadingWrap}>
          <div className={styles.spinner} />
          <span>{loadingMsg}</span>
        </div>
      )}

      {/* Histórico da sessão */}
      {historico.length > 0 && etapa === 'input' && (
        <div className={styles.historicoSection}>
          <h3 className={styles.historicoTitle}>📚 Devocionais desta sessão</h3>
          {historico.map((item) => (
            <div
              key={item.id}
              className={styles.historicoItem}
              onClick={() => carregarDoHistorico(item)}
            >
              <div>
                <div className={styles.historicoRef}>{item.passagem_ref}</div>
                <div className={styles.historicoInput}>{item.input_usuario}</div>
              </div>
              <div className={styles.historicoDate}>
                {new Date(item.created_at).toLocaleTimeString('pt-BR', {
                  hour: '2-digit', minute: '2-digit',
                })}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Toast */}
      {showToast && (
        <div className={styles.toast}>✅ Devocional copiada!</div>
      )}
    </div>
  );
}
