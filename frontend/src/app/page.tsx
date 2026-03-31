'use client';

import { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '@/lib/api';
import { ChatMessage, CarRecommendation, ConstraintReport } from '@/types';
import CarCard from '@/components/CarCard';
import TextType from '@/components/TextType';
import RippleGrid from '@/components/RippleGrid';
import ManualWeightInput from '@/components/ManualWeightInput';
import { useScientificMode } from '@/lib/ScientificModeContext';
import api from '@/lib/api';
import styles from './page.module.css';
import { HiPaperAirplane, HiArrowPath } from 'react-icons/hi2';
import { RiRobot2Fill } from 'react-icons/ri';
import { HiUser } from 'react-icons/hi2';

const WELCOME_CONTENT = 'Halo! 👋 Saya **Otobot** — asisten rekomendasi mobil cerdas Anda.\n\nCeritakan kebutuhan dan budget Anda — saya akan merekomendasikan **5 kandidat mobil terbaik** yang sudah diranking secara objektif! 🚗';

function createWelcomeMessage(): ChatMessage {
  return {
    id: 'welcome',
    role: 'assistant',
    content: WELCOME_CONTENT,
    timestamp: new Date(),
  };
}

function parseMarkdown(text: string): string {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br/>');
}



function MsgBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === 'user';
  return (
    <div className={`${styles.msgRow} ${isUser ? styles.msgRowUser : ''}`}>
      {!isUser && <div className={styles.avatarBot}><RiRobot2Fill size={14} /></div>}
      <div className={`${styles.bubble} ${isUser ? styles.bubbleUser : styles.bubbleBot}`}>
        <span dangerouslySetInnerHTML={{ __html: parseMarkdown(msg.content) }} />
        <span className={styles.timestamp}>
          {msg.timestamp.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
      {isUser && <div className={styles.avatarUser}><HiUser size={14} /></div>}
    </div>
  );
}

function RankedCars({ cars, constraintReport }: { cars: CarRecommendation[], constraintReport?: ConstraintReport }) {
  const { isScientific } = useScientificMode();
  const weights = constraintReport?.normalized_weights;
  const relaxNotes = constraintReport?.relax_notes;

  return (
    <div className={styles.carsSection}>
      <div className={styles.carsSectionHeader}>
        <span className={styles.carsSectionTitle}>🏆 Top {cars.length} Rekomendasi</span>
        {isScientific && <span className={styles.carsSectionBadge}>VIKOR Ranked</span>}
      </div>

      {/* Weight Vector Panel (Scientific Only) */}
      {isScientific && weights && Object.keys(weights).length > 0 && (
        <div style={{ marginBottom: '12px', padding: '12px 14px', borderRadius: '12px', background: 'rgba(30,111,217,0.07)', border: '1px solid rgba(30,111,217,0.2)', fontSize: '0.75rem' }}>
          <div style={{ fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#4090F7', marginBottom: '8px' }}>📊 Bobot Preferensi (Normalized)</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: '4px 12px' }}>
            {Object.entries(weights)
              .filter(([, v]) => v > 0.001)
              .sort(([, a], [, b]) => b - a)
              .map(([k, v]) => (
                <div key={k} style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)' }}>
                  <span>{k.replace('INDEX_', '').replace(/_/g, ' ')}</span>
                  <span style={{ fontWeight: 700, color: 'var(--text-secondary)' }}>{(v * 100).toFixed(1)}%</span>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Relaxation Log (Scientific Only) */}
      {isScientific && relaxNotes && relaxNotes.length > 0 && (
        <div style={{ marginBottom: '12px', padding: '10px 14px', borderRadius: '10px', background: 'rgba(245,158,11,0.07)', border: '1px solid rgba(245,158,11,0.25)', fontSize: '0.75rem' }}>
          <div style={{ fontWeight: 800, color: '#F59E0B', marginBottom: '5px', textTransform: 'uppercase', letterSpacing: '0.06em' }}>⚠️ Constraint Relaxation</div>
          {relaxNotes.map((note, i) => (
            <div key={i} style={{ color: 'var(--text-muted)', lineHeight: 1.8 }}>→ {note}</div>
          ))}
        </div>
      )}

      <div className={styles.carGrid}>
        {cars[0] && <CarCard car={cars[0]} rank={1} />}
        {cars.slice(1, 3).length > 0 && (
          <div className={styles.carRow}>
            {cars.slice(1, 3).map((car, i) => <CarCard key={i} car={car} rank={i + 2} />)}
          </div>
        )}
        {cars.slice(3, 5).length > 0 && (
          <div className={styles.carRow}>
            {cars.slice(3, 5).map((car, i) => <CarCard key={i} car={car} rank={i + 4} />)}
          </div>
        )}
      </div>
    </div>
  );
}



export default function ChatbotPage() {
  const { isScientific } = useScientificMode();
  const [messages, setMessages] = useState<ChatMessage[]>(() => [createWelcomeMessage()]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const submitWeights = async (weights: Record<string, number>, payload: Record<string, unknown>, msgId: string) => {
    const finalPayload = { ...payload, manual_weights: weights };
    setLoading(true);

    try {
      console.log("[FRONTEND] Mengirim bobot manual ke FastAPI", finalPayload);
      const { data } = await api.post('/chat', finalPayload);
      
      const recs = data.recommendations || [];
      const constraint_report = data.constraint_report || null;

      setMessages(prev => prev.map(m => m.id === msgId ? { ...m, ask_weights_payload: undefined } : m));

      setMessages(prev => [...prev, {
        id: `b-${Date.now()}`,
        role: 'assistant',
        content: `Sip! Berdasarkan bobot preferensi Anda, berikut hasilnya:`,
        recommendations: recs,
        constraint_report: constraint_report,
        timestamp: new Date(),
      }]);

      try { await fetch('http://localhost:8000/history'); } catch {}
    } catch (e) {
      setMessages(prev => [...prev, {
        id: `e-${Date.now()}`,
        role: 'assistant',
        content: '⚠️ Gagal memuat rekomendasi dengan bobot manual.',
        timestamp: new Date(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async (overrideText?: string) => {
    const text = (overrideText ?? input).trim();
    if (!text || loading) return;
    const userMsg: ChatMessage = {
      id: `u-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      console.log("==================================================");
      console.log(`[FRONTEND UI] User menekan tombol kirim dengan isi pesan: "${text}"`);
      // 1. Send text to Rasa via API
      const rasaResponses = await sendChatMessage(text);
      
      // Rasa returns an array of messages: [{ recipient_id: "user", text: "...", custom: {...} }]
      interface RasaMessage {
        recipient_id?: string;
        text?: string;
        custom?: {
          action?: string;
          payload?: Record<string, unknown>;
          recommendations?: CarRecommendation[];
          constraint_report?: ConstraintReport;
        };
      }
      
      if (Array.isArray(rasaResponses) && rasaResponses.length > 0) {
        // Gabungkan semua balasan teks jika ada banyak text
        const textParts = rasaResponses
          .map((r: RasaMessage) => r.text)
          .filter(Boolean)
          .join('\n\n');

        // Cari balasan custom action jika disediakan oleh actions.py
        const actionResponse = rasaResponses.find((r: RasaMessage) => r.custom && r.custom.action === "ask_weights");
        
        // Cari balasan custom recommendations jika disediakan oleh actions.py
        const recResponse = rasaResponses.find((r: RasaMessage) => r.custom && r.custom.recommendations);
        const recs = recResponse ? recResponse.custom.recommendations || [] : [];
        const constraint_report = recResponse ? recResponse.custom.constraint_report || null : null;

        if (actionResponse) {
          setMessages(prev => [...prev, {
            id: `b-${Date.now()}`,
            role: 'assistant',
            content: textParts || '...',
            ask_weights_payload: actionResponse.custom.payload,
            timestamp: new Date(),
          }]);
        } else {
          setMessages(prev => [...prev, {
            id: `b-${Date.now()}`,
            role: 'assistant',
            content: textParts || '...',
            recommendations: recs,
            constraint_report: constraint_report,
            timestamp: new Date(),
          }]);
        }
      } else {
        setMessages(prev => [...prev, {
          id: `b-${Date.now()}`,
          role: 'assistant',
          content: 'Maaf, saya tidak mengerti. Bisa diulangi?',
          timestamp: new Date(),
        }]);
      }
      
      // Refresh history
      try { await fetch('http://localhost:8000/history'); } catch {}

    } catch {
      setMessages(prev => [...prev, {
        id: `e-${Date.now()}`,
        role: 'assistant',
        content: '⚠️ Gagal menghubungi server NLP (Rasa). Pastikan backend di `localhost:5005` berjalan.',
        timestamp: new Date(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleResetSession = async () => {
    const WELCOME_FRESH = createWelcomeMessage();
    setMessages([WELCOME_FRESH]);
    setInput('');
    
    // Clear backend
    try {
      await sendChatMessage('/restart');
    } catch (e) {
      console.error('Failed to clear Rasa backend conversation state:', e);
    }
  };

  return (
    <div className={styles.pageLayout}>
      {/* ── Main Chat Area ── */}
      <main className={styles.chatMain} style={{ position: 'relative', overflow: 'hidden' }}>
        
        {/* ── Ripple Grid Animation (Only for Chat Background) ── */}
        <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 0, opacity: 10, pointerEvents: 'none' }}>
          <RippleGrid
            enableRainbow={true}
            gridColor="#000000ff" 
            rippleIntensity={0.01}
            gridSize={10}
            gridThickness={50}
            mouseInteraction={true}
            mouseInteractionRadius={0.2}
          />
        </div>

        {/* Chat Header */}
        <div className={styles.chatHeader} style={{ position: 'relative', zIndex: 1 }}>
          <div className={styles.chatHeaderLeft}>
            <div className={styles.botAvatar}><RiRobot2Fill size={18} /></div>
            <div>
              <div className={styles.chatHeaderTitle}>Otobot Assistant</div>
              <div className={styles.chatHeaderStatus}>
                <span className={styles.statusDot} />
                Online • Siap membantu
              </div>
            </div>
          </div>
          <div className={styles.chatHeaderRight}>
            <span className={styles.chatHeaderBadge}>Chatbot Rekomendasi Mobil</span>
            <button
              className={styles.resetBtn}
              onClick={handleResetSession}
              title="Reset Sesi"
              aria-label="Reset Sesi"
            >
              <HiArrowPath size={25} />
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className={styles.chatBody} style={{ position: 'relative', zIndex: 1 }}>
        {messages.map(msg => {
          const payload = msg.ask_weights_payload as any;
          return (
            <div key={msg.id}>
              <MsgBubble msg={msg} />
              
              {payload && isScientific && (
                <div style={{ marginBottom: '12px', background: 'var(--bg-secondary)', padding: '14px', borderRadius: '12px', border: '1px solid var(--border-color)', fontSize: '0.8rem' }}>
                  <div style={{ fontWeight: 800, marginBottom: '10px', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <RiRobot2Fill size={16} style={{ color: '#4090F7' }} /> Otobot menangkap:
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                        <span style={{ fontWeight: 700, width: '100px', color: 'var(--text-muted)' }}>Target Klaster:</span>
                        <span style={{ fontWeight: 800, color: '#8B5CF6' }}>{payload.cluster_name || "Global"}</span>
                    </div>
                    {payload.entities?.length > 0 && (
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                          <span style={{ fontWeight: 700, width: '100px', color: 'var(--text-muted)' }}>Filter Syarat:</span>
                          <span style={{ color: '#4090F7', fontWeight: 600 }}>{payload.entities.join(", ")}</span>
                      </div>
                    )}
                    {(payload.min_budget || payload.max_budget) && (
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                          <span style={{ fontWeight: 700, width: '100px', color: 'var(--text-muted)' }}>Batas Budget:</span>
                          <span style={{ color: '#00BB77', fontWeight: 700 }}>
                            {payload.min_budget ? `Rp ${(payload.min_budget/1000000).toLocaleString('id-ID')} Jt` : 'Rp 0'} 
                            {' - '} 
                            {payload.max_budget ? `Rp ${(payload.max_budget/1000000).toLocaleString('id-ID')} Jt` : 'Tak Terbatas'}
                          </span>
                      </div>
                    )}
                  </div>
                  <div style={{ marginTop: '14px', paddingTop: '10px', borderTop: '1px solid var(--border-color)', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                     Saya telah menyiapkan profil bobot rekomendasi awal berdasarkan klaster spesifik Anda. Silakan putuskan di bawah ini 👇
                  </div>
                </div>
              )}

              {/* Simplified summary for Awam mode */}
              {payload && !isScientific && (
                <div style={{ marginBottom: '12px', background: 'var(--bg-secondary)', padding: '12px 14px', borderRadius: '12px', border: '1px solid var(--border-color)', fontSize: '0.8rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-primary)' }}>
                    <RiRobot2Fill size={16} style={{ color: '#4090F7' }} />
                    <span style={{ fontWeight: 700 }}>
                      🔍 Mencari {payload.cluster_name ? `mobil ${payload.cluster_name}` : 'mobil'}
                      {payload.entities?.length > 0 && ` (${payload.entities.join(', ')})`}
                      {(payload.min_budget || payload.max_budget) && (
                        <> dengan budget {payload.min_budget ? `Rp ${(payload.min_budget/1000000).toLocaleString('id-ID')} Jt` : 'Rp 0'}{' - '}{payload.max_budget ? `Rp ${(payload.max_budget/1000000).toLocaleString('id-ID')} Jt` : 'Tak Terbatas'}</>
                      )}
                    </span>
                  </div>
                  <div style={{ marginTop: '8px', color: 'var(--text-muted)', fontSize: '0.75rem', fontStyle: 'italic' }}>
                    Atur prioritas Anda di bawah, lalu tekan tombol untuk mendapatkan rekomendasi 👇
                  </div>
                </div>
              )}

              {payload && (
                <ManualWeightInput 
                  initialWeights={payload.base_weight_profile || {}} 
                  onSubmit={(w) => submitWeights(w, payload, msg.id)}
                  disabled={loading}
                />
              )}

              {msg.recommendations && msg.recommendations.length > 0 && (
                <RankedCars cars={msg.recommendations} constraintReport={msg.constraint_report} />
              )}
            </div>
          );
        })}
          {loading && (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '180px', margin: '16px 0', opacity: 0.9 }}>
              <div style={{ padding: '16px 20px', borderRadius: '14px', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', display: 'inline-flex', alignItems: 'center', gap: '10px' }}>
                <RiRobot2Fill size={18} style={{ color: '#4090F7', animation: 'pulse 2s infinite' }} />
                <TextType 
                  text={[
                    "Otobot sedang menganalisis kebutuhan Anda...", 
                    "Sistem sedang menyaring kandidat mobil terbaik...", 
                    "Menghitung bobot ranking VIKOR...", 
                    "Sebentar lagi selesai..."
                  ]}
                  typingSpeed={30}
                  pauseDuration={2000}
                  showCursor
                  cursorCharacter="|"
                  deletingSpeed={30}
                  cursorBlinkDuration={0.5}
                  style={{
                    fontSize: '0.85rem',
                    color: 'var(--text-primary)',
                    fontWeight: 600,
                  }}
                />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className={styles.inputArea} style={{ position: 'relative', zIndex: 1 }}>
          <div className={styles.inputRow}>
            <input
              className={styles.input}
              type="text"
              placeholder="Ceritakan kebutuhan mobil Anda... (mis: SUV irit budget 500 juta)"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              disabled={loading}
            />
            <button
              className={styles.sendBtn}
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
              aria-label="Kirim"
            >
              {loading ? <span className={styles.spinner} /> : <HiPaperAirplane size={17} />}
            </button>
          </div>
          <p className={styles.inputHint}>
            Tekan <kbd>Enter</kbd> untuk mengirim • Bahasa Indonesia
          </p>
        </div>
      </main>
    </div>
  );
}
